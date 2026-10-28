# Brasa OS — protótipo de instalador

Brasa é um protótipo x86-64 baseado em FreeBSD. O objetivo é oferecer instalação gráfica simples, desktop KDE, suporte a áudio USB class-compliant e execução de alguns aplicativos Windows por Wine. Ainda não está pronto para instalar num computador de uso diário.

## Estado da ISO

A ISO mais recente é `.build/Brasa-live-r37-plasma-session-2026-10-28.iso` (SHA-256 `FF215E6CAD3AE4998A9865CEEFCFBB1F369971E84A13EB9C3DC3DC6635849084`). A instalação limpa da r37 terminou em um QCOW de 40 GiB e iniciou pelo disco, mas o primeiro login aceitou `brasa` e deixou a tela preta: `startplasma-x11` iniciou e encerrou em cerca de dois segundos. Portanto, a r37 ainda não passou no teste funcional do KDE; veja `docs/RELEASES.md` para o diagnóstico registrado. A imagem permanece publicada como `alpha_1.37`; nenhuma instalação em hardware real ou teste de áudio USB físico foi feita.

Não use esta imagem num disco físico. A base FreeBSD e o kernel vêm na ISO; KDE, Wine e componentes opcionais são instalados pela rede durante a instalação. O módulo `snd_uaudio` está habilitado, mas áudio USB em dispositivo físico ainda não foi testado.

## Objetivos e limitações

- KDE Plasma continua sendo o desktop instalado pretendido.
- Wine oferece compatibilidade parcial com aplicativos Windows; não executa drivers Windows.
- O driver FreeBSD `uaudio` cobre parte dos dispositivos USB Audio Class, sem garantia universal nem paridade com macOS.
- Instalação em computador físico, primeiro login KDE, áudio USB real e compatibilidade de aplicativos Windows não foram validados.

Leia `docs/PROJECT.md`, `docs/PROTOTYPE.md`, `docs/RELEASES.md` e `docs/USB-AUDIO.md`. Continue usando QCOW descartável; instalação em computador físico e áudio USB real ainda não foram validados.
