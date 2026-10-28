#!/usr/bin/env python3
"""Turn the Brasa optical ISO into a hybrid image for BIOS/UEFI USB boot."""
from __future__ import annotations

import argparse
import math
from pathlib import Path
import struct
import uuid
import zlib

import pycdlib

SECTOR = 512
GPT_ENTRY_COUNT = 128
GPT_ENTRY_SIZE = 128
GPT_TABLE_SECTORS = GPT_ENTRY_COUNT * GPT_ENTRY_SIZE // SECTOR
ALIGN = 2048
FREEBSD_BOOT = uuid.UUID("83bd6b9d-7f41-11dc-be0b-001560b84f0f")
EFI_SYSTEM = uuid.UUID("c12a7328-f81f-11d2-ba4b-00a0c93ec93b")


def align(value: int, boundary: int = ALIGN) -> int:
    return (value + boundary - 1) // boundary * boundary


def gpt_entry(type_guid: uuid.UUID, first: int, last: int, name: str) -> bytes:
    entry = bytearray(GPT_ENTRY_SIZE)
    entry[0:16] = type_guid.bytes_le
    entry[16:32] = uuid.uuid4().bytes_le
    struct.pack_into("<QQQ", entry, 32, first, last, 0)
    entry[56:128] = name.encode("utf-16le")[:72].ljust(72, b"\0")
    return bytes(entry)


def gpt_header(current: int, backup: int, first_usable: int,
               last_usable: int, disk_guid: uuid.UUID,
               table_lba: int, table_crc: int) -> bytes:
    header = bytearray(SECTOR)
    struct.pack_into(
        "<8sIIIIQQQQ16sQIII", header, 0,
        b"EFI PART", 0x00010000, 92, 0, 0, current, backup,
        first_usable, last_usable, disk_guid.bytes_le,
        table_lba, GPT_ENTRY_COUNT, GPT_ENTRY_SIZE, table_crc,
    )
    struct.pack_into("<I", header, 16, zlib.crc32(header[:92]) & 0xffffffff)
    return bytes(header)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_iso", type=Path)
    parser.add_argument("output_img", type=Path)
    args = parser.parse_args()
    source = args.source_iso.resolve()
    output = args.output_img.resolve()
    if not source.is_file():
        raise SystemExit(f"ISO não encontrada: {source}")
    if output.exists():
        raise SystemExit(f"O arquivo de saída já existe: {output}")

    image = pycdlib.PyCdlib()
    image.open(str(source))
    try:
        catalog = image.eltorito_boot_catalog
        if catalog is None or not catalog.sections:
            raise SystemExit("A ISO não contém catálogo El Torito com boot UEFI.")
        efi_entries = [entry for section in catalog.sections
                       if section.platform_id == 0xef
                       for entry in section.section_entries]
        if len(efi_entries) != 1:
            raise SystemExit("Era esperado exatamente um carregador UEFI El Torito.")
        efi_entry = efi_entries[0]
        with source.open("rb") as iso_file:
            iso_file.seek(efi_entry.load_rba * 2048)
            efi_image = iso_file.read(efi_entry.inode.data_length)
        if len(efi_image) != efi_entry.inode.data_length:
            raise SystemExit("A imagem UEFI da ISO está incompleta.")
        import io
        pmbr_buffer = io.BytesIO()
        isoboot_buffer = io.BytesIO()
        image.get_file_from_iso_fp(pmbr_buffer, rr_path="/boot/pmbr")
        image.get_file_from_iso_fp(isoboot_buffer, rr_path="/boot/isoboot")
        pmbr = pmbr_buffer.getvalue()
        isoboot = isoboot_buffer.getvalue()
    finally:
        image.close()

    if len(pmbr) != SECTOR or pmbr[510:512] != b"\x55\xaa":
        raise SystemExit("O PMBR FreeBSD não passou na verificação de tamanho/assinatura.")
    if len(isoboot) > 128 * SECTOR:
        raise SystemExit("O isoboot excede a partição FreeBSD-boot reservada.")
    if len(efi_image) % SECTOR or efi_image[:3] not in (b"\xeb\x3c\x90", b"\xe9\x00\x00"):
        raise SystemExit("A imagem UEFI El Torito não parece ser uma imagem FAT válida.")

    # El Torito ISO9660 starts at byte 0 and reserves its first 32 KiB as a
    # system area. Put the PMBR, GPT, and BIOS loader into that reserved area;
    # point the EFI partition entry at the existing El Torito FAT image.
    p1_first, p1_sectors = 34, 30
    p2_first = efi_entry.load_rba * 2048 // SECTOR
    p2_sectors = len(efi_image) // SECTOR
    if p1_first * SECTOR + len(isoboot) > 64 * 2048:
        raise SystemExit("O isoboot excede a área reservada da ISO para inicialização híbrida.")
    source_sectors = math.ceil(source.stat().st_size / SECTOR)
    disk_last = source_sectors + GPT_TABLE_SECTORS
    disk_sectors = disk_last + 1
    last_usable = disk_last - GPT_TABLE_SECTORS - 1

    entries = bytearray(GPT_ENTRY_COUNT * GPT_ENTRY_SIZE)
    entries[0:128] = gpt_entry(FREEBSD_BOOT, p1_first, p1_first + p1_sectors - 1, "FreeBSD boot")
    entries[128:256] = gpt_entry(EFI_SYSTEM, p2_first, p2_first + p2_sectors - 1, "EFI System")
    table_crc = zlib.crc32(entries) & 0xffffffff
    disk_guid = uuid.uuid4()
    primary = gpt_header(1, disk_last, 34, last_usable, disk_guid, 2, table_crc)
    backup_table_lba = disk_last - GPT_TABLE_SECTORS
    backup = gpt_header(disk_last, 1, 34, last_usable, disk_guid, backup_table_lba, table_crc)

    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with output.open("xb") as disk:
            with source.open("rb") as iso_file:
                while chunk := iso_file.read(16 * 1024 * 1024):
                    disk.write(chunk)
            disk.truncate(disk_sectors * SECTOR)
            mbr = bytearray(pmbr[:446])
            mbr.extend(b"\0" * 64)
            mbr.extend(b"\x55\xaa")
            # Protective MBR entry covering the complete image (saturated at 2 TiB).
            mbr[446:462] = struct.pack("<B3sB3sII", 0, b"\0\x02\0", 0xee,
                                      b"\xff\xff\xff", 1, min(disk_sectors - 1, 0xffffffff))
            disk.seek(0); disk.write(mbr)
            disk.seek(SECTOR); disk.write(primary)
            disk.seek(2 * SECTOR); disk.write(entries)
            disk.seek(p1_first * SECTOR); disk.write(isoboot)
            disk.seek(backup_table_lba * SECTOR); disk.write(entries)
            disk.seek(disk_last * SECTOR); disk.write(backup)
        print(f"Imagem USB criada: {output}")
        print(f"Tamanho: {output.stat().st_size:,} bytes")
        print(f"Boot BIOS em LBA {p1_first}; partição UEFI reaproveita a imagem El Torito em LBA {p2_first}.")
        print("Sistema de arquivos ISO9660 e arquivos de instalação mantidos desde LBA 0.")
    except Exception:
        output.unlink(missing_ok=True)
        raise


if __name__ == "__main__":
    main()
