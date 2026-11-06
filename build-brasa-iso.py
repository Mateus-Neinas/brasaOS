#!/usr/bin/env python3
"""Update the existing Brasa ISO in place without fetching a new FreeBSD base."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import tarfile
import tempfile
import stat

import pycdlib

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'dist' / 'Brasa-15.1-amd64.iso'
OUTPUT = ROOT / '.build' / 'Brasa-15.1-amd64.iso.new'
README = ROOT / 'README.md'
PACKAGE_PATH = '/BRASA/BRASA_PROJECT_TAR_GZ;1'
README_PATH = '/README_BRASA.TXT;1'


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def build_package(path: Path) -> None:
    with tarfile.open(path, 'w:gz') as archive:
        for folder in ('scripts', 'config', 'docs'):
            archive.add(ROOT / folder, arcname=folder)
        archive.add(README, arcname='README.md')


def add_or_replace(image: pycdlib.PyCdlib, source: Path, iso_path: str, rr_name: str) -> None:
    try:
        image.get_record(iso_path=iso_path)
    except pycdlib.pycdlibexception.PyCdlibInvalidInput:
        pass
    else:
        image.rm_file(iso_path=iso_path)
    image.add_file(str(source), iso_path=iso_path, rr_name=rr_name)


def verify(path: Path) -> None:
    image = pycdlib.PyCdlib()
    image.open(str(path))
    try:
        if image.eltorito_boot_catalog is None:
            raise RuntimeError('The rebuilt ISO lost its El Torito boot catalog.')
        if image.pvd.volume_identifier.decode().strip() != '15_1_RELEASE_AMD64_BO':
            raise RuntimeError('The rebuilt ISO volume label changed unexpectedly.')
        for iso_path in (README_PATH, PACKAGE_PATH):
            record = image.get_record(iso_path=iso_path)
            if record.data_length == 0:
                raise RuntimeError(f'Empty file in rebuilt ISO: {iso_path}')
        if image.get_record(iso_path=PACKAGE_PATH).data_length < 10_000:
            raise RuntimeError('The embedded Brasa source package is unexpectedly small.')
        if image.get_record(iso_path=README_PATH).data_length < 500:
            raise RuntimeError('The embedded Brasa guide is unexpectedly small.')
    finally:
        image.close()


def main() -> None:
    if not SOURCE.is_file():
        raise SystemExit(f'Existing Brasa ISO not found: {SOURCE}')
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='brasa-iso-') as temp_dir:
        package = Path(temp_dir) / 'brasa-project.tar.gz'
        build_package(package)

        image = pycdlib.PyCdlib()
        image.open(str(SOURCE))
        try:
            add_or_replace(image, README, README_PATH, 'README_BRASA_TXT')
            add_or_replace(image, package, PACKAGE_PATH, 'BRASA_PROJECT_TAR_GZ')
            image.write(str(OUTPUT))
        finally:
            image.close()

    verify(OUTPUT)
    # Swap only after boot metadata and replacement payloads pass verification.
    try:
        OUTPUT.chmod(stat.S_IWRITE | stat.S_IREAD)
    except OSError:
        pass
    os.replace(OUTPUT, SOURCE)
    verify(SOURCE)
    print(f'Updated existing Brasa ISO: {SOURCE}')
    print(f'Size: {SOURCE.stat().st_size:,} bytes')
    print(f'SHA-256: {sha256(SOURCE)}')
    print('El Torito boot catalog: preserved')


if __name__ == '__main__':
    main()
