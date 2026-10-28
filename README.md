# Brasa OS — protótipo de instalador

Brasa é um protótipo x86-64 baseado em FreeBSD. O objetivo é oferecer uma instalação gráfica simples, KDE preservado, Wine e suporte a interfaces de áudio USB class-compliant. Ainda não está pronto para instalar num computador de uso diário.

## Estado da imagem experimental mais recente

A ISO local mais recente é r16, com marcadores de subetapas em `bsdinstall config`. Em QEMU/WHPX com 8 GiB, 4 vCPUs e VirtIO GPU 128 MiB, o assistente gráfico confirmou um QCOW2 descartável de 40 GiB e extraiu base/kernel; depois ficou em `bsdconfig` por 10 minutos, sem gravações no disco desde 00:28. Os novos marcadores não apareceram e a instalação não concluiu. KDE após instalação, primeiro boot, Wine e áudio USB em hardware real não foram validados. Consulte `docs/RELEASES.md` para hash e resultado. As imagens são experimentais; não use num computador com dados importantes. JWM é somente o ambiente temporário do instalador; KDE continua sendo o desktop pretendido no sistema instalado. Consulte `docs/PROTOTYPE.md` antes de testar.

## O que funciona nesta mídia

- A r16 inicia o assistente gráfico, confirma o disco virtual de teste e extrai base/kernel; a instalação não chegou ao fim.
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
