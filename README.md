# Brasa OS — protótipo de instalador

Brasa é um protótipo x86-64 baseado em FreeBSD. O objetivo é oferecer uma instalação gráfica simples, KDE preservado, Wine e suporte a interfaces de áudio USB class-compliant. Ainda não está pronto para instalar num computador de uso diário.

## Estado da imagem experimental mais recente

A ISO [pkgbase minimal com diagnóstico de fases](https://github.com/Mateus-Neinas/brasaOS/releases/tag/brasa-whpx-pkgbase-minimal-phases-2026-10-27) seleciona somente o conjunto inicializável `minimal`, em vez do conjunto `base` que também inclui `devel` e `optional`. Ela inclui mensagens para identificar se a próxima tentativa para ao consultar componentes, atualizar o catálogo, baixar ou instalar pacotes. Em QEMU/WHPX, esta variante ainda não passou do boot do kernel em dois perfis de CPU; a instalação não foi iniciada e a redução de tempo ainda não foi validada. A ISO anterior [pkgbase bounded-fetch diagnostic](https://github.com/Mateus-Neinas/brasaOS/releases/tag/brasa-whpx-pkgbase-bounded-fetch-diagnostic-2026-10-27) chegou ao pkgbase, mas ficou sem gravações no QCOW por cerca de 24 minutos. Consulte `docs/RELEASES.md` para hashes e resultados. As imagens são experimentais; não use num computador com dados importantes. JWM é somente o ambiente temporário do instalador; KDE continua sendo o desktop pretendido no sistema instalado. Consulte `docs/PROTOTYPE.md` antes de testar.

## O que funciona nesta mídia

- Inicia o instalador padrão do FreeBSD pelo menu **Boot Brasa**; também tenta abrir o assistente gráfico experimental.
- Permite testar a base FreeBSD e consultar o pacote Brasa em `/BRASA/BRASA_PROJECT_TAR_GZ`.
- Inclui o assistente gráfico Brasa e tenta iniciá-lo no ambiente live.
- O KDE, Wine e os aplicativos de áudio pertencem ao sistema instalado e ainda não foram validados nesta ISO.

## Limitações conhecidas

- A instalação da base FreeBSD ainda não foi concluída pelo assistente gráfico; o teste mais recente parou na etapa `FreeBSD Installer`, após particionar o QCOW descartável.
- `scripts/brasa-install-assistant` tem etapas visuais para conta, senha, seleção de disco e confirmação destrutiva. O instalador processou os componentes live, mas ainda não foi validado até o primeiro boot.
- A instalação e o primeiro login ainda precisam ser validados num ambiente live real antes de usar em um computador com dados importantes.
- O driver FreeBSD `uaudio` fornece suporte a parte dos dispositivos USB Audio Class; a compatibilidade depende do dispositivo e não foi validada contra toda a classe ou contra o macOS.
- Wine executa alguns programas Windows em espaço de usuário. Não executa drivers Windows nem garante compatibilidade geral.

## Desenvolvimento

Leia `docs/PROJECT.md`, `docs/PROTOTYPE.md`, `docs/RELEASES.md` e `docs/USB-AUDIO.md` antes de tentar instalar. Mantenha qualquer teste numa máquina virtual descartável. A compatibilidade de áudio USB depende do dispositivo, e a instalação completa, o primeiro login, KDE e Wine ainda precisam ser validados.
