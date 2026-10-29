# Brasa OS — protótipo de instalador

Brasa é um protótipo x86-64 baseado em FreeBSD. O objetivo é oferecer instalação gráfica simples, desktop KDE, suporte a áudio USB class-compliant e execução de alguns aplicativos Windows por Wine. Ainda não está pronto para instalar num computador de uso diário.

## Estado da ISO

A versão publicada mais recente é `alpha_1.37b`, disponível como `Brasa-live-alpha_1.37b.iso` na página de Releases. SHA-256: `36B53E173EEBE74FA4DA0395A469350BD632A6ADACE11573F05DBC0C9F1A6CC3`. A candidata `.build/Brasa-live-alpha_1.37e-ethernet.iso` desativa o início automático do stack Bluetooth somente no live. No QEMU, com e1000 e DHCP, iniciou sozinha o assistente gráfico sem abrir o menu padrão do FreeBSD. Ainda não foi testada com a placa Ethernet física do usuário, nem instalada em disco; por isso permanece local e não publicada. As candidatas `alpha_1.37c` e `alpha_1.37d-ethernet` permanecem intactas. No Rufus, use modo DD/raw; `Alt+I` força esse modo.

O boot BIOS da mídia alpha_1.37b foi confirmado no QEMU. Em máquina real, ela parou por cerca de 20 minutos antes da interface gráfica; o instalador não chegou a abrir nem a selecionar um disco. As versões 1.37c em diante removem uma possível espera em `/dev/ttyu0`; a candidata 1.37e chegou ao assistente gráfico no QEMU, mas a placa Ethernet física e a instalação em disco continuam sem validação. Não inicie a instalação em disco físico. O áudio USB real também não foi validado.

O desktop KDE Plasma continua sendo o desktop instalado pretendido. O módulo `snd_uaudio` está habilitado, mas dispositivos USB Audio Class ainda não foram testados em equipamento físico.

## Objetivos e limitações

- KDE Plasma continua sendo o desktop instalado pretendido.
- Wine oferece compatibilidade parcial com aplicativos Windows; não executa drivers Windows.
- O driver FreeBSD `uaudio` cobre parte dos dispositivos USB Audio Class, sem garantia universal nem paridade com macOS.
- Instalação em computador físico, primeiro login KDE, áudio USB real e compatibilidade de aplicativos Windows não foram validados.

Leia `docs/PROJECT.md`, `docs/PROTOTYPE.md`, `docs/RELEASES.md` e `docs/USB-AUDIO.md`. Continue usando QCOW descartável; instalação em computador físico e áudio USB real ainda não foram validados.
