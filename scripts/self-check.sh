#!/bin/sh
# Smoke checks using stubbed FreeBSD/Wine commands; safe on a development host.
set -eu
root=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
for file in bootstrap-freebsd.sh brasa-audio-select brasa-audio-aggregate brasa-audio-start brasa-audio-status brasa-audio-monitor brasa-audio-test brasa-run-windows brasa-windows-import brasa-apply-theme brasa-live-start brasa-install-assistant; do
  sh -n "$root/scripts/$file"
done
if grep -q '/dev/ttyu0' "$root/scripts/brasa-live-start" "$root/scripts/brasa-install-assistant"; then
  echo 'Live startup and installer must not open a serial TTY directly.' >&2
  exit 1
fi
grep -q "say 'Montando o espaço temporário dos componentes gráficos.'" "$root/scripts/brasa-live-start"
grep -q "say 'Espaço temporário pronto.'" "$root/scripts/brasa-live-start"
grep -q 'service devmatch onestart' "$root/scripts/brasa-live-start"
grep -q 'do not auto-start the optional Bluetooth stack' "$root/scripts/build-brasa-live-prototype.py"
grep -q "media:.*Ethernet" "$root/scripts/brasa-live-start"
grep -q 'dhclient -b' "$root/scripts/brasa-live-start"
grep -q "realtek-rge-kmod" "$root/scripts/build-brasa-live-prototype.py"
grep -q 'BRASA_LIVE_PKG_ARCHIVES' "$root/scripts/brasa-live-start"
grep -q 'BRASA_LIVE_PKG_ARCHIVES' "$root/scripts/build-brasa-live-prototype.py"
grep -q 'if_rge_load="YES"' "$root/scripts/bootstrap-freebsd.sh"
grep -q 'install -m 0755 scripts/brasa-audio-monitor /usr/local/bin/brasa-audio-monitor' "$root/scripts/bootstrap-freebsd.sh"
grep -q 'install -m 0644 config/brasa-audio-monitor.desktop /usr/local/share/applications/brasa-audio-monitor.desktop' "$root/scripts/bootstrap-freebsd.sh"
grep -q '^Exec=/usr/local/bin/brasa-audio-monitor$' "$root/config/brasa-audio-monitor.desktop"
work=$(mktemp -d "${TMPDIR:-/tmp}/brasa-check.XXXXXX")
trap 'rm -rf "$work"' EXIT HUP INT TERM
mkdir -p "$work/bin" "$work/home"
cat > "$work/bin/zenity" <<'STUB'
#!/bin/sh
case "$1" in
  --question) [ "${BRASA_AUDIO_REMOVE:-0}" = 1 ] ;;
  --list)
    cat > "$BRASA_ZENITY_LOG"
    case "${BRASA_DIRECTION_ONLY:-}:$*" in
      capture:*"Saidas agregadas"*|capture:*"Tolerancia a variacoes"*|playback:*"Entradas agregadas"*)
        echo 'unexpected dialog for unavailable direction' >&2; exit 1 ;;
    esac
    case "$*" in
      *"Audio Brasa"*) printf '%s\n' "${BRASA_ZENITY_SELECTION:-1}" ;;
      *"Saidas agregadas"*) if [ "${BRASA_WPCTL_RENUMBER:-0}" = 1 ]; then printf 'pcm0.play|pcm2.play\n'; elif [ "${BRASA_WPCTL_DUPLICATE_LABEL:-0}" = 1 ]; then printf 'pcm1.play\n'; else printf 'pcm0.play|pcm1.play\n'; fi ;;
      *"Entradas agregadas"*) if [ "${BRASA_CAPTURE_WIDTH:-0}" = 32 ] && [ "${BRASA_CAPTURE_OVERFLOW:-0}" = 0 ]; then printf 'pcm0.rec|pcm1.rec\n'; elif [ "${BRASA_WPCTL_RENUMBER:-0}" = 1 ]; then printf 'pcm0.rec|pcm2.rec|pcm3.rec\n'; elif [ "${BRASA_WPCTL_DUPLICATE_LABEL:-0}" = 1 ]; then printf 'pcm0.rec\n'; else printf 'pcm0.rec|pcm1.rec|pcm3.rec\n'; fi ;;
      *"Mestre de sincronismo"*) printf '%s\n' "${BRASA_MASTER_SELECTION:-pcm0.play}" ;;
      *"Tolerancia a variacoes"*) printf '%s\n' "${BRASA_OSS_DELAY:-16}" ;;
      *"Fragmento do dispositivo"*) printf '%s\n' "${BRASA_OSS_FRAGMENT:-0}" ;;
      *) printf '1\n' ;;
    esac ;;
  --info) exit 0 ;;
  --error) echo "$*" >&2; exit 1 ;;
  *) exit 0 ;;
esac
STUB
cat > "$work/bin/sysctl" <<'STUB'
#!/bin/sh
if [ "$1" = "-n" ]; then echo 0
elif [ "$1" = "-a" ]; then echo 'dev.pcm.1.feedback_rate: 48001'
else exit 0; fi
STUB
cat > "$work/bin/kdesu" <<'STUB'
#!/bin/sh
printf '%s\n' "$*" > "$BRASA_KDESU_LOG"
STUB
cat > "$work/bin/pw-cli" <<'STUB'
#!/bin/sh
exit 0
STUB
cat > "$work/bin/pw-top" <<'STUB'
#!/bin/sh
case "$*" in
  *--iterations=1) printf 'S ID  QUANT RATE WAIT  BUSY W/Q B/Q ERR FORMAT NAME\nR 45  1024 48000 0.1  0.2 0.1 0.2 3   S16 2 48000 pcm0.play\nR 46  1024 48000 0.1  0.2 0.1 0.2 5   S16 2 48000 + pcm1.play\n' ;;
  *)
    i=0
    while [ "$i" -lt "${BRASA_MONITOR_SECONDS:-5}" ]; do
      printf 'S ID  QUANT RATE WAIT  BUSY W/Q B/Q ERR FORMAT NAME\n'
      errors=3; [ "$i" -lt 2 ] || errors=4
      [ "${BRASA_MONITOR_CLEAN:-0}" != 1 ] || errors=3
      if [ "${BRASA_MONITOR_RESET:-0}" = 1 ]; then
        errors=5; [ "$i" -ne 1 ] || errors=0
      fi
      node_id=45
      if [ "${BRASA_MONITOR_RECREATE:-0}" = 1 ] && [ "$i" -ge 2 ]; then node_id=55; fi
      state=R; [ "${BRASA_MONITOR_IDLE:-0}" = 1 ] && state=I
      master_name=pcm1.play; [ "${BRASA_MONITOR_MASTER_FOLLOWER:-0}" = 1 ] && master_name='= pcm1.play'
      if [ "${BRASA_MONITOR_GAP:-0}" != 1 ] || [ "$i" -ne 2 ]; then
        printf '%s %s  1024 48000 0.1  0.2 0.1 0.2 %s   S16 2 48000 + pcm0.play\n' "$state" "$node_id" "$errors"
      fi
      printf '%s 46  1024 48000 0.1  0.2 0.1 0.2 5   S16 2 48000 %s\n' "$state" "$master_name"
      i=$((i + 1))
    done
    ;;
esac
STUB
cat > "$work/bin/dmesg" <<'STUB'
printf 'uaudio0: USB Audio Class device attached\n'
STUB
cat > "$work/bin/mixer" <<'STUB'
printf 'mixer0: pcm volume 100:100\n'
STUB
cat > "$work/bin/mv" <<'STUB'
#!/bin/sh
case "${BRASA_FAIL_RULE_MV:-0}:$2" in
  1:*90-brasa-clock-master.conf)
    if [ ! -e "$BRASA_MV_FAILED" ]; then : > "$BRASA_MV_FAILED"; exit 1; fi ;;
  2:*90-brasa-clock-master.conf.remove.*)
    if [ ! -e "$BRASA_MV_FAILED" ]; then : > "$BRASA_MV_FAILED"; exit 1; fi ;;
esac
command -p mv "$@"
STUB
cat > "$work/bin/wpctl" <<'STUB'
#!/bin/sh
if [ "$1" = "set-default" ]; then
  printf '%s\n' "$2" > "$BRASA_WPCTL_LOG"
  exit 0
fi
if [ "$1" = "inspect" ]; then
  if [ "${BRASA_CAPTURE_WIDTH:-0}" = 32 ]; then
    case "$2" in
      47|48)
        if [ "$2" = 47 ]; then name=pcm0.rec; else name=pcm1.rec; fi
        printf 'node.name = "%s"\nmedia.class = "Audio/Source"\nnode.description = "32-channel %s"\naudio.position = "[ FL FR' "$name" "$name"
        aux=0
        while [ "$aux" -lt 30 ]; do printf ' AUX%s' "$aux"; aux=$((aux + 1)); done
        printf ' ]"\n'
        exit 0 ;;
    esac
  fi
  case "$2" in
    45) printf 'node.name = "pcm0.play"\nmedia.class = "Audio/Sink"\nnode.description = "Internal Audio"\naudio.position = "[ FL, FR ]"\n' ;;
    46) printf 'node.name = "pcm1.play"\nmedia.class = "Audio/Sink"\nnode.description = "USB Studio Interface @ usb0:1.2"\naudio.position = "[ FL, FR ]"\n' ;;
    47) printf 'node.name = "pcm0.rec"\nmedia.class = "Audio/Source"\nnode.description = "Internal Capture"\naudio.position = "[ FL, FR ]"\n' ;;
    48) printf 'node.name = "pcm1.rec"\nmedia.class = "Audio/Source"\nnode.description = "USB Studio Interface @ usb0:1.2"\naudio.position = "[ FL, FR, FC, LFE, SL, SR ]"\n' ;;
    52) printf 'node.name = "pcm2.rec"\nmedia.class = "Audio/Source"\nnode.description = "USB Studio Capture @ usb0:1.2"\naudio.position = "[ FL, FR, FC, LFE, SL, SR ]"\n' ;;
    53) printf 'node.name = "pcm3.rec"\nmedia.class = "Audio/Source"\nnode.description = "Mono Mic @ usb0:1.7"\naudio.position = "[ MONO ]"\n' ;;
    50) printf 'node.name = "pcm2.play"\nmedia.class = "Audio/Sink"\nnode.description = "USB Studio Interface @ usb0:1.2"\naudio.position = "[ FL, FR ]"\n' ;;
    54) printf 'node.name = "pcm4.play"\nmedia.class = "Audio/Sink"\nnode.description = "USB Studio Interface @ usb0:1.2"\naudio.position = "[ FL, FR ]"\n' ;;
  esac
  if [ "${BRASA_STATUS_MASTER_ID:-}" = "$2" ]; then printf 'priority.driver = 1000000\n'; fi
  if [ "${BRASA_STATUS_FRAGMENT_ID:-}" = "$2" ]; then printf 'oss.fragment = %s\n' "${BRASA_STATUS_FRAGMENT:-4096}"; fi
  exit 0
fi
if [ "${BRASA_WPCTL_NO_PCM:-0}" = 1 ]; then
  cat <<'STATUS'
Audio
 ├─ Sinks:
 │  * 49. Brasa aggregate output (brasa.aggregate.output) [vol: 1.00]
 ├─ Sources:
STATUS
  exit 0
fi
if [ "${BRASA_STATUS_USB_ABSENT:-0}" = 1 ]; then
  cat <<'STATUS'
Audio
 ├─ Sinks:
 │  * 45. FreeBSD OSS pcm0.play [vol: 1.00]
 ├─ Sources:
 │  * 47. FreeBSD OSS pcm0.rec [vol: 1.00]
 ├─ Filters:
STATUS
  exit 0
fi
if [ "${BRASA_WPCTL_RENUMBER:-0}" = 1 ]; then
  cat <<'STATUS'
Audio
 ├─ Sinks:
 │  * 45. FreeBSD OSS pcm0.play [vol: 1.00]
 │    50. FreeBSD OSS pcm2.play [vol: 1.00]
 │    49. Brasa aggregate output (brasa.aggregate.output) [vol: 1.00]
 ├─ Sources:
 │  * 47. FreeBSD OSS pcm0.rec [vol: 1.00]
 │    52. FreeBSD OSS pcm2.rec [vol: 1.00]
 │    53. FreeBSD OSS pcm3.rec [vol: 1.00]
 ├─ Filters:
STATUS
  exit 0
fi
if [ -n "${BRASA_DIRECTION_ONLY:-}" ]; then
  printf 'Audio\n Sinks:\n'
  if [ "$BRASA_DIRECTION_ONLY" = playback ]; then
    printf ' 45. pcm0.play\n 46. pcm1.play\n'
  fi
  printf ' Sources:\n'
  if [ "$BRASA_DIRECTION_ONLY" = capture ]; then
    printf ' 47. pcm0.rec\n 48. pcm1.rec\n 53. pcm3.rec\n'
  fi
  printf ' Filters:\n'
  exit 0
fi
if [ "${BRASA_WPCTL_DUPLICATE_LABEL:-0}" = 1 ]; then
  cat <<'STATUS'
Audio
 ├─ Sinks:
 │  * 45. FreeBSD OSS pcm0.play [vol: 1.00]
 │    46. FreeBSD OSS pcm1.play [vol: 1.00]
 │    54. FreeBSD OSS pcm4.play [vol: 1.00]
 │    49. Brasa aggregate output (brasa.aggregate.output) [vol: 1.00]
 ├─ Sources:
 │  * 47. FreeBSD OSS pcm0.rec [vol: 1.00]
 │    48. FreeBSD OSS pcm1.rec [vol: 1.00]
 │    53. FreeBSD OSS pcm3.rec [vol: 1.00]
 ├─ Filters:
STATUS
  exit 0
fi
cat <<'STATUS'
Audio
 ├─ Sinks:
 │  * 45. FreeBSD OSS pcm0.play [vol: 1.00]
 │    46. FreeBSD OSS pcm1.play [vol: 1.00]
 │    49. Brasa aggregate output (brasa.aggregate.output) [vol: 1.00]
 ├─ Sources:
 │  * 47. FreeBSD OSS pcm0.rec [vol: 1.00]
 │    48. FreeBSD OSS pcm1.rec [vol: 1.00]
 │    53. FreeBSD OSS pcm3.rec [vol: 1.00]
 ├─ Filters:
STATUS
STUB
cat > "$work/bin/sox" <<'STUB'
#!/bin/sh
for arg do output=$arg; done
: > "$output"
STUB
cat > "$work/bin/pw-play" <<'STUB'
#!/bin/sh
printf '%s\n' "$*" > "$BRASA_PW_PLAY_LOG"
STUB
cat > "$work/bin/pkill" <<'STUB'
#!/bin/sh
exit 1
STUB
cat > "$work/bin/wineboot" <<'STUB'
#!/bin/sh
[ -n "$WINEPREFIX" ]
STUB
cat > "$work/bin/wine" <<'STUB'
#!/bin/sh
printf '%s\n' "$*" > "$BRASA_WINE_LOG"
STUB
chmod +x "$work/bin/"*
cat > "$work/sndstat" <<'SND'
Installed devices:
pcm0: <Internal Audio> (play/rec)
pcm1: <USB Studio Interface> (play/rec) default
SND
: > "$work/installer.exe"
PATH="$work/bin:$PATH"
export PATH HOME="$work/home"
export BRASA_SNDSTAT="$work/sndstat"
export BRASA_ZENITY_LOG="$work/zenity.log"
export BRASA_KDESU_LOG="$work/kdesu.log"
export BRASA_WPCTL_LOG="$work/wpctl.log"
export BRASA_WINE_LOG="$work/wine.log"
export BRASA_PW_PLAY_LOG="$work/pw-play.log"
export BRASA_MV_FAILED="$work/mv-failed"
export XDG_CONFIG_HOME="$work/config"
sh "$root/scripts/brasa-audio-select"
grep -q '1[[:space:]]Saida padrao atual[[:space:]]<USB Studio Interface>' "$work/zenity.log"
grep -qx '46' "$work/wpctl.log"
grep -q 'pw:49[[:space:]]Saida virtual Brasa[[:space:]]Agregado Brasa' "$work/zenity.log"
BRASA_ZENITY_SELECTION=pw:49 sh "$root/scripts/brasa-audio-select"
grep -qx '49' "$work/wpctl.log"
if BRASA_WPCTL_NO_PCM=1 sh "$root/scripts/brasa-audio-select" >/dev/null 2>&1; then
  echo 'ERROR: missing PipeWire PCM node silently changed the kernel default.' >&2; exit 1
fi
BRASA_DIRECTION_ONLY=capture BRASA_MASTER_SELECTION=pcm1.rec sh "$root/scripts/brasa-audio-aggregate"
grep -q 'node.name = "brasa.aggregate.input"' "$XDG_CONFIG_HOME/pipewire/pipewire.conf.d/90-brasa-aggregate.conf"
if grep -q 'brasa.aggregate.output' "$XDG_CONFIG_HOME/pipewire/pipewire.conf.d/90-brasa-aggregate.conf"; then
  echo 'ERROR: capture-only aggregate created an output.' >&2; exit 1
fi
grep -q 'media.class = "Audio/Source".*priority.driver = 1000000' "$XDG_CONFIG_HOME/wireplumber/wireplumber.conf.d/90-brasa-clock-master.conf"
if grep -q 'oss.delay' "$XDG_CONFIG_HOME/wireplumber/wireplumber.conf.d/90-brasa-clock-master.conf"; then
  echo 'ERROR: capture-only aggregate configured a playback buffer.' >&2; exit 1
fi
BRASA_DIRECTION_ONLY=playback sh "$root/scripts/brasa-audio-aggregate"
grep -q 'node.name = "brasa.aggregate.output"' "$XDG_CONFIG_HOME/pipewire/pipewire.conf.d/90-brasa-aggregate.conf"
if grep -q 'brasa.aggregate.input' "$XDG_CONFIG_HOME/pipewire/pipewire.conf.d/90-brasa-aggregate.conf"; then
  echo 'ERROR: playback-only aggregate created an input.' >&2; exit 1
fi
sh "$root/scripts/brasa-audio-aggregate"
grep -q 'node.name = "brasa.aggregate.output"' "$XDG_CONFIG_HOME/pipewire/pipewire.conf.d/90-brasa-aggregate.conf"
grep -q 'node.name = "brasa.aggregate.input"' "$XDG_CONFIG_HOME/pipewire/pipewire.conf.d/90-brasa-aggregate.conf"
[ "$(grep -c 'combine.latency-compensate = true' "$XDG_CONFIG_HOME/pipewire/pipewire.conf.d/90-brasa-aggregate.conf")" -eq 2 ]
grep -q 'audio.position = \[ FL FR AUX0 AUX1 AUX2 AUX3 AUX4 AUX5 AUX6 \]' "$XDG_CONFIG_HOME/pipewire/pipewire.conf.d/90-brasa-aggregate.conf" || { cat "$XDG_CONFIG_HOME/pipewire/pipewire.conf.d/90-brasa-aggregate.conf" >&2; exit 1; }
grep -q 'audio.position = \[ FL FR FC LFE SL SR \].*combine.audio.position = \[ AUX0 AUX1 AUX2 AUX3 AUX4 AUX5 \]' "$XDG_CONFIG_HOME/pipewire/pipewire.conf.d/90-brasa-aggregate.conf"
grep -q 'audio.position = \[ FL FR AUX0 AUX1 AUX2 AUX3 AUX4 AUX5 AUX6 \]' "$XDG_CONFIG_HOME/pipewire/pipewire.conf.d/90-brasa-aggregate.conf"
grep -q 'node.name = "pcm0.play".*priority.driver = 1000000' "$XDG_CONFIG_HOME/wireplumber/wireplumber.conf.d/90-brasa-clock-master.conf"
grep -q 'node.name = "pcm0.play" media.class = "Audio/Sink".*priority.driver = 1000000' "$XDG_CONFIG_HOME/wireplumber/wireplumber.conf.d/90-brasa-clock-master.conf"
grep -q 'node.name = "pcm0.rec" media.class = "Audio/Source".*priority.driver = 999999' "$XDG_CONFIG_HOME/wireplumber/wireplumber.conf.d/90-brasa-clock-master.conf"
grep -q 'node.description = "Mono Mic @ usb0:1.7" media.class = "Audio/Source".*priority.driver = 100' "$XDG_CONFIG_HOME/wireplumber/wireplumber.conf.d/90-brasa-clock-master.conf"
grep -q 'node.name = "pcm0.play" media.class = "Audio/Sink".*priority.driver = 1000000 oss.delay = 16 oss.fragment = 0' "$XDG_CONFIG_HOME/wireplumber/wireplumber.conf.d/90-brasa-clock-master.conf"
grep -q 'node.description = "USB Studio Interface @ usb0:1.2" media.class = "Audio/Sink".*priority.driver = 100 oss.delay = 16 oss.fragment = 0' "$XDG_CONFIG_HOME/wireplumber/wireplumber.conf.d/90-brasa-clock-master.conf"
grep -q 'node.description = "USB Studio Interface @ usb0:1.2" media.class = "Audio/Sink".*priority.driver = 100' "$XDG_CONFIG_HOME/wireplumber/wireplumber.conf.d/90-brasa-clock-master.conf"
grep -q 'node.description = "USB Studio Interface @ usb0:1.2"' "$XDG_CONFIG_HOME/pipewire/pipewire.conf.d/90-brasa-aggregate.conf"
BRASA_DIRECTION_ONLY=capture BRASA_CAPTURE_WIDTH=32 BRASA_MASTER_SELECTION=pcm1.rec sh "$root/scripts/brasa-audio-aggregate"
awk '
  /combine.props/ {
    sub(/^.*audio.position = \[ /, ""); sub(/ \].*$/, "")
    if (NF != 64) exit 1
    for (i=1; i<=NF; i++) if (seen[$i]++) exit 1
    found=1
  }
  END { if (!found) exit 1 }
' "$XDG_CONFIG_HOME/pipewire/pipewire.conf.d/90-brasa-aggregate.conf"
grep -q 'combine.audio.position = \[ AUX30 .* AUX61 \]' "$XDG_CONFIG_HOME/pipewire/pipewire.conf.d/90-brasa-aggregate.conf"
cp "$XDG_CONFIG_HOME/pipewire/pipewire.conf.d/90-brasa-aggregate.conf" "$work/aggregate.before-overflow"
cp "$XDG_CONFIG_HOME/wireplumber/wireplumber.conf.d/90-brasa-clock-master.conf" "$work/master.before-overflow"
if BRASA_DIRECTION_ONLY=capture BRASA_CAPTURE_WIDTH=32 BRASA_CAPTURE_OVERFLOW=1 BRASA_MASTER_SELECTION=pcm1.rec sh "$root/scripts/brasa-audio-aggregate" >"$work/overflow.log" 2>&1; then
  echo 'ERROR: 65-channel aggregate exceeded the supported channel count.' >&2; exit 1
fi
grep -q '64 canais' "$work/overflow.log"
cmp -s "$work/aggregate.before-overflow" "$XDG_CONFIG_HOME/pipewire/pipewire.conf.d/90-brasa-aggregate.conf"
cmp -s "$work/master.before-overflow" "$XDG_CONFIG_HOME/wireplumber/wireplumber.conf.d/90-brasa-clock-master.conf"
for candidate in "$XDG_CONFIG_HOME/pipewire/pipewire.conf.d/"*.conf; do
  [ "$candidate" = "$XDG_CONFIG_HOME/pipewire/pipewire.conf.d/90-brasa-aggregate.conf" ] || { echo 'ERROR: failed generation left a loadable partial config.' >&2; exit 1; }
done
sh "$root/scripts/brasa-audio-aggregate"
BRASA_AUDIO_REMOVE=0 BRASA_OSS_FRAGMENT=4096 sh "$root/scripts/brasa-audio-aggregate"
grep -q 'node.name = "pcm0.play" media.class = "Audio/Sink".*oss.fragment = 4096' "$XDG_CONFIG_HOME/wireplumber/wireplumber.conf.d/90-brasa-clock-master.conf"
grep -q 'node.name = "pcm0.rec" media.class = "Audio/Source".*oss.fragment = 4096' "$XDG_CONFIG_HOME/wireplumber/wireplumber.conf.d/90-brasa-clock-master.conf"
BRASA_AUDIO_REMOVE=0 sh "$root/scripts/brasa-audio-aggregate"
BRASA_WPCTL_DUPLICATE_LABEL=1 BRASA_MASTER_SELECTION=pcm1.play sh "$root/scripts/brasa-audio-aggregate"
grep -q 'matches = \[ { node.name = "pcm1.play" media.class = "Audio/Sink" } \]' "$XDG_CONFIG_HOME/pipewire/pipewire.conf.d/90-brasa-aggregate.conf"
BRASA_AUDIO_REMOVE=0 sh "$root/scripts/brasa-audio-aggregate"
BRASA_AUDIO_REMOVE=0 BRASA_MASTER_SELECTION=pcm1.rec sh "$root/scripts/brasa-audio-aggregate"
grep -q 'node.description = "USB Studio Interface @ usb0:1.2" media.class = "Audio/Source".*priority.driver = 1000000' "$XDG_CONFIG_HOME/wireplumber/wireplumber.conf.d/90-brasa-clock-master.conf"
grep -q 'node.description = "USB Studio Interface @ usb0:1.2" media.class = "Audio/Sink".*priority.driver = 999999 oss.delay = 16 oss.fragment = 0' "$XDG_CONFIG_HOME/wireplumber/wireplumber.conf.d/90-brasa-clock-master.conf"
BRASA_AUDIO_REMOVE=0 BRASA_WPCTL_RENUMBER=1 BRASA_MASTER_SELECTION=pcm2.play sh "$root/scripts/brasa-audio-aggregate"
grep -q 'node.description = "USB Studio Interface @ usb0:1.2".*priority.driver = 1000000' "$XDG_CONFIG_HOME/wireplumber/wireplumber.conf.d/90-brasa-clock-master.conf"
grep -q 'node.description = "USB Studio Interface @ usb0:1.2" media.class = "Audio/Sink".*priority.driver = 1000000 oss.delay = 16 oss.fragment = 0' "$XDG_CONFIG_HOME/wireplumber/wireplumber.conf.d/90-brasa-clock-master.conf"
grep -q 'node.description = "USB Studio Capture @ usb0:1.2" media.class = "Audio/Source".*priority.driver = 999999 oss.fragment = 0' "$XDG_CONFIG_HOME/wireplumber/wireplumber.conf.d/90-brasa-clock-master.conf"
grep -q 'node.description = "USB Studio Interface @ usb0:1.2"' "$XDG_CONFIG_HOME/pipewire/pipewire.conf.d/90-brasa-aggregate.conf"
sh "$root/scripts/brasa-audio-test"
grep -q -- '--target brasa.aggregate.output' "$work/pw-play.log"
BRASA_STATUS_USB_ABSENT=1 BRASA_SNDSTAT="$BRASA_SNDSTAT" sh "$root/scripts/brasa-audio-status" > "$work/audio-status.log"
grep -q 'dev.pcm.1.feedback_rate: 48001' "$work/audio-status.log"
grep -q 'PipeWire runtime statistics (including xruns/errors)' "$work/audio-status.log"
grep -q '3   S16 2 48000 pcm0.play' "$work/audio-status.log"
grep -q 'Physical PCM driver row(s) reported by pw-top' "$work/audio-status.log"
if awk '/Physical PCM driver row/ { drivers=1; next } /USB audio attach/ { drivers=0 } drivers' "$work/audio-status.log" | grep -q 'pcm1.play'; then
  echo 'ERROR: status classified a follower as a physical driver.' >&2; exit 1
fi
grep -q 'Configured clock master is not present in the current PipeWire graph' "$work/audio-status.log"
BRASA_SNDSTAT="$BRASA_SNDSTAT" sh "$root/scripts/brasa-audio-status" > "$work/audio-status-master-pending.log"
grep -q 'Configured clock master is connected, but the configured priority is not present on its node' "$work/audio-status-master-pending.log"
BRASA_STATUS_MASTER_ID=46 BRASA_SNDSTAT="$BRASA_SNDSTAT" sh "$root/scripts/brasa-audio-status" > "$work/audio-status-master-returned.log"
grep -q 'Configured clock master is connected and has the configured high driver priority; this does not prove it is driving the active graph' "$work/audio-status-master-returned.log"
BRASA_STATUS_FRAGMENT_ID=46 BRASA_STATUS_FRAGMENT=4096 BRASA_SNDSTAT="$BRASA_SNDSTAT" sh "$root/scripts/brasa-audio-status" > "$work/audio-status-fragment.log"
grep -q 'oss.fragment = 4096 (valor efetivo reportado pelo OSS-ng)' "$work/audio-status-fragment.log"
BRASA_AUDIO_REMOVE=0 BRASA_MASTER_SELECTION=pcm1.play sh "$root/scripts/brasa-audio-aggregate"
BRASA_MONITOR_SECONDS=10 sh "$root/scripts/brasa-audio-monitor" > "$work/audio-monitor.log"
grep -q 'pcm0.play: 1 xrun/erro novo(s)' "$work/audio-monitor.log"
grep -q 'pcm0.play:.*driver/seguidora 0/10' "$work/audio-monitor.log"
grep -q 'formato reportado S16 2 @ 48000-48000 Hz' "$work/audio-monitor.log"
grep -q 'Foram observados novos xruns/erros' "$work/audio-monitor.log"
grep -q 'Mestre configurado ativo em 10 amostra(s); foi driver do grafo em 10 amostra(s) e seguidor em 0.' "$work/audio-monitor.log"
BRASA_MONITOR_SECONDS=10 BRASA_MONITOR_MASTER_FOLLOWER=1 sh "$root/scripts/brasa-audio-monitor" > "$work/audio-monitor-master-following.log"
grep -q 'mestre configurado apareceu como seguidor, não como driver do grafo' "$work/audio-monitor-master-following.log"
BRASA_MONITOR_SECONDS=10 BRASA_MONITOR_IDLE=1 sh "$root/scripts/brasa-audio-monitor" > "$work/audio-monitor-idle.log"
grep -q 'Inconclusivo: nenhum PCM esteve em execução' "$work/audio-monitor-idle.log"
BRASA_MONITOR_SECONDS=10 BRASA_MONITOR_CLEAN=1 sh "$root/scripts/brasa-audio-monitor" > "$work/audio-monitor-clean.log"
grep -q 'Nenhum aumento de xrun/erro' "$work/audio-monitor-clean.log"
BRASA_MONITOR_SECONDS=10 BRASA_MONITOR_RESET=1 sh "$root/scripts/brasa-audio-monitor" > "$work/audio-monitor-reset.log"
grep -q 'pcm0.play: 5 xrun/erro novo(s) nos intervalos comparáveis' "$work/audio-monitor-reset.log"
grep -q 'contador reiniciou durante a observação' "$work/audio-monitor-reset.log"
BRASA_MONITOR_SECONDS=10 BRASA_MONITOR_RECREATE=1 sh "$root/scripts/brasa-audio-monitor" > "$work/audio-monitor-recreate.log"
grep -q 'ID do nó mudou durante a observação' "$work/audio-monitor-recreate.log"
BRASA_MONITOR_SECONDS=10 BRASA_MONITOR_GAP=1 sh "$root/scripts/brasa-audio-monitor" > "$work/audio-monitor-gap.log"
grep -q 'ausente em 1 de 10 amostra(s); observação interrompida' "$work/audio-monitor-gap.log"
for interrupted in reset recreate gap; do
  grep -q 'Observação incompleta/interrompida' "$work/audio-monitor-$interrupted.log"
  if grep -q 'Nenhum aumento de xrun/erro' "$work/audio-monitor-$interrupted.log"; then
    echo "ERROR: $interrupted was reported as an uninterrupted error-free run." >&2; exit 1
  fi
done
BRASA_AUDIO_REMOVE=0 sh "$root/scripts/brasa-audio-aggregate"
[ -f "$XDG_CONFIG_HOME/pipewire/pipewire.conf.d/90-brasa-aggregate.conf" ]
[ -f "$XDG_CONFIG_HOME/wireplumber/wireplumber.conf.d/90-brasa-clock-master.conf" ]
[ -f "$XDG_CONFIG_HOME/pipewire/pipewire.conf.d/90-brasa-aggregate.conf.previous" ]
cp "$XDG_CONFIG_HOME/pipewire/pipewire.conf.d/90-brasa-aggregate.conf" "$work/aggregate.before-failure"
cp "$XDG_CONFIG_HOME/wireplumber/wireplumber.conf.d/90-brasa-clock-master.conf" "$work/master.before-failure"
if BRASA_FAIL_RULE_MV=1 sh "$root/scripts/brasa-audio-aggregate" >/dev/null 2>&1; then
  echo 'ERROR: simulated WirePlumber commit failure was not reported.' >&2; exit 1
fi
cmp -s "$work/aggregate.before-failure" "$XDG_CONFIG_HOME/pipewire/pipewire.conf.d/90-brasa-aggregate.conf"
cmp -s "$work/master.before-failure" "$XDG_CONFIG_HOME/wireplumber/wireplumber.conf.d/90-brasa-clock-master.conf"
rm -f "$BRASA_MV_FAILED"
if BRASA_FAIL_RULE_MV=2 BRASA_AUDIO_REMOVE=1 sh "$root/scripts/brasa-audio-aggregate" >/dev/null 2>&1; then
  echo 'ERROR: simulated WirePlumber removal failure was not reported.' >&2; exit 1
fi
cmp -s "$work/aggregate.before-failure" "$XDG_CONFIG_HOME/pipewire/pipewire.conf.d/90-brasa-aggregate.conf"
cmp -s "$work/master.before-failure" "$XDG_CONFIG_HOME/wireplumber/wireplumber.conf.d/90-brasa-clock-master.conf"
BRASA_AUDIO_REMOVE=1 sh "$root/scripts/brasa-audio-aggregate"
[ ! -e "$XDG_CONFIG_HOME/pipewire/pipewire.conf.d/90-brasa-aggregate.conf" ]
[ ! -e "$XDG_CONFIG_HOME/wireplumber/wireplumber.conf.d/90-brasa-clock-master.conf" ]
sh "$root/scripts/brasa-run-windows" "$work/installer.exe" --name "Audio Editor"
[ -f "$HOME/.local/share/brasa/wineprefixes/audio-editor/.brasa-prefix-ready" ]
grep -q "$work/installer.exe" "$work/wine.log"
if sh "$root/scripts/brasa-run-windows" "$work/installer.exe" --name .. >/dev/null 2>&1; then
  echo 'ERROR: unsafe app name was accepted.' >&2; exit 1
fi
echo 'Brasa smoke checks passed: syntax, PipeWire output selection, aggregate rollback/removal and Wine prefix isolation.'



