# Brasa OS — protótipo de instalador

Brasa é um protótipo x86-64 baseado em FreeBSD. O objetivo é oferecer instalação gráfica simples, desktop KDE, suporte a áudio USB class-compliant e execução de alguns aplicativos Windows por Wine. Ainda não está pronto para instalar num computador de uso diário.

## Estado da ISO

A versão mais recente é `alpha_1.37b`, disponível como `Brasa-live-alpha_1.37b.iso` na página de Releases. SHA-256: `36B53E173EEBE74FA4DA0395A469350BD632A6ADACE11573F05DBC0C9F1A6CC3`. Ela mantém a r37 e adiciona estrutura híbrida PMBR/GPT para gravação bruta em pendrive. No Rufus, use modo DD/raw; `Alt+I` força esse modo.

O boot BIOS por USB foi confirmado no QEMU até o ambiente live gráfico. A instalação limpa desta imagem falhou no QEMU durante a extração da base FreeBSD; não instale em disco físico até essa falha ser corrigida. Use apenas para testar o boot live. A gravação física com Rufus, boot UEFI e áudio USB real ainda não foram testados.

O desktop KDE Plasma continua sendo o desktop instalado pretendido. O módulo `snd_uaudio` está habilitado, mas dispositivos USB Audio Class ainda não foram testados em equipamento físico.

## Objetivos e limitações

- KDE Plasma continua sendo o desktop instalado pretendido.
- Wine oferece compatibilidade parcial com aplicativos Windows; não executa drivers Windows.
- O driver FreeBSD `uaudio` cobre parte dos dispositivos USB Audio Class, sem garantia universal nem paridade com macOS.
- Instalação em computador físico, primeiro login KDE, áudio USB real e compatibilidade de aplicativos Windows não foram validados.

Leia `docs/PROJECT.md`, `docs/PROTOTYPE.md`, `docs/RELEASES.md` e `docs/USB-AUDIO.md`. Continue usando QCOW descartável; instalação em computador físico e áudio USB real ainda não foram validados.
