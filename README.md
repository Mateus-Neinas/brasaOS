# Brasa OS — protótipo de instalador

Brasa é um protótipo x86-64 baseado em FreeBSD. O objetivo é oferecer instalação gráfica simples, desktop KDE, suporte a áudio USB class-compliant e execução de alguns aplicativos Windows por Wine. Ainda não está pronto para instalar num computador de uso diário.

## Estado da ISO

A única release publicada é `alpha_1.37`, a primeira versão que iniciou com sucesso no QEMU. A candidata local mais recente é `.build/Brasa-live-alpha_1.40-boot-diagnostics-hybrid.iso` (1.285.319.168 bytes; SHA-256 `982E77F99C2E949D7ECC164ADC182C5F71AAE98BEA03F1E3D068CE7EC9A14766`). Ela iniciou como dispositivo USB em UEFI no QEMU, obteve DHCP, carregou os pacotes e abriu o assistente gráfico Brasa. Esse teste não tinha disco de destino e não concluiu instalação; o boot físico ainda não foi validado. As candidatas intermediárias ficam versionadas apenas no código, sem releases ou assets ISO.

O boot BIOS da mídia alpha_1.37 foi confirmado no QEMU. A tentativa anterior em máquina real parou antes da interface gráfica. A 1.40 candidata chega à interface gráfica tanto em boot UEFI via CD virtual quanto em boot UEFI via USB virtual; não foi testada no PC físico nem instalada em disco. VMware em NAT chegou à tela gráfica; VMware em bridge não recebeu oferta DHCP, e o teste NAT do VirtualBox mostrou `no carrier`. Esses resultados dos hipervisores não identificam ainda a causa na placa física. A instalação em disco, o primeiro login KDE e o áudio USB real continuam sem validação. Não inicie a instalação em disco físico.

O desktop KDE Plasma continua sendo o desktop instalado pretendido. O módulo `snd_uaudio` está habilitado, mas dispositivos USB Audio Class ainda não foram testados em equipamento físico.

O Windows identifica a Ethernet física deste PC como Realtek RTL8125 (`PCI 10EC:8125`) e atualmente informa link, DHCP, gateway e DNS ativos. A candidata g inclui o módulo `realtek-rge-kmod`; o manual `rge(4)` do FreeBSD 15.1 lista suporte ao RTL8125. Falta confirmar no boot do Brasa a detecção/associação do driver e a conexão DHCP.

## Objetivos e limitações

- KDE Plasma continua sendo o desktop instalado pretendido.
- Wine oferece compatibilidade parcial com aplicativos Windows; não executa drivers Windows.
- O driver FreeBSD `uaudio` cobre parte dos dispositivos USB Audio Class, sem garantia universal nem paridade com macOS.
- Instalação em computador físico, primeiro login KDE, áudio USB real e compatibilidade de aplicativos Windows não foram validados.

Leia `docs/PROJECT.md`, `docs/PROTOTYPE.md`, `docs/RELEASES.md` e `docs/USB-AUDIO.md`. Continue usando QCOW descartável; instalação em computador físico e áudio USB real ainda não foram validados.
