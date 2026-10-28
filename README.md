# Brasa OS — protótipo de instalador

Brasa é um protótipo x86-64 baseado em FreeBSD. O objetivo é oferecer instalação gráfica simples, desktop KDE, suporte a áudio USB class-compliant e execução de alguns aplicativos Windows por Wine. Ainda não está pronto para instalar num computador de uso diário.

## Estado da ISO

A única ISO Brasa mantida localmente é `.build/Brasa-live-r36-install-progress-2026-10-28.iso` (SHA-256 `D9A931F7F741326A1791A6A02EC70AED4418F57BC2E81E90DE0099AA4A483475`). Em QEMU, o instalador concluiu a instalação no QCOW de 40 GiB. O boot do disco não chegou à tela de login gráfica, tanto em WHPX como na comparação TCG; a VM segue aberta no teste. O QCOW fica em `%TEMP%\Brasa-r36-test.qcow2`.

Não use esta imagem num disco físico. A base FreeBSD e o kernel vêm na ISO; KDE, Wine e componentes opcionais são instalados pela rede durante a instalação. O módulo `snd_uaudio` está habilitado, mas áudio USB em dispositivo físico ainda não foi testado.

## Objetivos e limitações

- KDE Plasma continua sendo o desktop instalado pretendido.
- Wine oferece compatibilidade parcial com aplicativos Windows; não executa drivers Windows.
- O driver FreeBSD `uaudio` cobre parte dos dispositivos USB Audio Class, sem garantia universal nem paridade com macOS.
- Instalação em computador físico, primeiro login KDE, áudio USB real e compatibilidade de aplicativos Windows não foram validados.

Leia `docs/PROJECT.md`, `docs/PROTOTYPE.md`, `docs/RELEASES.md` e `docs/USB-AUDIO.md`. Enquanto o boot do disco não for confirmado, mantenha os testes em QCOW descartável e não publique ISO como release.
