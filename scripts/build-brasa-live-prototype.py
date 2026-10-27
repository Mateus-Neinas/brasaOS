#!/usr/bin/env python3
"""Make a separate experimental live ISO from the existing Brasa image."""
from pathlib import Path
import io
import os
import sqlite3
import sys
import tarfile
import tempfile
import pycdlib

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'dist/Brasa-15.1-amd64.iso'
if len(sys.argv) > 2:
    if sys.argv[1] == '--help':
        print('Uso: build-brasa-live-prototype.py [caminho-da-iso-de-saida] [--package-cache-iso ISO]')
        raise SystemExit(0)

def parse_args():
    output = ROOT / '.build/Brasa-live-experimental.iso'
    cache_iso = None
    positional_seen = False
    args = iter(sys.argv[1:])
    for arg in args:
        if arg == '--package-cache-iso':
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
    return output, cache_iso

OUTPUT, PACKAGE_CACHE_ISO = parse_args()
LIVE_PACKAGE_ROOTS = (
    'xorg-minimal', 'xinit', 'jwm', 'zenity', 'dejavu',
    'xf86-video-vesa', 'xf86-video-scfb',
)

def read_rr(image, path):
    data = io.BytesIO()
    image.get_file_from_iso_fp(data, rr_path=path)
    return data.getvalue()

def prune_package_cache(source, destination, temporary_directory):
    """Keep cached packages needed by the live GUI dependency closure."""
    with tarfile.open(source, 'r:*') as archive:
        catalog_member = next((member for member in archive.getmembers()
                               if member.name.endswith('db/pkg/repos/FreeBSD-ports/db')), None)
        if catalog_member is None:
            raise RuntimeError('O cache não contém o catálogo FreeBSD-ports necessário para reduzir os pacotes.')
        catalog_path = temporary_directory / 'freebsd-ports.sqlite'
        with catalog_path.open('wb') as catalog_file:
            catalog_file.write(archive.extractfile(catalog_member).read())

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
            (temp / 'rc.local').write_bytes(rc)
            (temp / 'rc.conf').write_bytes(rc_conf)
            package = temp / 'brasa-project.tar.gz'
            with tarfile.open(package, 'w:gz') as archive:
                for folder in ('scripts', 'config', 'docs'):
                    archive.add(ROOT / folder, arcname=folder)
                archive.add(ROOT / 'README.md', arcname='README.md')
            for path in ('/ETC/RC.LOCAL;1', '/ETC/RC.CONF;1', '/BRASA/BRASA_PROJECT_TAR_GZ;1'):
                image.rm_file(iso_path=path)
            if PACKAGE_CACHE_ISO:
                cache_archive = temp / 'brasa-pkg-cache.tar'
                cache_image = pycdlib.PyCdlib()
                cache_image.open(str(PACKAGE_CACHE_ISO))
                try:
                    with cache_archive.open('wb') as cache_file:
                        cache_image.get_file_from_iso_fp(cache_file, rr_path='/brasa/BRASA_PKG_CACHE_TAR')
                except Exception as error:
                    raise RuntimeError('A ISO de referência não contém o cache Brasa de pacotes.') from error
                finally:
                    cache_image.close()
                pruned_cache = temp / 'brasa-pkg-cache-pruned.tar'
                prune_package_cache(cache_archive, pruned_cache, temp)
                image.add_file(str(pruned_cache), iso_path='/BRASA/BRASA_PKG_CACHE_TAR;1', rr_name='BRASA_PKG_CACHE_TAR')
            image.add_file(str(temp / 'rc.local'), iso_path='/ETC/RC.LOCAL;1', rr_name='rc.local')
            image.add_file(str(temp / 'rc.conf'), iso_path='/ETC/RC.CONF;1', rr_name='rc.conf')
            image.add_file(str(package), iso_path='/BRASA/BRASA_PROJECT_TAR_GZ;1', rr_name='BRASA_PROJECT_TAR_GZ')
            image.add_file(str(ROOT / 'scripts/brasa-live-start'), iso_path='/BRASA/BRASA_LIVE_START;1', rr_name='brasa-live-start')
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
            required_paths.append('/brasa/BRASA_PKG_CACHE_TAR')
        for path in required_paths:
            if check.get_record(rr_path=path).data_length == 0:
                raise RuntimeError(f'Arquivo vazio na ISO: {path}')
    finally:
        check.close()
    print(f'ISO experimental criada: {OUTPUT}')
    print(f'Tamanho: {OUTPUT.stat().st_size:,} bytes')

if __name__ == '__main__':
    main()
