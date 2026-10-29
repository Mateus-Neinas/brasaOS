#!/usr/bin/env python3
"""Make a separate experimental live ISO from the existing Brasa image."""
from pathlib import Path
import io
import os
import hashlib
import json
import shutil
import subprocess
import sqlite3
import sys
import tarfile
import tempfile
import urllib.error
import urllib.request
import pycdlib

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'dist/Brasa-15.1-amd64.iso'
LIVE_PACKAGE_ROOTS = (
    'xorg-minimal', 'xinit', 'jwm', 'zenity', 'dejavu', 'realtek-rge-kmod',
    'xf86-video-vesa', 'xf86-video-scfb',
)
VIRTIO_GPU_KMOD_URL = (
    'https://pkg.freebsd.org/FreeBSD:15:amd64/quarterly/All/'
    'virtio-gpu-qemu-kmod-0.2.1501000_1.pkg'
)
FREEBSD_PKG_REPOSITORY_URL = 'https://pkg.freebsd.org/FreeBSD:15:amd64/quarterly/'
VIRTIO_GPU_KMOD_SHA256 = '97f42fe414e1a254142bdefe94d03538abe12874707eea36e9161beec4eed6bf'
VIRTIO_GPU_FILES = {
    '/boot/modules/virtio_gpu_qemu.ko': 'virtio_gpu_qemu.ko',
    '/usr/local/share/X11/xorg.conf.d/20-virtio-gpu-qemu.conf': 'virtio_gpu_qemu_xorg.conf',
}
PKG_REPO_DB_MEMBER = 'db/pkg/repos/FreeBSD-ports/db'
PKG_REPO_META_MEMBER = 'db/pkg/repos/FreeBSD-ports/meta'
FREEBSD_DIST_URL = 'https://download.freebsd.org/releases/amd64/amd64/15.1-RELEASE/'
FREEBSD_DIST_FILES = {
    'MANIFEST': '70ba0347054099662f22434797f1f33be289fc868ba58d6069a490b3e395d684',
    'base.txz': '3768988b151c20f965679062b065c63a977d6bbb9f47fd83695ec2c40790c18f',
    'kernel.txz': '49fea8ee25d0b1c523a02309efe4711d44a21ed0b36fb4191936a27a09324313',
}

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

def reuse_virtio_gpu_files(source_iso, destination):
    """Reuse the verified runtime driver/config shipped in an earlier Brasa ISO."""
    cached = pycdlib.PyCdlib()
    cached.open(str(source_iso))
    try:
        extracted = {}
        for member, output_name in VIRTIO_GPU_FILES.items():
            # r26 stored the Xorg file under /brasa while retaining the package path
            # for the kernel module.
            iso_path = ('/brasa/virtio_gpu_qemu_xorg.conf'
                        if output_name == 'virtio_gpu_qemu_xorg.conf' else member)
            output = destination / output_name
            try:
                output.write_bytes(read_rr(cached, iso_path))
            except Exception:
                return None
            if output.stat().st_size == 0:
                return None
            extracted[member] = output
        return extracted
    finally:
        cached.close()

def download_realtek_rge_module(source_iso, destination):
    """Embed the ABI-matched FreeBSD module for RTL8125/8126/8127 Ethernet."""
    if not source_iso:
        raise RuntimeError('A ISO de referência é necessária para obter o catálogo do driver Ethernet.')
    cached = pycdlib.PyCdlib()
    cached.open(str(source_iso))
    try:
        catalog = destination / 'realtek-rge-catalog.sqlite'
        with catalog.open('wb') as stream:
            cached.get_file_from_iso_fp(stream, rr_path='/brasa/BRASA_PKG_REPOSITORY_DB')
    finally:
        cached.close()
    database = sqlite3.connect(catalog)
    try:
        package = database.execute(
            "SELECT version, path, pkgsize FROM packages WHERE name = 'realtek-rge-kmod' "
            "ORDER BY version DESC LIMIT 1"
        ).fetchone()
    finally:
        database.close()
    if not package:
        raise RuntimeError('O catálogo FreeBSD embutido não contém o driver Realtek RGE.')
    version, path, expected_size = package
    package_path = destination / f'realtek-rge-kmod-{version}.pkg'
    # Repository snapshots may prune the old content-hash URL while retaining
    # the same immutable package version under All/<name>-<version>.pkg.
    package_url = FREEBSD_PKG_REPOSITORY_URL + f'All/realtek-rge-kmod-{version}.pkg'
    with urllib.request.urlopen(package_url, timeout=60) as response, package_path.open('wb') as output:
        shutil.copyfileobj(response, output)
    module_path = destination / 'if_rge.ko'
    try:
        with tarfile.open(package_path, 'r:*') as package_archive:
            manifest = json.load(package_archive.extractfile('+COMPACT_MANIFEST'))
            if (manifest.get('name') != 'realtek-rge-kmod' or
                    manifest.get('version') != version or
                    manifest.get('abi') != 'FreeBSD:15:amd64'):
                raise RuntimeError('O pacote Realtek RGE não corresponde à versão/ABI do catálogo FreeBSD.')
            member = next((item for item in package_archive.getmembers()
                           if item.name.lstrip('./').endswith('boot/modules/if_rge.ko')), None)
            if member is None:
                raise RuntimeError('O pacote Realtek RGE não contém boot/modules/if_rge.ko.')
            with module_path.open('wb') as output:
                shutil.copyfileobj(package_archive.extractfile(member), output)
    except RuntimeError:
        raise
    except Exception as error:
        raise RuntimeError('Falha ao validar ou extrair o pacote Realtek RGE.') from error
    if module_path.stat().st_size < 1024:
        raise RuntimeError('O módulo if_rge.ko extraído está vazio ou incompleto.')
    if package_path.stat().st_size != expected_size:
        print(f'Nota: o mirror FreeBSD forneceu {package_path.stat().st_size} bytes; '
              f'o catálogo de 1.37c registra {expected_size}. Manifesto e ABI conferidos.')
    print(f'Driver FreeBSD realtek-rge-kmod {version} incluído para RTL8125/8126/8127.')
    return module_path

def get_freebsd_distribution_files():
    """Fetch official 15.1 base/kernel sets once and verify pinned hashes."""
    directory = ROOT / '.build/freebsd-15.1-dist'
    directory.mkdir(parents=True, exist_ok=True)
    result = {}
    for name, expected in FREEBSD_DIST_FILES.items():
        path = directory / name
        digest = hashlib.sha256()
        if path.is_file():
            with path.open('rb') as existing:
                while block := existing.read(1024 * 1024):
                    digest.update(block)
        if not path.is_file() or digest.hexdigest() != expected:
            partial = path.with_suffix(path.suffix + '.partial')
            partial.unlink(missing_ok=True)
            digest = hashlib.sha256()
            with urllib.request.urlopen(FREEBSD_DIST_URL + name, timeout=120) as response, partial.open('wb') as output:
                while block := response.read(1024 * 1024):
                    digest.update(block)
                    output.write(block)
            if digest.hexdigest() != expected:
                partial.unlink(missing_ok=True)
                raise RuntimeError(f'O arquivo oficial FreeBSD {name} não corresponde ao SHA-256 fixado.')
            partial.replace(path)
        result[name] = path

    # Keep the requested class-compliant USB audio module in the ISO kernel set.
    with tarfile.open(result['kernel.txz'], 'r:xz') as kernel:
        if not any(member.name.removeprefix('./') == 'boot/kernel/snd_uaudio.ko'
                   for member in kernel.getmembers()):
            raise RuntimeError('O kernel FreeBSD incluído não contém snd_uaudio.ko.')
    return result

def read_rr(image, path):
    data = io.BytesIO()
    image.get_file_from_iso_fp(data, rr_path=path)
    return data.getvalue()

def add_normalized_project_tree(archive, source, arcname, exclude_release_notes=False):
    """Embed project files with Unix newlines so FreeBSD shell scripts parse."""
    source = Path(source)
    archive.addfile(archive.gettarinfo(str(source), arcname=arcname))
    for path in sorted(source.rglob('*')):
        relative = path.relative_to(source).as_posix()
        if exclude_release_notes and Path(relative).name == 'RELEASES.md':
            continue
        member_name = f'{arcname}/{relative}'
        info = archive.gettarinfo(str(path), arcname=member_name)
        if path.is_dir() or path.is_symlink():
            archive.addfile(info)
            continue
        data = path.read_bytes()
        if b'\0' not in data:
            data = data.replace(b'\r\n', b'\n')
        info.size = len(data)
        archive.addfile(info, io.BytesIO(data))

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
                'SELECT id, name, version, path, pkgsize FROM packages'
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
            present_paths = {member.name for member in archive.getmembers()}
            downloaded_packages = []
            package_archives = []
            for package_id, name, version, path, package_size in rows:
                if package_id not in selected:
                    continue
                regular_path = f'cache/pkg/{name}-{version}.pkg'
                hashed_path = f'cache/pkg/{os.path.basename(path)}'
                if regular_path in present_paths or hashed_path in present_paths:
                    selected_path = hashed_path if hashed_path in present_paths else regular_path
                    keep_paths.add(selected_path)
                    package_archives.append(os.path.basename(selected_path))
                    continue
                # A cache may have the dependency catalog but omit a handful
                # of required GUI packages. Fetch only those absent archives
                # while building the ISO so boot never waits for pkg update.
                destination_path = temporary_directory / os.path.basename(path)
                package_url = FREEBSD_PKG_REPOSITORY_URL + path
                unhashed_fallback = False
                try:
                    response = urllib.request.urlopen(package_url, timeout=60)
                except urllib.error.HTTPError as error:
                    if error.code != 404:
                        raise
                    # Mirrors may prune old content-hash URLs while the same
                    # immutable version remains available in the flat All dir.
                    package_url = (FREEBSD_PKG_REPOSITORY_URL +
                                   f'All/{name}-{version}.pkg')
                    response = urllib.request.urlopen(package_url, timeout=60)
                    unhashed_fallback = True
                with response, destination_path.open('wb') as output:
                    while block := response.read(1024 * 1024):
                        output.write(block)
                try:
                    with tarfile.open(destination_path, 'r:*') as fetched:
                        manifest = json.load(fetched.extractfile('+COMPACT_MANIFEST'))
                except Exception as error:
                    raise RuntimeError(f'O pacote {name}-{version} não tem manifesto válido.') from error
                if (manifest.get('name') != name or manifest.get('version') != version or
                        manifest.get('abi') != 'FreeBSD:15:amd64'):
                    raise RuntimeError(f'O manifesto do pacote {name}-{version} não corresponde ao catálogo/ABI FreeBSD 15.')
                if destination_path.stat().st_size != package_size:
                    if not unhashed_fallback:
                        raise RuntimeError(f'O pacote gráfico {name}-{version} veio incompleto do repositório FreeBSD.')
                    print(f'Nota: mirror entregou {destination_path.stat().st_size} bytes para {name}-{version}; '
                          f'o catálogo registra {package_size}. Manifesto e ABI conferidos.')
                downloaded_packages.append((destination_path, hashed_path))
                keep_paths.add(hashed_path)
                package_archives.append(os.path.basename(hashed_path))

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
                for package_path, archive_path in downloaded_packages:
                    output.add(package_path, arcname=archive_path)
            print(f'Cache gráfico reduzido: {len(selected)} dependências; '
                  f'{included_packages} arquivos preservados e {len(downloaded_packages)} ausentes baixados.')
        finally:
            database.close()
        archives_path = temporary_directory / 'brasa-live-package-archives'
        archives_path.write_bytes(''.join(f'{name}\n' for name in package_archives).encode('ascii'))
        return catalog_path, catalog_meta_path, archives_path

def main():
    if not SOURCE.is_file():
        raise SystemExit('A ISO Brasa existente não foi encontrada.')
    image = pycdlib.PyCdlib()
    image.open(str(SOURCE))
    try:
        old_rc = read_rr(image, '/etc/rc.local')
        pkgbase_script = read_rr(image, '/usr/libexec/bsdinstall/pkgbase')
        bsdinstall_script = read_rr(image, '/usr/libexec/bsdinstall/script')
        bsdinstall_config = read_rr(image, '/usr/libexec/bsdinstall/config')
        config_helper_anchor = b'############################################################ MAIN\n'
        config_helper = (config_helper_anchor +
                         b'brasa_config_phase() {\n'
                         b'\tprintf "%s\\n" "$1" > /tmp/brasa-install-phase\n'
                         b'\tshift\n'
                         b'\tprintf "Brasa: bsdinstall config: %s.\\n" "$*"\n'
                         b'}\n\n')
        if bsdinstall_config.count(config_helper_anchor) != 1:
            raise RuntimeError('Nao foi possivel instrumentar o inicio do bsdinstall config.')
        bsdinstall_config = bsdinstall_config.replace(config_helper_anchor, config_helper)
        config_markers = (
            (b'cat $BSDINSTALL_TMPETC/rc.conf.* >> $BSDINSTALL_TMPETC/rc.conf',
             b'brasa_config_phase bsdinstall-config-rcconf "Consolidando rc.conf"\n'
             b'cat $BSDINSTALL_TMPETC/rc.conf.* >> $BSDINSTALL_TMPETC/rc.conf'),
            (b'cp $BSDINSTALL_TMPETC/* $BSDINSTALL_CHROOT/etc',
             b'brasa_config_phase bsdinstall-config-etc "Copiando configuracao do sistema"\n'
             b'cp $BSDINSTALL_TMPETC/* $BSDINSTALL_CHROOT/etc'),
            (b'cp $BSDINSTALL_TMPBOOT/* $BSDINSTALL_CHROOT/boot',
             b'brasa_config_phase bsdinstall-config-boot "Copiando configuracao de boot"\n'
             b'cp $BSDINSTALL_TMPBOOT/* $BSDINSTALL_CHROOT/boot'),
            (b'chroot $BSDINSTALL_CHROOT /usr/bin/newaliases > /dev/null 2>&1',
             b'brasa_config_phase bsdinstall-config-newaliases "Executando newaliases"\n'
             b'chroot $BSDINSTALL_CHROOT /usr/bin/newaliases > /dev/null 2>&1\n'
             b'brasa_config_phase bsdinstall-config-newaliases-done "newaliases concluido"'),
            (b'exit 0', b'brasa_config_phase bsdinstall-config-complete "Etapa concluida"\nexit 0'),
        )
        for anchor, replacement in config_markers:
            if bsdinstall_config.count(anchor) != 1:
                raise RuntimeError('Nao foi possivel instrumentar uma etapa do bsdinstall config.')
            bsdinstall_config = bsdinstall_config.replace(anchor, replacement)
        phase_anchor = b'set -e\ntrap error EXIT\n'
        phase_helper = (
            phase_anchor +
            b'\nbrasa_phase() {\n'
            b'\tprintf "%s\\n" "$1" > /tmp/brasa-install-phase\n'
            b'}\n')
        if bsdinstall_script.count(phase_anchor) != 1:
            raise RuntimeError('Não foi possível localizar o início do fluxo bsdinstall para as fases Brasa.')
        bsdinstall_script = bsdinstall_script.replace(phase_anchor, phase_helper)
        phase_markers = (
            (b'rm -f $PATH_FSTAB\ntouch $PATH_FSTAB\n',
             b'rm -f $PATH_FSTAB\ntouch $PATH_FSTAB\nbrasa_phase particionando\n'),
            (b'\tbsdinstall checksum\n',
             b'\tbrasa_phase verificando-distribuicoes\n\tbsdinstall checksum\n'),
            (b'\t\tfor set in $DISTRIBUTIONS; do\n',
             b'\t\tfor set in $DISTRIBUTIONS; do\n'
             b'\t\t\tcase "$set" in\n'
             b'\t\t\t\tbase.txz) brasa_phase extraindo-base ;;\n'
             b'\t\t\t\tkernel.txz) brasa_phase extraindo-kernel ;;\n'
             b'\t\t\t\t*) brasa_phase extraindo-arquivos ;;\n'
             b'\t\t\tesac\n'),
            (b'\n# Configure bootloader if needed\n',
             b'\nbrasa_phase configurando-boot\n# Configure bootloader if needed\n'),
            (b'\n# Finalize install\n',
             b'\nbrasa_phase configurando-sistema\n# Finalize install\n'),
            (b'\nbsdinstall config\n',
             b'\nbrasa_phase bsdinstall-config-start\n'
             b'printf "Brasa: bsdinstall config: iniciando.\\n"\n'
             b'bsdinstall config\n'
             b'brasa_phase bsdinstall-config-returned\n'),
            (b'\n# Run post-install script\n',
             b'\nbrasa_phase configurando-brasa\n# Run post-install script\n'),
        )
        for anchor, replacement in phase_markers:
            if bsdinstall_script.count(anchor) != 1:
                raise RuntimeError('Não foi possível localizar uma etapa bsdinstall para exibir o progresso.')
            bsdinstall_script = bsdinstall_script.replace(anchor, replacement)
        resolver_anchor = b'brasa_phase configurando-brasa\n# Run post-install script\n'
        resolver_copy = (b'brasa_phase configurando-brasa\n'
                         b'# bsdinstall config cleans the live resolver link target; use the pre-install snapshot.\n'
                         b'if [ -s "$BRASA_RESOLV_CONF" ]; then\n'
                         b'\trm -f $BSDINSTALL_CHROOT/etc/resolv.conf\n'
                         b'\tcp "$BRASA_RESOLV_CONF" $BSDINSTALL_CHROOT/etc/resolv.conf\n'
                         b'fi\n'
                         b'# Run post-install script\n')
        if bsdinstall_script.count(resolver_anchor) != 1:
            raise RuntimeError('Não foi possível localizar o ponto de sincronização do DNS no sistema-alvo.')
        bsdinstall_script = bsdinstall_script.replace(resolver_anchor, resolver_copy)
        postinstall_markers = (
            (b'if [ -f $TMPDIR/bsdinstall-installscript-setup ]; then\n',
             b'brasa_phase bsdinstall-postinstall-copy\n'
             b'printf "Brasa: preparando o script de instalacao no sistema-alvo.\\n"\n'
             b'if [ -f $TMPDIR/bsdinstall-installscript-setup ]; then\n'),
            (b'\tcp $TMPDIR/bsdinstall-installscript-setup \\\n\t    $BSDINSTALL_CHROOT/tmp/installscript\n',
             b'\tbrasa_phase bsdinstall-postinstall-copy\n'
             b'\tcp $TMPDIR/bsdinstall-installscript-setup \\\n\t    $BSDINSTALL_CHROOT/tmp/installscript\n'),
            (b'\tchmod a+x $BSDINSTALL_CHROOT/tmp/installscript\n',
             b'\tbrasa_phase bsdinstall-postinstall-chmod\n'
             b'\tchmod a+x $BSDINSTALL_CHROOT/tmp/installscript\n'),
            (b'\tchroot $BSDINSTALL_CHROOT /tmp/installscript $@ 2>&1\n',
             b'\tbrasa_phase bsdinstall-postinstall-start\n'
             b'\tbrasa_log=$BSDINSTALL_CHROOT/tmp/brasa-installscript.log\n'
             b'\t: > "$brasa_log"\n'
             b'\tchroot $BSDINSTALL_CHROOT /bin/sh /tmp/installscript $@ > "$brasa_log" 2>&1 &\n'
             b'\tbrasa_pid=$!\n'
             b'\tbrasa_last_line=\n'
             b'\twhile :; do\n'
             b'\t\tbrasa_state=$(ps -o stat= -p "$brasa_pid" 2>/dev/null || true)\n'
             b"\t\tcase \"$brasa_state\" in Z*|'') break ;; esac\n"
             b'\t\tbrasa_line=$(tail -n 1 "$brasa_log" 2>/dev/null || true)\n'
             b'\t\tif [ -n "$brasa_line" ] && [ "$brasa_line" != "$brasa_last_line" ]; then\n'
             b'\t\t\tprintf "%s\\n" "$brasa_line"\n'
             b'\t\t\tbrasa_last_line=$brasa_line\n'
             b'\t\tfi\n'
             b'\t\tsleep 2\n'
             b'\tdone\n'
             b'\tif wait "$brasa_pid"; then\n'
             b'\t\tbrasa_line=$(tail -n 1 "$brasa_log" 2>/dev/null || true)\n'
             b'\t\tif [ -n "$brasa_line" ] && [ "$brasa_line" != "$brasa_last_line" ]; then printf "%s\\n" "$brasa_line"; fi\n'
             b'\t\tbrasa_phase bsdinstall-postinstall-returned\n'
             b'\telse\n'
             b'\t\tbrasa_status=$?\n'
             b'\t\tcat "$brasa_log"\n'
             b'\t\texit "$brasa_status"\n'
             b'\tfi\n'),
            (b'\trm $BSDINSTALL_CHROOT/tmp/installscript\n',
             b'\tbrasa_phase bsdinstall-postinstall-cleanup\n'
             b'\trm $BSDINSTALL_CHROOT/tmp/installscript\n'),
        )
        for anchor, replacement in postinstall_markers:
            if bsdinstall_script.count(anchor) != 1:
                raise RuntimeError('Nao foi possivel instrumentar o inicio do script pos-instalacao.')
            bsdinstall_script = bsdinstall_script.replace(anchor, replacement)
        anchor = b'mkdir /tmp/bsdinstall_etc\n'
        if old_rc.count(anchor) != 1:
            raise RuntimeError('O arquivo de inicialização da mídia não é o esperado.')
        hook = (b'# Experimental Brasa live desktop; fall back to stock installer on failure.\n'
                b'if [ -r /brasa/brasa-live-start ]; then\n'
                b'    if /bin/sh /brasa/brasa-live-start; then\n'
                b'        # A normal exit, including a cancel choice, must not\n'
                b'        # fall through to a second, unrelated text installer.\n'
                b'        exit 0\n'
                b'    fi\n'
                b'fi\n\n')
        rc = old_rc.replace(anchor, anchor + b'\n' + hook)
        rc_conf = read_rr(image, '/etc/rc.conf') + b'\ntmpsize="1g"\nvarsize="1g"\n'
        # The live desktop needs USB HID input, display and Ethernet. Do not
        # let devd start a Bluetooth HCI stack for optional adapters: several
        # laptop combo chips time out during HCI reset, producing noisy errors
        # while the Brasa graphical bootstrap is starting. The installed OS
        # gets the stock Bluetooth configuration from its own base packages.
        bluetooth_devd = (b'# Brasa live image: do not auto-start the optional Bluetooth stack.\n'
                          b'# USB keyboards and mice continue to use the normal HID drivers.\n')
        with tempfile.TemporaryDirectory(prefix='brasa-live-') as directory:
            temp = Path(directory)
            freebsd_dist_files = get_freebsd_distribution_files()
            virtio_gpu_files = {}
            if VIRTIO_GPU_QEMU:
                if PACKAGE_CACHE_ISO:
                    virtio_gpu_files = reuse_virtio_gpu_files(PACKAGE_CACHE_ISO, temp) or {}
                if not virtio_gpu_files:
                    virtio_gpu_files = download_virtio_gpu_files(temp)
            rge_module = download_realtek_rge_module(PACKAGE_CACHE_ISO, temp)
            (temp / 'rc.local').write_bytes(rc)
            (temp / 'rc.conf').write_bytes(rc_conf)
            (temp / 'bluetooth.devd.conf').write_bytes(bluetooth_devd)
            (temp / 'bsdinstall-pkgbase').write_bytes(pkgbase_script)
            (temp / 'bsdinstall-script').write_bytes(bsdinstall_script)
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
                    add_normalized_project_tree(
                        archive, ROOT / folder, folder, exclude_release_notes=(folder == 'docs'))
                readme = (ROOT / 'README.md').read_bytes().replace(b'\r\n', b'\n')
                info = archive.gettarinfo(str(ROOT / 'README.md'), arcname='README.md')
                info.size = len(readme)
                archive.addfile(info, io.BytesIO(readme))
            replace_paths = [
                '/ETC/RC.LOCAL;1', '/ETC/RC.CONF;1',
                '/ETC/DEVD/BLUETOOTH.CONF;1',
                '/USR/LIBEXEC/BSDINSTALL/PKGBASE.;1',
                '/USR/LIBEXEC/BSDINSTALL/SCRIPT.;1',
                '/USR/LIBEXEC/BSDINSTALL/CONFIG.;1',
                '/BRASA/BRASA_PROJECT_TAR_GZ;1',
            ]
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
            image.add_file(str(temp / 'bluetooth.devd.conf'),
                           iso_path='/ETC/DEVD/BLUETOOTH.CONF;1', rr_name='bluetooth.conf')
            image.add_file(str(temp / 'bsdinstall-pkgbase'),
                           iso_path='/USR/LIBEXEC/BSDINSTALL/PKGBASE.;1',
                           rr_name='pkgbase', file_mode=0o100555)
            image.add_file(str(temp / 'bsdinstall-script'),
                           iso_path='/USR/LIBEXEC/BSDINSTALL/SCRIPT.;1',
                           rr_name='script', file_mode=0o100555)
            instrumented_config = temp / 'bsdinstall-config'
            instrumented_config.write_bytes(bsdinstall_config)
            image.add_file(str(instrumented_config),
                           iso_path='/USR/LIBEXEC/BSDINSTALL/CONFIG.;1',
                           rr_name='config', file_mode=0o100555)
            image.add_file(str(package), iso_path='/BRASA/BRASA_PROJECT_TAR_GZ;1', rr_name='BRASA_PROJECT_TAR_GZ')
            image.add_directory(iso_path='/BRASA/FREEBSD_DIST', rr_name='freebsd-dist')
            for name, path in freebsd_dist_files.items():
                image.add_file(str(path),
                               iso_path=f'/BRASA/FREEBSD_DIST/{name.upper()};1',
                               rr_name=name)
            image.add_file(str(ROOT / 'scripts/brasa-live-start'), iso_path='/BRASA/BRASA_LIVE_START;1', rr_name='brasa-live-start')
            image.add_file(str(rge_module), iso_path='/BRASA/IF_RGE.KO;1', rr_name='if_rge.ko')
            if pkg_repo_catalog:
                image.add_file(str(pkg_repo_catalog[0]), iso_path='/BRASA/BRASA_PKG_REPOSITORY_DB;1',
                               rr_name='BRASA_PKG_REPOSITORY_DB')
                image.add_file(str(pkg_repo_catalog[1]), iso_path='/BRASA/BRASA_PKG_REPOSITORY_META;1',
                               rr_name='BRASA_PKG_REPOSITORY_META')
                image.add_file(str(pkg_repo_catalog[2]), iso_path='/BRASA/BRASA_LIVE_PKG_ARCHIVES;1',
                               rr_name='BRASA_LIVE_PKG_ARCHIVES')
            image.write(str(OUTPUT))
    finally:
        image.close()
    check = pycdlib.PyCdlib()
    check.open(str(OUTPUT))
    try:
        if not check.eltorito_boot_catalog:
            raise RuntimeError('O catálogo de boot foi perdido.')
        rc_local = read_rr(check, '/etc/rc.local')
        if (b'if /bin/sh /brasa/brasa-live-start; then' not in rc_local or
                b'        exit 0\n' not in rc_local):
            raise RuntimeError('A saída normal do live Brasa ainda cai no instalador texto do FreeBSD.')
        bluetooth_config = read_rr(check, '/etc/devd/bluetooth.conf')
        if b'service bluetooth quietstart' in bluetooth_config:
            raise RuntimeError('O live não pode iniciar automaticamente a pilha Bluetooth opcional.')
        live_start = read_rr(check, '/brasa/brasa-live-start')
        if (b'brasa-pkg-seed' in live_start or
                live_start.count(b'tar -xf /brasa/BRASA_PKG_CACHE_TAR -C /var') != 1):
            raise RuntimeError('O cache de pacotes live deve ser extraído apenas uma vez para /var.')
        rge_payload = read_rr(check, '/brasa/if_rge.ko')
        if len(rge_payload) < 1024 or b'prepare_network()' not in live_start or \
                b'kldload /brasa/if_rge.ko' not in live_start or \
                b'media:.*Ethernet' not in live_start or b'dhclient -b' not in live_start:
            raise RuntimeError('A ISO precisa carregar o driver Ethernet extra e tentar DHCP nas interfaces cabeadas reconhecidas.')
        if PACKAGE_CACHE_ISO:
            package_archives = read_rr(check, '/brasa/BRASA_LIVE_PKG_ARCHIVES').decode('ascii').splitlines()
            if len(package_archives) < 100 or len(package_archives) != len(set(package_archives)) or \
                    any('/' in name or not name.endswith('.pkg') for name in package_archives):
                raise RuntimeError('A ISO precisa fornecer uma vez cada pacote da árvore gráfica cacheada.')
        project_payload = read_rr(check, '/brasa/BRASA_PROJECT_TAR_GZ')
        with tarfile.open(fileobj=io.BytesIO(project_payload), mode='r:gz') as project_archive:
            assistant = project_archive.extractfile('scripts/brasa-install-assistant').read()
            bootstrap = project_archive.extractfile('scripts/bootstrap-freebsd.sh').read()
        for marker in (b'Brasa: Extraindo os arquivos de configura\xc3\xa7\xc3\xa3o do Brasa.',
                       b'Brasa: Criando a conta de usu\xc3\xa1rio.',
                       b'Brasa: Iniciando o bootstrap do desktop e dos componentes.'):
            if marker not in assistant:
                raise RuntimeError('A ISO precisa mostrar cada etapa anterior ao bootstrap do Brasa.')
        if (b'*) progress_message=$output_line ;;' not in assistant or
                b'Preparando o gerenciador de pacotes pkg.' not in bootstrap or
                b'Verificando a disponibilidade do Wine.' not in bootstrap):
            raise RuntimeError('A ISO precisa exibir a saída do instalador e as consultas de pacotes.')
        bsd_script_payload = read_rr(check, '/usr/libexec/bsdinstall/script')
        for marker in (b'bsdinstall-config-start', b'bsdinstall-config-returned',
                       b'bsdinstall-postinstall-copy', b'bsdinstall-postinstall-chmod',
                       b'bsdinstall-postinstall-start', b'bsdinstall-postinstall-returned',
                       b'brasa_state=$(ps -o stat= -p \"$brasa_pid\" 2>/dev/null || true)',
                       b'cp "$BRASA_RESOLV_CONF" $BSDINSTALL_CHROOT/etc/resolv.conf'):
            if marker not in bsd_script_payload:
                raise RuntimeError('A ISO precisa identificar a entrada e a saida de bsdinstall config.')
        config_payload = read_rr(check, '/usr/libexec/bsdinstall/config')
        for marker in (b'brasa_config_phase() {', b'bsdinstall-config-rcconf',
                       b'bsdinstall-config-etc', b'bsdinstall-config-boot',
                       b'bsdinstall-config-newaliases', b'bsdinstall-config-complete'):
            if marker not in config_payload:
                raise RuntimeError('A ISO precisa identificar cada subetapa do bsdinstall config.')
        for marker in (b'bsdinstall-config-start)', b'bsdinstall-config-returned)',
                       b'bsdinstall-config-rcconf)', b'bsdinstall-config-newaliases)',
                       b'bsdinstall-postinstall-copy)', b'bsdinstall-postinstall-chmod)',
                       b'bsdinstall-postinstall-start)', b'bsdinstall-postinstall-returned)'):
            if marker not in assistant:
                raise RuntimeError('O progresso precisa traduzir as subetapas do bsdinstall config.')
        if b"bsdinstall-postinstall-start)\n        case \"$output_line\" in" not in assistant:
            raise RuntimeError('O progresso deve preservar a saída real do script pós-instalação.')
        if (b'cat > "$install_script" <<EOF\nPARTITIONS=' not in assistant or
                b'export DISTRIBUTIONS\n\n#!/bin/sh\nset -eu' not in assistant):
            raise RuntimeError('As variáveis bsdinstall precisam ficar antes do separador shebang do script.')
        if (b'cp -L /etc/resolv.conf "$resolver_file"' not in assistant or
                b'export BRASA_RESOLV_CONF="$resolver_file"' not in assistant or
                b'cp "$BRASA_RESOLV_CONF" $BSDINSTALL_CHROOT/etc/resolv.conf' not in bsd_script_payload):
            raise RuntimeError('A instalação precisa salvar o DNS live antes do bsdinstall config e restaurá-lo no alvo.')
        if b"tr -d '\\015' < \"$install_script\" > \"$install_script.normalized\"" not in assistant:
            raise RuntimeError('O script de pós-instalação precisa remover CR antes de ser executado pelo chroot.')
        if (b'repo_catalog_file' in assistant or b'cat <&10' in assistant or
                b'cat <&11' in assistant or b'tar -xf - -C /var/db/pkg/repos' in assistant):
            raise RuntimeError('O script não deve copiar catálogos com descritores frágeis; o sistema-alvo atualiza via pkg.')
        if b'report_install_processes() {' not in assistant or \
                b'ps -ax -o pid,ppid,stat,etime,pcpu,command' not in assistant:
            raise RuntimeError('A ISO precisa registrar os processos ativos do instalador durante esperas longas.')
        for marker in (b'Brasa: Inicializando as configura\xc3\xa7\xc3\xb5es do sistema instalado.',
                       b'Brasa: Dados da conta recebidos.',
                       b'Brasa: Arquivos de configura\xc3\xa7\xc3\xa3o extra\xc3\xaddos.',
                       b'Brasa: Conta de usu\xc3\xa1rio criada.'):
            if marker not in assistant:
                raise RuntimeError('A ISO precisa mostrar o progresso interno do script pos-instalacao.')
        required_paths = ['/etc/rc.local', '/brasa/brasa-live-start', '/brasa/BRASA_PROJECT_TAR_GZ',
                          '/brasa/freebsd-dist/MANIFEST', '/brasa/freebsd-dist/base.txz',
                          '/brasa/freebsd-dist/kernel.txz']
        if PACKAGE_CACHE_ISO:
            required_paths.extend(['/brasa/BRASA_PKG_CACHE_TAR',
                                   '/brasa/BRASA_PKG_REPOSITORY_DB',
                                   '/brasa/BRASA_PKG_REPOSITORY_META',
                                   '/brasa/BRASA_LIVE_PKG_ARCHIVES'])
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
