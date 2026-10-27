# Brasa OS — protótipo de instalador

Brasa é um protótipo x86-64 baseado em FreeBSD. O objetivo é oferecer uma instalação gráfica simples, KDE preservado, Wine e suporte a interfaces de áudio USB class-compliant. Ainda não está pronto para instalar num computador de uso diário.

## Estado da imagem experimental mais recente

A ISO [WHPX pkgbase extract-test](https://github.com/Mateus-Neinas/brasaOS/releases/tag/brasa-whpx-pkgbase-extract-test-2026-10-27) testa a instalação da base FreeBSD 15.1 por pacotes, sem baixar e descompactar `base.txz`/`kernel.txz`. Em QEMU/WHPX com 8 GB, o live e o assistente gráfico abriram e o QCOW descartável foi particionado. A instalação da base parou antes de baixar pacotes por falha de resolução DNS no repositório FreeBSD-base; portanto não houve medição de velocidade nem instalação concluída. A variante anterior por distribuições continua disponível na release anterior. Não use nenhuma dessas ISOs num computador com dados importantes. JWM é somente o ambiente temporário do instalador; KDE continua sendo o desktop pretendido no sistema instalado. Consulte `docs/RELEASES.md` e `docs/PROTOTYPE.md` antes de testar.
## O que funciona nesta mídia

- Inicia o instalador padrão do FreeBSD pelo menu **Boot Brasa**; também tenta abrir o assistente gráfico experimental.
- Permite testar a base FreeBSD e consultar o pacote Brasa em `/BRASA/BRASA_PROJECT_TAR_GZ`.
- Inclui o assistente gráfico Brasa e tenta iniciá-lo no ambiente live.
- O KDE, Wine e os aplicativos de áudio pertencem ao sistema instalado e ainda não foram validados nesta ISO.

## Limitações conhecidas

- A instalação da base FreeBSD ainda não foi concluída pelo assistente gráfico; o teste pkgbase parou ao atualizar o repositório por falha de resolução DNS.
- `scripts/brasa-install-assistant` tem etapas visuais para conta, senha, seleção de disco e confirmação destrutiva. O instalador processou os componentes live e baixou a base, mas ainda não foi validado até o primeiro boot.
- A instalação e o primeiro login ainda precisam ser validados num ambiente live real antes de usar em um computador com dados importantes.
- O driver FreeBSD `uaudio` fornece suporte a parte dos dispositivos USB Audio Class; a compatibilidade depende do dispositivo e não foi validada contra toda a classe ou contra o macOS.
- Wine executa alguns programas Windows em espaço de usuário. Não executa drivers Windows nem garante compatibilidade geral.

## Desenvolvimento

Leia `docs/PROJECT.md`, `docs/PROTOTYPE.md`, `docs/RELEASES.md` e `docs/USB-AUDIO.md` antes de tentar instalar. Mantenha qualquer teste numa máquina virtual descartável. A compatibilidade de áudio USB depende do dispositivo, e a instalação completa, o primeiro login, KDE e Wine ainda precisam ser validados.
