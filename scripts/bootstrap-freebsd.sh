#!/bin/sh
# Bootstrap Brasa OS on a fresh FreeBSD amd64 installation.
set -eu
fail() { echo "brasa: $*" >&2; exit 1; }
msg() { printf '\nBrasa: %s\n' "$*"; }
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
installing_from_live=no
[ "${1-}" = --installing-from-live ] && installing_from_live=yes
release=$(freebsd-version -u | cut -d- -f1)
case "$release" in
  14.4|14.5|15.1) ;;
  *) fail "use FreeBSD 15.1, 14.5, or 14.4 (supported as of October 2026)." ;;
esac
msg "Bem-vindo à configuração do Brasa. Vamos preparar a conta e o desktop."
if [ ! -x /usr/local/sbin/pkg ]; then
  msg "Preparando o gerenciador de pacotes pkg."
  env ASSUME_ALWAYS_YES=yes /usr/sbin/pkg bootstrap -f
  msg "Gerenciador de pacotes pkg pronto."
fi
# Bound network stalls for repository metadata and missing packages. pkg.conf
# uses UCL syntax; each individual file fetch already defaults to 30 seconds.
install -d -m 0755 /usr/local/etc
cat > /usr/local/etc/pkg.conf <<'EOF'
fetch_timeout: 30
fetch_retry: 1
EOF
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

repo_catalog_ready=no
if [ -f /var/db/brasa-live-repo-catalog-ready ]; then
  repo_catalog_ready=yes
  export REPO_AUTOUPDATE=no
fi
install_packages() {
  if [ "$repo_catalog_ready" = yes ]; then
    if pkg install -U -y "$@"; then return 0; fi
    msg "Atualizando o catálogo de pacotes para concluir a instalação."
    pkg update -f
  fi
  pkg install -y "$@"
}

if [ "$repo_catalog_ready" != yes ]; then
  msg "Atualizando o catálogo de pacotes uma vez para conferir os componentes disponíveis."
  pkg update -f
  repo_catalog_ready=yes
  export REPO_AUTOUPDATE=no
fi

msg "Preparando o desktop KDE Plasma e os aplicativos essenciais."
# Use FreeBSD Handbook's Plasma meta package so the session manager, shell,
# activity manager, audio widget, and other required desktop services are all
# installed together. Keep the desired X11 session and familiar applications.
set -- plasma6-plasma plasma6-kactivitymanagerd plasma6-plasma-pa plasma6-kglobalacceld \
  plasma6-kwin-x11 plasma6-breeze konsole dolphin ark \
  sddm xorg-minimal drm-kmod
msg "Verificando a disponibilidade do componente opcional KDE kf6-kdesu."
if pkg rquery '%n' kf6-kdesu 2>/dev/null | grep -qx kf6-kdesu; then
  set -- "$@" kf6-kdesu
else
  echo "brasa: optional package 'kf6-kdesu' is unavailable; skipped."
fi
msg "Etapa 1/3: instalando o desktop KDE Plasma e os aplicativos essenciais."
install_packages "$@"

# Keep independent package transactions small so the GUI can identify which
# feature is currently being configured and a slow optional download does not
# hide progress for the core desktop.
set --
# Prefer the FreeBSD-native OSS backend with its rate servo. Keep OSS/kernel
# audio available as a fallback if the newer optional packages are missing.
for package in sox pipewire wireplumber; do
  msg "Verificando a disponibilidade do pacote de áudio $package."
  if pkg rquery '%n' "$package" 2>/dev/null | grep -qx "$package"; then
    set -- "$@" "$package"
  else
    echo "brasa: optional package '$package' is unavailable; skipped."
  fi
done
if pkg info -e pipewire-spa-oss >/dev/null 2>&1; then
  echo "brasa: pipewire-spa-oss is installed and conflicts with pipewire-spa-oss-ng; keeping the OSS/kernel audio fallback."
else
  package=pipewire-spa-oss-ng
  msg "Verificando a disponibilidade do backend OSS do PipeWire."
  if pkg rquery '%n' "$package" 2>/dev/null | grep -qx "$package"; then
    set -- "$@" "$package"
  else
    echo "brasa: optional package '$package' is unavailable; skipped."
  fi
fi
if [ "$#" -gt 0 ]; then
  msg "Etapa 2/3: instalando os componentes opcionais de áudio; snd_uaudio já está habilitado no kernel."
  install_packages "$@"
else
  msg "Etapa 2/3: componentes PipeWire opcionais indisponíveis; áudio USB class compliant continua pelo snd_uaudio/OSS."
fi

set --
msg "Verificando a disponibilidade do Wine."
if pkg rquery '%n' wine 2>/dev/null | grep -qx wine; then
  set -- wine
  for package in wine-gecko wine-mono; do
    msg "Verificando a disponibilidade do componente $package."
    if pkg rquery '%n' "$package" 2>/dev/null | grep -qx "$package"; then
      set -- "$@" "$package"
    else
      echo "brasa: optional package '$package' is unavailable; skipped."
    fi
  done
  msg "Etapa 3/3: instalando Wine e os componentes de compatibilidade disponíveis."
  install_packages "$@"
else
  msg "Etapa 3/3: Wine não está disponível neste repositório; o desktop está pronto sem ele."
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
install -d -m 0755 "$brasa_home/.config"
chown "$brasa_user:$brasa_group" "$brasa_home/.config"
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
if [ "$installing_from_live" = yes ]; then
  rm -f /var/db/brasa-live-repo-catalog-ready
  msg "Desktop Brasa configurado para $brasa_user."
else
  msg "O desktop Brasa foi configurado para $brasa_user. A senha de administrador e de login é a mesma. Reinicie para entrar no desktop."
fi
