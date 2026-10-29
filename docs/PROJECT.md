# Product direction

Brasa is a graphical x86-64 operating system fork based on Kubuntu. Development restarts from the unmodified Kubuntu 26.04.1 LTS desktop image. The earlier FreeBSD prototype is archived as historical context only; its build system, installer, drivers, and audio implementation are not the basis for Brasa.

## Goals

- Preserve a familiar KDE Plasma desktop and a straightforward graphical installation.
- Add Brasa capabilities gradually without destabilizing installation or first boot.
- Make class-compliant USB audio devices easy to discover, select, diagnose, and use.
- Explore multi-device audio aggregation with transparent latency and clock-drift behavior.
- Keep optional Brasa additions installable after setup through a guided graphical application while they mature.
- Maintain a clear, tested compatibility record rather than claiming universal device or Windows application support.

## Architecture direction

- **Base:** Kubuntu 26.04.1 LTS amd64, with Linux kernel and Ubuntu package archive.
- **Desktop:** KDE Plasma from Kubuntu.
- **Hardware audio:** ALSA kernel drivers, including upstream USB audio support, provide device access. PipeWire and WirePlumber provide routing and session policy.
- **Audio aggregation:** evaluate PipeWire's combine-stream functionality only after baseline devices work. Independent device clocks need drift correction/resampling and can still have differing latency or phase.
- **Windows applications:** not in the initial Kubuntu fork milestone. Any later compatibility layer must have app-by-app test evidence and cannot run Windows kernel drivers.
- **Brasa features:** separate packages/configuration overlays, initially opt-in after installation. Keep a rollback path and avoid changing the base installer until the additions are proven.

## Milestones

1. Verify the official unmodified Kubuntu image, checksum, live desktop, and installer baseline.
2. Record ALSA/PipeWire device discovery for built-in audio, HDMI, and available USB class-compliant interfaces.
3. Build a small Brasa audio control and diagnostics tool using supported Linux interfaces.
4. Test routing, formats, channel maps, hotplug, suspend/resume, and application coexistence.
5. Prototype multi-interface aggregation; measure latency, xruns, and long-run drift with physical devices.
6. Package the stable extras behind a guided post-install application.
7. Only then produce a branded install image, test upgrades and recovery, and publish documented builds.

## Current evidence

The official Kubuntu 26.04.1 ISO is downloaded locally and its SHA-256 matches the official checksum. A QEMU TCG boot reached the Kubuntu splash screen; the live desktop has not yet been confirmed. No Brasa modifications have been applied to the ISO. See [`docs/KUBUNTU-FORK.md`](KUBUNTU-FORK.md) and [`docs/USB-AUDIO.md`](USB-AUDIO.md).
