# Brasa OS — protótipo de instalador

Brasa é um protótipo x86-64 baseado em FreeBSD. O objetivo é oferecer uma instalação gráfica simples, KDE preservado, Wine e suporte a interfaces de áudio USB class-compliant. Ainda não está pronto para instalar num computador de uso diário.

## Estado da imagem experimental mais recente

A release r7 abre o assistente gráfico e extrai a base/kernel locais, mas o teste parou ao configurar o desktop. Esta revisão reduz o conjunto KDE instalado: usa Plasma Desktop com KWin X11 e Breeze, em vez do pacote meta completo, preservando SDDM, Dolphin, Konsole, Ark, áudio USB e Wine. Também junta os pacotes numa única transação. Na base de pacotes incluída numa ISO experimental anterior, a dependência estimada cai de 960 para 683 pacotes e de 2.359 para 1.378 MiB de downloads; isso ainda é uma estimativa, não um tempo medido. A nova ISO experimental e esse fluxo precisam ser retestados em QEMU. A instalação completa, o primeiro boot, KDE, Wine e interfaces USB físicas ainda não foram validados. Consulte `docs/RELEASES.md` para hashes e resultados. As imagens são experimentais; não use num computador com dados importantes. JWM é somente o ambiente temporário do instalador; KDE continua sendo o desktop pretendido no sistema instalado. Consulte `docs/PROTOTYPE.md` antes de testar.

## O que funciona nesta mídia

- Inicia o assistente gráfico experimental automaticamente, com o instalador FreeBSD como fallback.
- Permite testar a base FreeBSD e consultar o pacote Brasa em `/BRASA/BRASA_PROJECT_TAR_GZ`.
- Inclui o assistente gráfico Brasa e tenta iniciá-lo no ambiente live.
- O KDE, Wine e os aplicativos de áudio pertencem ao sistema instalado e ainda não foram validados nesta ISO.

## Limitações conhecidas

- A instalação da base FreeBSD e a configuração do desktop ainda não foram concluídas pelo assistente gráfico.
- `scripts/brasa-install-assistant` tem etapas visuais para conta, senha, seleção de disco e confirmação destrutiva. O instalador processou os componentes live, mas ainda não foi validado até o primeiro boot.
- A instalação e o primeiro login ainda precisam ser validados num ambiente live real antes de usar em um computador com dados importantes.
- O driver FreeBSD `uaudio` fornece suporte a parte dos dispositivos USB Audio Class; a compatibilidade depende do dispositivo e não foi validada contra toda a classe ou contra o macOS.
- Wine executa alguns programas Windows em espaço de usuário. Não executa drivers Windows nem garante compatibilidade geral.

## Desenvolvimento

Leia `docs/PROJECT.md`, `docs/PROTOTYPE.md`, `docs/RELEASES.md` e `docs/USB-AUDIO.md` antes de tentar instalar. Mantenha qualquer teste numa máquina virtual descartável. A compatibilidade de áudio USB depende do dispositivo, e a instalação completa, o primeiro login, KDE e Wine ainda precisam ser validados.
