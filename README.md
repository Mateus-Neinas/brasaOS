# Brasa OS — protótipo de instalador

Brasa é um protótipo x86-64 baseado em FreeBSD. O objetivo é oferecer uma instalação gráfica simples, KDE preservado, Wine e suporte a interfaces de áudio USB class-compliant. Ainda não está pronto para instalar num computador de uso diário.

## Estado da imagem experimental mais recente

A [ISO experimental WHPX com VirtIO GPU](https://github.com/Mateus-Neinas/brasaOS/releases/tag/brasa-whpx-virtio-progress-2026-10-27) inicia o ambiente live, abre o assistente gráfico e chega à confirmação do disco virtual de 40 GB. O driver VirtIO permitiu abrir o X no QEMU com WHPX. Após confirmar o disco descartável, a instalação avançou pela base, mas ficou em 97% por vários minutos sem novas gravações. A instalação completa não foi validada; não use esta imagem em um computador com dados importantes. JWM é somente o ambiente temporário do instalador; KDE continua sendo o desktop pretendido no sistema instalado. Consulte `docs/RELEASES.md` e `docs/PROTOTYPE.md` antes de testar.

## O que funciona nesta mídia

- Inicia o instalador padrão do FreeBSD pelo menu **Boot Brasa**; também tenta abrir o assistente gráfico experimental.
- Permite testar a base FreeBSD e consultar o pacote Brasa em `/BRASA/BRASA_PROJECT_TAR_GZ`.
- Inclui o assistente gráfico Brasa e tenta iniciá-lo no ambiente live.
- O KDE, Wine e os aplicativos de áudio pertencem ao sistema instalado e ainda não foram validados nesta ISO.

## Limitações conhecidas

- A instalação da base FreeBSD ainda não foi concluída pelo assistente gráfico.
- `scripts/brasa-install-assistant` tem etapas visuais para conta, senha, seleção de disco e confirmação destrutiva. O fluxo chegou à extração da base no disco virtual, mas ainda não foi concluído nem validado até o primeiro boot.
- A instalação e o primeiro login ainda precisam ser validados num ambiente live real antes de usar em um computador com dados importantes.
- O driver FreeBSD `uaudio` fornece suporte a parte dos dispositivos USB Audio Class; a compatibilidade depende do dispositivo e não foi validada contra toda a classe ou contra o macOS.
- Wine executa alguns programas Windows em espaço de usuário. Não executa drivers Windows nem garante compatibilidade geral.

## Desenvolvimento

Leia `docs/PROJECT.md`, `docs/PROTOTYPE.md`, `docs/RELEASES.md` e `docs/USB-AUDIO.md` antes de tentar instalar. Mantenha qualquer teste numa máquina virtual descartável. A compatibilidade de áudio USB depende do dispositivo, e a instalação completa, o primeiro login, KDE e Wine ainda precisam ser validados.
