#!/bin/sh
# Bootstrap Brasa OS on a fresh FreeBSD amd64 installation.
set -eu
fail() { echo "brasa: $*" >&2; exit 1; }
msg() { printf '\n\033[1;36mBrasa\033[0m %s\n' "$*"; }
ask() {
  prompt=$1 default=${2-}
  if [ -n "$default" ]; then
    printf '%s [%s]: ' "$prompt" "$default"
  else
    printf '%s: ' "$prompt"
  fi
  IFS= read -r reply
  printf '%s' "${reply:-$default}"
}
[ "$(id -u)" -eq 0 ] || fail "run as root."
[ "$(uname -s)" = "FreeBSD" ] || fail "this installer requires FreeBSD."
[ "$(uname -m)" = "amd64" ] || fail "only FreeBSD amd64 is supported."
release=$(freebsd-version -u | cut -d- -f1)
case "$release" in
  14.4|14.5|15.1) ;;
  *) fail "use FreeBSD 15.1, 14.5, or 14.4 (supported as of October 2026)." ;;
esac
msg "Bem-vindo à configuração do Brasa. Vamos preparar a conta e o desktop."
if [ ! -x /usr/local/sbin/pkg ]; then
  env ASSUME_ALWAYS_YES=yes /usr/sbin/pkg bootstrap -f
fi
if [ -f /var/db/brasa-live-user ]; then
  IFS='|' read -r brasa_user full_name < /var/db/brasa-live-user
  case "$brasa_user" in ''|*[!a-z0-9_-]*) fail "nome de usuário inválido enviado pelo instalador." ;; esac
  [ -n "$full_name" ] || full_name='Usuário Brasa'
  if ! pw usershow "$brasa_user" >/dev/null 2>&1; then
    pw useradd "$brasa_user" -m -d "/home/$brasa_user" -s /bin/tcsh -G wheel,video,operator -c "$full_name"
  fi
  rm -f /var/db/brasa-live-user
elif pw usershow brasa >/dev/null 2>&1; then
  brasa_user=brasa
  msg "A conta brasa já existe; vou preservar os dados pessoais dela."
else
  full_name=$(ask 'Como você quer ser chamado?' 'Usuário Brasa')
  login=$(ask 'Nome curto para entrar no computador' 'brasa')
  case "$login" in
    ''|*[!a-z0-9_-]*) fail "use apenas letras minúsculas, números, _ ou - no nome de usuário." ;;
  esac
  pw usershow "$login" >/dev/null 2>&1 && fail "esse nome de usuário já existe; escolha outro."
  pw useradd "$login" -m -d "/home/$login" -s /bin/tcsh -G wheel,video,operator -c "$full_name"
  brasa_user=$login
  echo "$brasa_user" > /var/db/brasa-user
fi
brasa_home=$(pw usershow "$brasa_user" | awk -F: '{print $9}')
[ -n "$brasa_home" ] && [ -d "$brasa_home" ] || fail "could not find the brasa home directory."
brasa_group=$(id -gn "$brasa_user")

if [ -t 0 ] && [ -t 1 ] && [ ! -f /var/db/brasa-password-ready ]; then
  msg "Defina uma senha de login. A mesma senha será usada para a conta de administrador."
  while :; do
    printf 'Senha: '; stty -echo; IFS= read -r password; stty echo; printf '\n'
    printf 'Repita a senha: '; stty -echo; IFS= read -r password_again; stty echo; printf '\n'
    [ -n "$password" ] || { echo 'A senha não pode ficar vazia.'; continue; }
    [ "$password" = "$password_again" ] && break
    echo 'As senhas não coincidem. Tente novamente.'
  done
  password_file=$(mktemp /tmp/brasa-password.XXXXXX)
  chmod 600 "$password_file"
  printf '%s\n' "$password" > "$password_file"
  exec 3< "$password_file"
  pw usermod "$brasa_user" -h 3
  exec 3<&-
  exec 3< "$password_file"
  pw usermod root -h 3
  exec 3<&-
  rm -f "$password_file"
  unset password password_again
  : > /var/db/brasa-password-ready
fi

# snd_uaudio is the FreeBSD USB Audio Class kernel driver.
sysrc dbus_enable="YES"
sysrc sddm_enable="YES"
sysrc kld_list+="snd_uaudio"
msg "Instalando o desktop KDE Plasma e os aplicativos essenciais."
pkg install -y plasma6-plasma konsole dolphin ark sddm xorg drm-kmod zenity

install_optional() {
  if pkg rquery '%n' "$1" 2>/dev/null | grep -qx "$1"; then
    msg "Instalando o componente opcional $1."
    pkg install -y "$1"
  else
    echo "brasa: optional package '$1' is unavailable; skipped."
  fi
}
install_optional kf6-kdesu
install_optional sox
# Prefer the FreeBSD-native OSS backend with its rate servo. Keep OSS/kernel
# audio available as a fallback if the newer optional packages are missing.
for audio_pkg in pipewire wireplumber; do
  install_optional "$audio_pkg"
done
if pkg info -e pipewire-spa-oss >/dev/null 2>&1; then
  echo "brasa: pipewire-spa-oss is installed and conflicts with pipewire-spa-oss-ng; remove it before enabling the Brasa PipeWire backend."
else
  install_optional pipewire-spa-oss-ng
fi
if pkg rquery '%n' wine 2>/dev/null | grep -qx wine; then
  pkg install -y wine
  install_optional wine-gecko
  install_optional wine-mono
else
  echo "brasa: Wine is unavailable in this repository; install it later if supported."
fi

install -d -o root -g wheel -m 0755 /usr/local/bin /usr/local/share/applications /usr/local/share/color-schemes
install -m 0755 scripts/brasa-run-windows /usr/local/bin/brasa-run-windows
install -m 0755 scripts/brasa-audio-status /usr/local/bin/brasa-audio-status
install -m 0755 scripts/brasa-audio-monitor /usr/local/bin/brasa-audio-monitor
install -m 0755 scripts/brasa-audio-select /usr/local/bin/brasa-audio-select
install -m 0755 scripts/brasa-audio-aggregate /usr/local/bin/brasa-audio-aggregate
install -m 0755 scripts/brasa-audio-start /usr/local/bin/brasa-audio-start
install -m 0755 scripts/brasa-audio-test /usr/local/bin/brasa-audio-test
install -m 0755 scripts/brasa-windows-import /usr/local/bin/brasa-windows-import
install -m 0755 scripts/brasa-apply-theme /usr/local/bin/brasa-apply-theme
install -m 0644 config/colors/Brasa.colors /usr/local/share/color-schemes/Brasa.colors
install -m 0644 config/brasa-audio.desktop /usr/local/share/applications/brasa-audio.desktop
install -m 0644 config/brasa-audio-aggregate.desktop /usr/local/share/applications/brasa-audio-aggregate.desktop
install -m 0644 config/brasa-audio-test.desktop /usr/local/share/applications/brasa-audio-test.desktop
install -m 0644 config/brasa-audio-monitor.desktop /usr/local/share/applications/brasa-audio-monitor.desktop
install -m 0644 config/brasa-windows.desktop /usr/local/share/applications/brasa-windows.desktop
install -d -o "$brasa_user" -g "$brasa_group" -m 0755 "$brasa_home/.config/autostart"
install -o "$brasa_user" -g "$brasa_group" -m 0644 config/brasa-theme-autostart.desktop "$brasa_home/.config/autostart/brasa-theme.desktop"
if pkg info -e pipewire && pkg info -e wireplumber && pkg info -e pipewire-spa-oss-ng; then
  install -d -o "$brasa_user" -g "$brasa_group" -m 0755 "$brasa_home/.config/autostart"
  cat > "$brasa_home/.config/autostart/brasa-pipewire.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Name=Brasa Audio Engine
Exec=/usr/local/bin/brasa-audio-start
OnlyShowIn=KDE;
X-KDE-autostart-after=panel
EOF
  chown "$brasa_user:$brasa_group" "$brasa_home/.config/autostart/brasa-pipewire.desktop"
fi
if [ "${1-}" = --installing-from-live ]; then
  msg "Desktop Brasa configurado para $brasa_user."
else
  msg "O desktop Brasa foi configurado para $brasa_user. A senha de administrador e de login é a mesma. Reinicie para entrar no desktop."
fi
