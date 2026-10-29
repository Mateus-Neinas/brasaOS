# Brasa as a Kubuntu fork

## Upstream baseline

Brasa starts from the official Kubuntu 26.04.1 LTS amd64 desktop image. This keeps the KDE Plasma desktop, Ubuntu package archive, Linux kernel, installer, and hardware support from a known upstream baseline. The local upstream image and its checksum are recorded in the repository README; the ISO itself is excluded from Git.

Kubuntu is a community flavor of Ubuntu, and its source packages are published under their respective licenses. “Open source” describes source availability and license rights, not a guarantee that every firmware blob, codec, font, or package in a distributable image is free software. Each added or redistributed component must be checked under its own license.

## Fork workflow

1. Keep the original Kubuntu image immutable as the baseline.
2. Boot and record the unmodified live image and installer behavior.
3. Make Brasa changes as small, reviewable packages or configuration overlays.
4. Keep the standard Kubuntu installation path unchanged while features are experimental.
5. Offer early Brasa features through an optional post-installation setup app; only integrate them into the default image after repeated installation and upgrade tests.
6. Build a reproducible respun image from documented inputs, then test boot, installation, first login, updates, and rollback before publishing it.

The earlier FreeBSD image builder and audio code are not part of this architecture and must not be copied into the Kubuntu implementation.

## Identity and publishing

Use Brasa artwork and product names for the modified system. State clearly that Brasa is based on Kubuntu/Ubuntu; do not imply that a modified image is an official Kubuntu release. Before distributing a modified ISO, review Canonical's current trademark policy and each included package's redistribution terms. Preserve required copyright and license notices.

The initial Brasa wordmark and notice are in [`../branding/`](../branding/). The detailed redistribution checklist is in [`BRANDING-COMPLIANCE.md`](BRANDING-COMPLIANCE.md). These assets do not by themselves make a modified Kubuntu ISO ready for redistribution.

## Audio design direction

The baseline uses the Linux kernel ALSA subsystem for hardware drivers, with PipeWire and WirePlumber as the desktop audio graph and policy layer. First implement reliable enumeration, selection, and diagnostics for class-compliant USB and HDMI devices using upstream components. Aggregation and clock-drift handling are separate later milestones and must be tested with physical devices; software resampling does not synchronize independent hardware clocks or guarantee phase alignment.
