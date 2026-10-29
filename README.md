# Brasa OS — protótipo de instalador

Brasa é um protótipo x86-64 baseado em FreeBSD. O objetivo é oferecer instalação gráfica simples, desktop KDE, suporte a áudio USB class-compliant e execução de alguns aplicativos Windows por Wine. Ainda não está pronto para instalar num computador de uso diário.

## Estado da ISO

A única release publicada é `alpha_1.37`, a primeira versão que iniciou com sucesso no QEMU. A candidata local mais recente é `.build/Brasa-live-alpha_1.40-boot-diagnostics-hybrid.iso` (1.285.319.168 bytes; SHA-256 `982E77F99C2E949D7ECC164ADC182C5F71AAE98BEA03F1E3D068CE7EC9A14766`). Ela iniciou por USB em UEFI no QEMU, obteve DHCP, abriu o assistente gráfico e concluiu a instalação num QCOW2 descartável. O primeiro boot UEFI pelo disco chegou ao console do FreeBSD; o Xorg terminou com `no screens found`, sem abrir SDDM/KDE. A causa de vídeo UEFI continua em investigação. O boot e a instalação em PC físico ainda não foram validados. As candidatas intermediárias ficam versionadas apenas no código, sem releases ou assets ISO.

O boot BIOS da mídia alpha_1.37 foi confirmado no QEMU. A tentativa anterior em máquina real parou antes da interface gráfica. A candidata 1.40 chega à interface do instalador tanto por CD virtual quanto por USB virtual UEFI, e instalou no disco virtual descartável; seu desktop UEFI ainda não inicia. VMware em NAT chegou à tela gráfica; VMware em bridge não recebeu oferta DHCP, e o teste NAT do VirtualBox mostrou `no carrier`. Esses resultados dos hipervisores não identificam ainda a causa na placa física. A sessão KDE após instalação UEFI, o boot e a instalação em PC físico e o áudio USB real continuam sem validação. Não inicie a instalação em disco físico.

O desktop KDE Plasma continua sendo o desktop instalado pretendido. O módulo `snd_uaudio` está habilitado, mas dispositivos USB Audio Class ainda não foram testados em equipamento físico.

O Windows identifica a Ethernet física deste PC como Realtek RTL8125 (`PCI 10EC:8125`) e atualmente informa link, DHCP, gateway e DNS ativos. A candidata g inclui o módulo `realtek-rge-kmod`; o manual `rge(4)` do FreeBSD 15.1 lista suporte ao RTL8125. Falta confirmar no boot do Brasa a detecção/associação do driver e a conexão DHCP.

## Objetivos e limitações

- KDE Plasma continua sendo o desktop instalado pretendido.
- Wine oferece compatibilidade parcial com aplicativos Windows; não executa drivers Windows.
- O driver FreeBSD `uaudio` cobre parte dos dispositivos USB Audio Class, sem garantia universal nem paridade com macOS.
- Instalação em computador físico, primeiro login KDE, áudio USB real e compatibilidade de aplicativos Windows não foram validados.

Leia `docs/PROJECT.md`, `docs/PROTOTYPE.md`, `docs/RELEASES.md` e `docs/USB-AUDIO.md`. Continue usando QCOW descartável; instalação em computador físico e áudio USB real ainda não foram validados.
