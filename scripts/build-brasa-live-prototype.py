#!/usr/bin/env python3
"""Make a separate experimental live ISO from the existing Brasa image."""
from pathlib import Path
import io
import sys
import tarfile
import tempfile
import pycdlib

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'dist/Brasa-15.1-amd64.iso'
if len(sys.argv) > 2:
    raise SystemExit('Uso: build-brasa-live-prototype.py [caminho-da-iso-de-saida]')
OUTPUT = Path(sys.argv[1]).resolve() if len(sys.argv) == 2 else ROOT / '.build/Brasa-live-experimental.iso'
CACHE = ROOT / '.build/brasa-pkg-cache.tar'

def read_rr(image, path):
    data = io.BytesIO()
    image.get_file_from_iso_fp(data, rr_path=path)
    return data.getvalue()

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
        rc_conf = read_rr(image, '/etc/rc.conf') + b'\ntmpsize="3g"\nvarsize="1g"\n'
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
            image.add_file(str(temp / 'rc.local'), iso_path='/ETC/RC.LOCAL;1', rr_name='rc.local')
            image.add_file(str(temp / 'rc.conf'), iso_path='/ETC/RC.CONF;1', rr_name='rc.conf')
            image.add_file(str(package), iso_path='/BRASA/BRASA_PROJECT_TAR_GZ;1', rr_name='BRASA_PROJECT_TAR_GZ')
            image.add_file(str(ROOT / 'scripts/brasa-live-start'), iso_path='/BRASA/BRASA_LIVE_START;1', rr_name='brasa-live-start')
            if CACHE.is_file():
                with tarfile.open(CACHE, 'r:') as cache:
                    for member in cache:
                        path = Path(member.name)
                        if path.is_absolute() or '..' in path.parts or path.parts[:2] not in (('cache', 'pkg'), ('db', 'pkg')):
                            raise RuntimeError(f'Caminho inesperado no cache: {member.name}')
                        if member.issym() and ('/' in member.linkname or '..' in member.linkname):
                            raise RuntimeError(f'Link inesperado no cache: {member.name}')
                image.add_file(str(CACHE), iso_path='/BRASA/BRASA_PKG_CACHE_TAR;1', rr_name='BRASA_PKG_CACHE_TAR')
            image.write(str(OUTPUT))
    finally:
        image.close()
    check = pycdlib.PyCdlib()
    check.open(str(OUTPUT))
    try:
        if not check.eltorito_boot_catalog:
            raise RuntimeError('O catálogo de boot foi perdido.')
        for path in ('/etc/rc.local', '/brasa/brasa-live-start', '/brasa/BRASA_PROJECT_TAR_GZ'):
            if check.get_record(rr_path=path).data_length == 0:
                raise RuntimeError(f'Arquivo vazio na ISO: {path}')
    finally:
        check.close()
    print(f'ISO experimental criada: {OUTPUT}')
    print(f'Tamanho: {OUTPUT.stat().st_size:,} bytes')

if __name__ == '__main__':
    main()
