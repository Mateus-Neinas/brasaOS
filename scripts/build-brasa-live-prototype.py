#!/usr/bin/env python3
"""Make a separate experimental live ISO from the existing Brasa image."""
from pathlib import Path
import io
import os
import hashlib
import shutil
import subprocess
import sqlite3
import sys
import tarfile
import tempfile
import urllib.request
import pycdlib

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'dist/Brasa-15.1-amd64.iso'
LIVE_PACKAGE_ROOTS = (
    'xorg-minimal', 'xinit', 'jwm', 'zenity', 'dejavu',
    'xf86-video-vesa', 'xf86-video-scfb',
)
VIRTIO_GPU_KMOD_URL = (
    'https://pkg.freebsd.org/FreeBSD:15:amd64/quarterly/All/'
    'virtio-gpu-qemu-kmod-0.2.1501000_1.pkg'
)
VIRTIO_GPU_KMOD_SHA256 = '97f42fe414e1a254142bdefe94d03538abe12874707eea36e9161beec4eed6bf'
VIRTIO_GPU_FILES = {
    '/boot/modules/virtio_gpu_qemu.ko': 'virtio_gpu_qemu.ko',
    '/usr/local/share/X11/xorg.conf.d/20-virtio-gpu-qemu.conf': 'virtio_gpu_qemu_xorg.conf',
}
PKG_REPO_DB_MEMBER = 'db/pkg/repos/FreeBSD-ports/db'
PKG_REPO_META_MEMBER = 'db/pkg/repos/FreeBSD-ports/meta'

def parse_args():
    output = ROOT / '.build/Brasa-live-experimental.iso'
    cache_iso = None
    virtio_gpu_qemu = False
    positional_seen = False
    args = iter(sys.argv[1:])
    for arg in args:
        if arg == '--help':
            print('Uso: build-brasa-live-prototype.py [caminho-da-iso-de-saida] '
                  '[--package-cache-iso ISO] [--virtio-gpu-qemu]')
            raise SystemExit(0)
        elif arg == '--virtio-gpu-qemu':
            virtio_gpu_qemu = True
            continue
        elif arg == '--package-cache-iso':
            try:
                cache_iso = Path(next(args)).resolve()
            except StopIteration:
                raise SystemExit('--package-cache-iso precisa de um caminho ISO.')
        elif arg.startswith('--'):
            raise SystemExit(f'Opção desconhecida: {arg}')
        elif not positional_seen:
            output = Path(arg).resolve()
            positional_seen = True
        else:
            raise SystemExit('Informe apenas um caminho de saída.')
    return output, cache_iso, virtio_gpu_qemu

OUTPUT, PACKAGE_CACHE_ISO, VIRTIO_GPU_QEMU = parse_args()


def download_virtio_gpu_files(destination):
    """Fetch the ABI-matched FreeBSD driver and extract only its two runtime files."""
    archive = destination / 'virtio-gpu-qemu-kmod.pkg'
    digest = hashlib.sha256()
    with urllib.request.urlopen(VIRTIO_GPU_KMOD_URL, timeout=60) as response, archive.open('wb') as output:
        while block := response.read(1024 * 1024):
            digest.update(block)
            output.write(block)
    if digest.hexdigest() != VIRTIO_GPU_KMOD_SHA256:
        raise RuntimeError('O pacote virtio-gpu-qemu-kmod não corresponde ao SHA-256 fixado.')

    tar = shutil.which('tar')
    if not tar:
        raise RuntimeError('O comando tar é necessário para extrair os arquivos do pacote FreeBSD.')
    extracted = {}
    for member, output_name in VIRTIO_GPU_FILES.items():
        output = destination / output_name
        with output.open('wb') as stream:
            result = subprocess.run(
                [tar, '-xOf', str(archive), member],
                stdout=stream, stderr=subprocess.PIPE, check=False,
            )
        if result.returncode or output.stat().st_size == 0:
            detail = result.stderr.decode(errors='replace').strip()
            raise RuntimeError(f'Falha ao extrair {member} do pacote FreeBSD: {detail}')
        extracted[member] = output
    return extracted

def read_rr(image, path):
    data = io.BytesIO()
    image.get_file_from_iso_fp(data, rr_path=path)
    return data.getvalue()

def prune_package_cache(source, destination, temporary_directory, catalog_fallback=None):
    """Keep cached packages needed by the live GUI dependency closure."""
    with tarfile.open(source, 'r:*') as archive:
        catalog_member = next((member for member in archive.getmembers()
                               if member.name.endswith('db/pkg/repos/FreeBSD-ports/db')), None)
        catalog_meta_member = next((member for member in archive.getmembers()
                                    if member.name.endswith('db/pkg/repos/FreeBSD-ports/meta')), None)
        catalog_path = temporary_directory / 'freebsd-ports.sqlite'
        catalog_meta_path = temporary_directory / 'freebsd-ports.meta'
        if catalog_member is not None and catalog_meta_member is not None:
            with catalog_path.open('wb') as catalog_file:
                shutil.copyfileobj(archive.extractfile(catalog_member), catalog_file)
            with catalog_meta_path.open('wb') as catalog_meta_file:
                shutil.copyfileobj(archive.extractfile(catalog_meta_member), catalog_meta_file)
        elif catalog_fallback and all(path.is_file() for path in catalog_fallback):
            shutil.copyfile(catalog_fallback[0], catalog_path)
            shutil.copyfile(catalog_fallback[1], catalog_meta_path)
        else:
            raise RuntimeError('O cache e a ISO de referência não contêm o catálogo FreeBSD-ports necessário.')

        database = sqlite3.connect(catalog_path)
        try:
            rows = database.execute(
                'SELECT id, name, version, path FROM packages'
            ).fetchall()
            by_name_version = {(row[1], row[2]): row for row in rows}
            by_name = {}
            for row in rows:
                by_name.setdefault(row[1], []).append(row)
            selected = set()
            pending = []
            for name in LIVE_PACKAGE_ROOTS:
                candidates = by_name.get(name, [])
                if candidates:
                    pending.append(candidates[0])
            if len(pending) != len(LIVE_PACKAGE_ROOTS):
                missing = sorted(set(LIVE_PACKAGE_ROOTS) - set(by_name))
                raise RuntimeError(f'Pacotes gráficos ausentes do catálogo local: {", ".join(missing)}')
            while pending:
                package = pending.pop()
                package_id = package[0]
                if package_id in selected:
                    continue
                selected.add(package_id)
                for name, version in database.execute(
                        'SELECT name, version FROM deps WHERE package_id = ?', (package_id,)):
                    dependency = by_name_version.get((name, version))
                    if dependency is None:
                        raise RuntimeError(f'Dependência sem pacote no catálogo: {name}-{version}')
                    pending.append(dependency)

            keep_paths = set()
            for package_id, name, version, path in rows:
                if package_id not in selected:
                    continue
                keep_paths.add(f'cache/pkg/{name}-{version}.pkg')
                keep_paths.add(f'cache/pkg/{os.path.basename(path)}')

            all_members = archive.getmembers()
            original_packages = sum(1 for member in all_members
                                    if member.name.startswith('cache/pkg/') and member.name.endswith('.pkg'))
            included_packages = 0
            with tarfile.open(destination, 'w') as output:
                for member in all_members:
                    if member.name in (PKG_REPO_DB_MEMBER, PKG_REPO_META_MEMBER):
                        continue
                    if member.name.startswith('cache/pkg/') and member.name.endswith('.pkg'):
                        if member.name not in keep_paths:
                            continue
                        included_packages += 1
                    file_data = archive.extractfile(member) if member.isreg() else None
                    output.addfile(member, file_data)
            print(f'Cache gráfico reduzido: {len(selected)} dependências; '
                  f'{included_packages}/{original_packages} arquivos de pacote preservados.')
        finally:
            database.close()
        return catalog_path, catalog_meta_path

def main():
    if not SOURCE.is_file():
        raise SystemExit('A ISO Brasa existente não foi encontrada.')
    image = pycdlib.PyCdlib()
    image.open(str(SOURCE))
    try:
        old_rc = read_rr(image, '/etc/rc.local')
        anchor = b'mkdir /tmp/bsdinstall_etc\n'
        if old_rc.count(anchor) != 1:
            raise RuntimeError('O arquivo de inicialização da mídia não é o esperado.')
        hook = (b'# Experimental Brasa live desktop; fall back to stock installer on failure.\n'
                b'if [ -r /brasa/brasa-live-start ]; then\n'
                b'    /bin/sh /brasa/brasa-live-start || true\n'
                b'fi\n\n')
        rc = old_rc.replace(anchor, anchor + b'\n' + hook)
        rc_conf = read_rr(image, '/etc/rc.conf') + b'\ntmpsize="1g"\nvarsize="1g"\n'
        with tempfile.TemporaryDirectory(prefix='brasa-live-') as directory:
            temp = Path(directory)
            virtio_gpu_files = download_virtio_gpu_files(temp) if VIRTIO_GPU_QEMU else {}
            (temp / 'rc.local').write_bytes(rc)
            (temp / 'rc.conf').write_bytes(rc_conf)
            if VIRTIO_GPU_QEMU:
                loader_conf = read_rr(image, '/boot/loader.conf')
                if b'virtio_gpu_qemu_load=' not in loader_conf:
                    loader_conf += (
                        b'\n# QEMU virtio framebuffer, loaded before the built-in driver.\n'
                        b'virtio_gpu_qemu_load="YES"\n'
                        b'hw.virtio_gpu_qemu.width="1280"\n'
                        b'hw.virtio_gpu_qemu.height="800"\n'
                        b'hw.virtio_gpu_qemu.refresh_rate="30"\n'
                    )
                (temp / 'loader.conf').write_bytes(loader_conf)
            package = temp / 'brasa-project.tar.gz'
            with tarfile.open(package, 'w:gz') as archive:
                for folder in ('scripts', 'config', 'docs'):
                    source_folder = ROOT / folder
                    if folder == 'docs':
                        archive.add(
                            source_folder,
                            arcname=folder,
                            filter=lambda member: None if Path(member.name).name == 'RELEASES.md' else member,
                        )
                    else:
                        archive.add(source_folder, arcname=folder)
                archive.add(ROOT / 'README.md', arcname='README.md')
            replace_paths = ['/ETC/RC.LOCAL;1', '/ETC/RC.CONF;1', '/BRASA/BRASA_PROJECT_TAR_GZ;1']
            if VIRTIO_GPU_QEMU:
                replace_paths.append('/BOOT/LOADER.CONF;1')
            for path in replace_paths:
                image.rm_file(iso_path=path)
            pkg_repo_catalog = None
            if PACKAGE_CACHE_ISO:
                cache_archive = temp / 'brasa-pkg-cache.tar'
                catalog_files = (temp / 'freebsd-ports-from-iso.sqlite',
                                 temp / 'freebsd-ports-from-iso.meta')
                cache_image = pycdlib.PyCdlib()
                cache_image.open(str(PACKAGE_CACHE_ISO))
                try:
                    with cache_archive.open('wb') as cache_file:
                        cache_image.get_file_from_iso_fp(cache_file, rr_path='/brasa/BRASA_PKG_CACHE_TAR')
                    external_catalog_available = True
                    for image_path, output_path in zip(
                            ('/brasa/BRASA_PKG_REPOSITORY_DB', '/brasa/BRASA_PKG_REPOSITORY_META'),
                            catalog_files):
                        try:
                            with output_path.open('wb') as output_file:
                                cache_image.get_file_from_iso_fp(output_file, rr_path=image_path)
                        except Exception:
                            output_path.unlink(missing_ok=True)
                            external_catalog_available = False
                            break
                except Exception as error:
                    raise RuntimeError('A ISO de referência não contém o cache/catálogo de pacotes Brasa.') from error
                finally:
                    cache_image.close()
                pruned_cache = temp / 'brasa-pkg-cache-pruned.tar'
                pkg_repo_catalog = prune_package_cache(
                    cache_archive, pruned_cache, temp,
                    catalog_fallback=catalog_files if external_catalog_available else None)
                image.add_file(str(pruned_cache), iso_path='/BRASA/BRASA_PKG_CACHE_TAR;1', rr_name='BRASA_PKG_CACHE_TAR')
            if VIRTIO_GPU_QEMU:
                image.add_file(str(temp / 'loader.conf'), iso_path='/BOOT/LOADER.CONF;1', rr_name='loader.conf')
                image.add_file(str(virtio_gpu_files['/boot/modules/virtio_gpu_qemu.ko']),
                               iso_path='/BOOT/MODULES/VIRTIO_GPU_QEMU.KO;1', rr_name='virtio_gpu_qemu.ko')
                image.add_file(str(virtio_gpu_files['/usr/local/share/X11/xorg.conf.d/20-virtio-gpu-qemu.conf']),
                               iso_path='/BRASA/VIRTIO_GPU_QEMU_XORG.CONF;1', rr_name='virtio_gpu_qemu_xorg.conf')
            image.add_file(str(temp / 'rc.local'), iso_path='/ETC/RC.LOCAL;1', rr_name='rc.local')
            image.add_file(str(temp / 'rc.conf'), iso_path='/ETC/RC.CONF;1', rr_name='rc.conf')
            image.add_file(str(package), iso_path='/BRASA/BRASA_PROJECT_TAR_GZ;1', rr_name='BRASA_PROJECT_TAR_GZ')
            image.add_file(str(ROOT / 'scripts/brasa-live-start'), iso_path='/BRASA/BRASA_LIVE_START;1', rr_name='brasa-live-start')
            if pkg_repo_catalog:
                image.add_file(str(pkg_repo_catalog[0]), iso_path='/BRASA/BRASA_PKG_REPOSITORY_DB;1',
                               rr_name='BRASA_PKG_REPOSITORY_DB')
                image.add_file(str(pkg_repo_catalog[1]), iso_path='/BRASA/BRASA_PKG_REPOSITORY_META;1',
                               rr_name='BRASA_PKG_REPOSITORY_META')
            image.write(str(OUTPUT))
    finally:
        image.close()
    check = pycdlib.PyCdlib()
    check.open(str(OUTPUT))
    try:
        if not check.eltorito_boot_catalog:
            raise RuntimeError('O catálogo de boot foi perdido.')
        required_paths = ['/etc/rc.local', '/brasa/brasa-live-start', '/brasa/BRASA_PROJECT_TAR_GZ']
        if PACKAGE_CACHE_ISO:
            required_paths.extend(['/brasa/BRASA_PKG_CACHE_TAR',
                                   '/brasa/BRASA_PKG_REPOSITORY_DB',
                                   '/brasa/BRASA_PKG_REPOSITORY_META'])
        if VIRTIO_GPU_QEMU:
            required_paths.extend(['/boot/loader.conf', '/boot/modules/virtio_gpu_qemu.ko',
                                   '/brasa/virtio_gpu_qemu_xorg.conf'])
        for path in required_paths:
            if check.get_record(rr_path=path).data_length == 0:
                raise RuntimeError(f'Arquivo vazio na ISO: {path}')
        if VIRTIO_GPU_QEMU and b'virtio_gpu_qemu_load="YES"' not in read_rr(check, '/boot/loader.conf'):
            raise RuntimeError('O módulo virtio_gpu_qemu não foi configurado para carregar no boot.')
    finally:
        check.close()
    print(f'ISO experimental criada: {OUTPUT}')
    print(f'Tamanho: {OUTPUT.stat().st_size:,} bytes')

if __name__ == '__main__':
    main()
