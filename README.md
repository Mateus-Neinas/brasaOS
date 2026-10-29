# Brasa OS — protótipo de instalador

Brasa é um protótipo x86-64 baseado em FreeBSD. O objetivo é oferecer instalação gráfica simples, desktop KDE, suporte a áudio USB class-compliant e execução de alguns aplicativos Windows por Wine. Ainda não está pronto para instalar num computador de uso diário.

## Estado da ISO

A única release publicada é `alpha_1.37`, a primeira versão que iniciou com sucesso no QEMU. A candidata USB híbrida atual é `.build/Brasa-live-alpha_1.45-rge-link-recovery-hybrid.iso` (1.285.331.456 bytes; SHA-256 `AFBFE52B9670C63CD337B44F469B25EF4980C40AF4D173C43431561A931A6BE4`); a cópia para teste está em `Downloads/Brasa-alpha_1.45-rge-link-recovery-hybrid.iso`. O firmware UEFI do QEMU carregou o sistema pela partição EFI GPT e o live abriu o assistente gráfico “Instalar Brasa”. A 1.45 tenta renegociar o link da Realtek RTL8125 se o driver for carregado sem carrier, mas essa mudança ainda precisa de teste físico. Não use as ISOs ópticas antigas para gravar USB. Candidatas intermediárias ficam no histórico do código, sem releases ou assets ISO.

O boot BIOS da mídia alpha_1.37 foi confirmado no QEMU. A foto do boot físico mais recente mostra que `if_rge.ko` associou-se à RTL8125 (`rge0`), mas a interface ficou `no carrier`; por isso DHCP falhou e o instalador gráfico não iniciou. A ISO 1.45 inclui uma tentativa limitada de renegociação, ainda não testada no PC. O QEMU chegou à tela gráfica do assistente, mas não tinha disco destino e não instalou o sistema. A sessão KDE após instalação UEFI, a instalação em PC físico e o áudio USB real continuam sem validação. Não inicie a instalação em disco físico.

O desktop KDE Plasma continua sendo o desktop instalado pretendido. O módulo `snd_uaudio` está habilitado, mas dispositivos USB Audio Class ainda não foram testados em equipamento físico.

O Windows identifica a Ethernet física deste PC como Realtek RTL8125 (`PCI 10EC:8125`) e atualmente informa link, DHCP, gateway e DNS ativos. A candidata inclui `realtek-rge-kmod`; o manual [`rge(4)` do FreeBSD 15.1](https://man.freebsd.org/cgi/man.cgi?query=rge&manpath=FreeBSD+15.1-RELEASE+and+Ports.quarterly) lista RTL8125/8125B. O driver associou-se no boot físico, mas ainda falta conseguir link e DHCP no Brasa.

## Objetivos e limitações

- KDE Plasma continua sendo o desktop instalado pretendido.
- Wine oferece compatibilidade parcial com aplicativos Windows; não executa drivers Windows.
- O driver FreeBSD `uaudio` cobre parte dos dispositivos USB Audio Class, sem garantia universal nem paridade com macOS.
- Instalação em computador físico, primeiro login KDE, áudio USB real e compatibilidade de aplicativos Windows não foram validados.

Leia `docs/PROJECT.md`, `docs/PROTOTYPE.md`, `docs/RELEASES.md` e `docs/USB-AUDIO.md`. Continue usando QCOW descartável; instalação em computador físico e áudio USB real ainda não foram validados.
