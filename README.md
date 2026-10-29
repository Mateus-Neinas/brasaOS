# Brasa OS

Brasa is a private desktop operating system project based on Kubuntu. Development is restarting from a clean Kubuntu base; the earlier FreeBSD prototype has been removed from the working tree and is not used as the foundation.

## Current baseline

- Upstream: Kubuntu 26.04.1 LTS, amd64, official unmodified desktop image.
- Local base image: `dist/kubuntu-26.04.1-desktop-amd64.iso` (5,072,990,208 bytes).
- Official SHA-256 verified: `831e4d4bb85098339ba43d3502cd6619b27e76daf37246a084cd68a6413090b8`.
- A clean QEMU boot reached the Kubuntu boot splash. The live desktop has not yet been confirmed; the current TCG run is slow.
- No Brasa package, installer change, or audio modification has been applied to the upstream ISO.
- The first private Brasa image will be named `Brasa-alpha_1.1_reboot.iso`.

## Product direction

Keep the Kubuntu installer and desktop stable while building Brasa features in independent, reversible layers. The first product area is class-compliant USB audio: discovery and selection of devices, clear routing controls, and later optional aggregation of multiple devices. Extra Brasa features should be offered after installation through an optional guided app, rather than changing the installer during early development.

The goal is broad USB Audio Class support, but hardware compatibility and clock behavior must be measured. Combining devices with independent clocks can require resampling and latency compensation; it does not guarantee phase alignment or identical behavior to macOS. Details and evidence are tracked in [`docs/USB-AUDIO.md`](docs/USB-AUDIO.md).

## Project documents

- [`docs/PROJECT.md`](docs/PROJECT.md): product scope and architecture.
- [`docs/KUBUNTU-FORK.md`](docs/KUBUNTU-FORK.md): upstream, branding, licensing, and staged fork workflow.
- [`docs/BRANDING-COMPLIANCE.md`](docs/BRANDING-COMPLIANCE.md): legal/branding steps before redistributing a modified ISO.
- [`branding/`](branding/): original Brasa logo and explanatory notice (not yet applied to an image).
- [`docs/USB-AUDIO.md`](docs/USB-AUDIO.md): audio design and validation criteria.
- [`docs/LEGACY-FREEBSD.md`](docs/LEGACY-FREEBSD.md): status of the retired prototype.

## Redistribution

Brasa uses its own name and artwork and accurately identifies Kubuntu as its upstream. The project is for private use; no modified ISO is being published or attached to a GitHub release. The unmodified upstream ISO is a local build input and is not committed to Git.
