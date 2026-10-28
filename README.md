# Brasa OS — protótipo de instalador

Brasa é um protótipo x86-64 baseado em FreeBSD. O objetivo é oferecer uma instalação gráfica simples, KDE preservado, Wine e suporte a interfaces de áudio USB class-compliant. Ainda não está pronto para instalar num computador de uso diário.

## Estado da imagem experimental mais recente

A ISO local mais recente é r28 (`.build/Brasa-live-r28-fd-fix-2026-10-28.iso`). O r27 confirmou que o seletor gráfico e a instalação da base/kernel local funcionam, mas revelou `Bad fd number` ao copiar o catálogo no script pós-instalação: `/bin/sh` não aceita os descritores 10 e 11. A r28 troca por 4 e 5; o build passou, mas o ensaio gráfico não confirmou a correção. KDE instalado, primeiro boot, Wine e áudio USB em hardware real seguem sem validação. Consulte `docs/RELEASES.md` para hash e resultados. As imagens são experimentais; não use num computador com dados importantes. JWM é somente o ambiente temporário do instalador; KDE continua sendo o desktop pretendido no sistema instalado. Consulte `docs/PROTOTYPE.md` antes de testar.

## O que funciona nesta mídia

- A instalação no disco virtual ainda não concluiu o pós-instalação; r27 confirmou o fluxo até a configuração do sistema, e r28 ainda não validou o ajuste.
- Inclui o pacote Brasa em `/BRASA/BRASA_PROJECT_TAR_GZ` e `snd_uaudio.ko` no kernel.
- KDE instalado, Wine, áudio USB físico e primeiro boot continuam sem validação.

## Limitações conhecidas

- A instalação da base FreeBSD e a configuração do desktop ainda não foram concluídas pelo assistente gráfico.
- `scripts/brasa-install-assistant` tem etapas visuais para conta, senha, seleção de disco e confirmação destrutiva. O instalador processou os componentes live, mas ainda não foi validado até o primeiro boot.
- A instalação e o primeiro login ainda precisam ser validados num ambiente live real antes de usar em um computador com dados importantes.
- O driver FreeBSD `uaudio` fornece suporte a parte dos dispositivos USB Audio Class; a compatibilidade depende do dispositivo e não foi validada contra toda a classe ou contra o macOS.
- Wine executa alguns programas Windows em espaço de usuário. Não executa drivers Windows nem garante compatibilidade geral.

## Desenvolvimento

Leia `docs/PROJECT.md`, `docs/PROTOTYPE.md`, `docs/RELEASES.md` e `docs/USB-AUDIO.md` antes de tentar instalar. Mantenha qualquer teste numa máquina virtual descartável. A compatibilidade de áudio USB depende do dispositivo, e a instalação completa, o primeiro login, KDE e Wine ainda precisam ser validados.
