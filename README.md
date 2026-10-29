# Brasa OS — protótipo de instalador

Brasa é um protótipo x86-64 baseado em FreeBSD. O objetivo é oferecer instalação gráfica simples, desktop KDE, suporte a áudio USB class-compliant e execução de alguns aplicativos Windows por Wine. Ainda não está pronto para instalar num computador de uso diário.

## Estado da ISO

A versão publicada mais recente é `alpha_1.37b`, disponível como `Brasa-live-alpha_1.37b.iso` na página de Releases. SHA-256: `36B53E173EEBE74FA4DA0395A469350BD632A6ADACE11573F05DBC0C9F1A6CC3`. A candidata local `alpha_1.37c` está em `.build/Brasa-live-alpha_1.37c.iso`; ela remove aberturas diretas da porta serial durante o boot, possível causa da espera de 20 minutos em máquina real. A candidata passou pela criação e inspeção estrutural, mas ainda aguarda novo boot em hardware. No Rufus, use modo DD/raw; `Alt+I` força esse modo.

O boot BIOS da mídia alpha_1.37b foi confirmado no QEMU. Em máquina real, ela parou por cerca de 20 minutos antes da interface gráfica; o instalador não chegou a abrir nem a selecionar um disco. A candidata alpha_1.37c remove uma possível espera em `/dev/ttyu0`, mas ainda não foi validada em hardware. Não inicie a instalação em disco físico. A instalação limpa em QEMU e o áudio USB real também não foram validados nesta candidata.

O desktop KDE Plasma continua sendo o desktop instalado pretendido. O módulo `snd_uaudio` está habilitado, mas dispositivos USB Audio Class ainda não foram testados em equipamento físico.

## Objetivos e limitações

- KDE Plasma continua sendo o desktop instalado pretendido.
- Wine oferece compatibilidade parcial com aplicativos Windows; não executa drivers Windows.
- O driver FreeBSD `uaudio` cobre parte dos dispositivos USB Audio Class, sem garantia universal nem paridade com macOS.
- Instalação em computador físico, primeiro login KDE, áudio USB real e compatibilidade de aplicativos Windows não foram validados.

Leia `docs/PROJECT.md`, `docs/PROTOTYPE.md`, `docs/RELEASES.md` e `docs/USB-AUDIO.md`. Continue usando QCOW descartável; instalação em computador físico e áudio USB real ainda não foram validados.
