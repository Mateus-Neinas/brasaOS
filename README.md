# Brasa OS — protótipo de instalador

Brasa é um protótipo x86-64 baseado em FreeBSD. O objetivo é oferecer instalação gráfica simples, desktop KDE, suporte a áudio USB class-compliant e execução de alguns aplicativos Windows por Wine. Ainda não está pronto para instalar num computador de uso diário.

## Estado da ISO

A versão publicada mais recente é `alpha_1.37b`, disponível como `Brasa-live-alpha_1.37b.iso` na página de Releases. SHA-256: `36B53E173EEBE74FA4DA0395A469350BD632A6ADACE11573F05DBC0C9F1A6CC3`. A candidata híbrida local mais nova é `.build/Brasa-live-alpha_1.37g-network-diagnostics-hybrid.iso` (1.285.308.928 bytes; SHA-256 `3F5B2C09864F645949EB3C0DA59CEF188E628F097649BC425BFEFBED6491E6E4`). Ela inicia pelo USB virtual no QEMU, obtém DHCP pela rede NAT e abre a tela gráfica “Instalar Brasa”. Nenhuma instalação foi iniciada e nenhum disco virtual foi conectado. A versão g ainda não foi testada em máquina física nem instalada em disco, portanto continua local e não publicada. No Rufus, use modo DD/raw; `Alt+I` força esse modo.

O boot BIOS da mídia alpha_1.37b foi confirmado no QEMU. Em máquina real, ela parou por cerca de 20 minutos antes da interface gráfica; o instalador não chegou a abrir nem a selecionar um disco. A candidata g mostra etapa, interface, DHCP e PCI quando a rede falha. VMware em NAT chegou à tela gráfica; VMware em bridge não recebeu oferta DHCP, e o teste NAT do VirtualBox mostrou `no carrier`. Esses resultados dos hipervisores não identificam ainda a causa na placa física. A instalação em disco, o primeiro login KDE e o áudio USB real continuam sem validação. Não inicie a instalação em disco físico.

O desktop KDE Plasma continua sendo o desktop instalado pretendido. O módulo `snd_uaudio` está habilitado, mas dispositivos USB Audio Class ainda não foram testados em equipamento físico.

## Objetivos e limitações

- KDE Plasma continua sendo o desktop instalado pretendido.
- Wine oferece compatibilidade parcial com aplicativos Windows; não executa drivers Windows.
- O driver FreeBSD `uaudio` cobre parte dos dispositivos USB Audio Class, sem garantia universal nem paridade com macOS.
- Instalação em computador físico, primeiro login KDE, áudio USB real e compatibilidade de aplicativos Windows não foram validados.

Leia `docs/PROJECT.md`, `docs/PROTOTYPE.md`, `docs/RELEASES.md` e `docs/USB-AUDIO.md`. Continue usando QCOW descartável; instalação em computador físico e áudio USB real ainda não foram validados.
