# Experimental FreeBSD USB audio patch

`freebsd-15.1-uaudio-shared-clock.patch` is a candidate fix for the UAC2
shared-clock failure reported against FreeBSD 15.1 in
[FreeBSD bug 295933](https://bugs.freebsd.org/bugzilla/show_bug.cgi?id=295933).
The report reproduces when an asynchronous playback stream uses a 44.1 kHz
family rate while an idle capture endpoint, started for feedback/jitter
measurement, resets the same UAC2 Clock Source to its 48 kHz default.

The patch skips `SET_CUR` only for a clock ID that the descriptors associate
with both directions, when the channel being configured is not running and the
opposite channel is running. Other clock IDs and a genuinely active capture or
playback stream retain the existing path. It does not resolve incompatible
rates when both directions are actively streaming on one physical clock, nor
does it add missing device-specific controls or class support.

This is not applied by the bootstrap. It has not been compiled, reviewed by
FreeBSD maintainers, or tested on a USB audio device. On a disposable FreeBSD
15.1 development system with its matching `/usr/src` tree, first check and
apply it from the source tree:

```sh
cd /usr/src
patch -C -p1 < /path/to/patches/freebsd-15.1-uaudio-shared-clock.patch
patch -p1 < /path/to/patches/freebsd-15.1-uaudio-shared-clock.patch
make -C /usr/src/sys/modules/sound/driver/uaudio
```

`patch -C` checks whether the patch applies without changing files. This builds
the candidate module only; it does not install or load it. After
testing the build and deciding whether to continue, the source change can be
reverted with:

```sh
cd /usr/src
patch -R -p1 < /path/to/patches/freebsd-15.1-uaudio-shared-clock.patch
```

Do not replace the stock module on a working system before testing the built
module on disposable hardware. Preserve the stock module and a bootable kernel
so the change can be reverted.

Validation should cover UAC2 devices with a shared playback/capture clock:

- Playback at 44.1, 88.2, 176.4, and 352.8 kHz with capture idle.
- Playback at 48, 96, 192, and 384 kHz with capture idle.
- Capture-only, then playback-only, then simultaneous duplex at matching rates.
- A device with independent playback and capture clocks, to confirm unrelated
  clock programming remains unchanged.
- Repeated start/stop, hotplug, and at least one-hour playback/capture runs;
  inspect the device's lock indicator or feedback rate, `/dev/sndstat`, and
  PipeWire xrun counters.

The FreeBSD 15.1 `snd_uaudio(4)` manual documents `hw.usb.uaudio.default_rate`
as an attach-time preferred rate. A report in bug 295933 says setting it to
44100 and reattaching the affected DAC avoids the specific 44.1/48 kHz conflict,
but this is a global compromise, not a general Brasa fix: it can constrain the
available rate choice for every USB audio device.
