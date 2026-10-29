# USB audio on Brasa

## User requirement

Brasa should make USB Audio Class compliant interfaces straightforward to use, without a fixed list of supported manufacturers. Users should be able to inspect playback and capture devices, choose the desired output/input, understand channel and format capabilities, and eventually combine devices where practical. The goal is dependable behavior comparable to a polished desktop OS; parity with macOS is not established and must not be claimed without side-by-side testing.

## Kubuntu audio stack

The new baseline is Kubuntu 26.04.1 LTS. Linux ALSA drivers expose audio hardware to the system; the `snd-usb-audio` kernel driver supports many USB Audio Class devices. PipeWire provides the desktop audio graph, and WirePlumber manages device/node policy. HDMI audio depends on the graphics and audio hardware drivers as well as the selected PipeWire profile. Actual device support depends on descriptors, firmware, controls, and the upstream driver implementation.

Do not carry over the retired FreeBSD OSS/PipeWire backend or its configuration scripts. Use standard Ubuntu/Kubuntu packages and APIs first, then add a thin Brasa interface only where the desktop controls are unclear or insufficient.

## Development stages

1. **Observe:** inventory ALSA cards, PCM devices, PipeWire nodes, profiles, channels, and formats on clean Kubuntu.
2. **Select:** create clear UI for choosing existing input/output and showing availability/errors; do not replace KDE audio settings until feature parity is established.
3. **Test:** provide an actual graphical playback/recording test with explicit device selection and visible result; do not launch a terminal as the app UI.
4. **Aggregate:** evaluate PipeWire combine-stream for multiple sinks/sources. Expose member selection, channel maps, latency, and device loss clearly.
5. **Measure:** test independent hardware clocks during sustained duplex playback/capture. Resampling and latency compensation can manage drift but cannot guarantee common phase or sample-accurate synchronization.
6. **Package:** distribute the feature as an optional post-install Brasa component while it is experimental.

## Validation matrix

For each built-in, HDMI, and USB interface tested, record hardware and kernel versions, connection type, ALSA card/profile, PipeWire nodes, sample rates, channel maps, playback, capture, duplex, hotplug, suspend/resume, xruns, latency, and long-run stability. Test at least one UAC1 and UAC2 device if available, and multiple devices for aggregation. Do not infer support for UAC3 or every class-compliant device from a successful UAC1/UAC2 test.

Compare with macOS only using the same interface, rate, channel configuration, duration, and workload. Publish limits and failures alongside successful results.

## Upstream references

- [Ubuntu audio overview](https://wiki.ubuntu.com/AudioOnUbuntu)
- [PipeWire combine-stream module](https://pipewire.pages.freedesktop.org/pipewire/page_module_combine_stream.html)
- [Kubuntu 26.04 LTS release notes](https://kubuntu.org/news/kubuntu-26-04-release-notes/)
