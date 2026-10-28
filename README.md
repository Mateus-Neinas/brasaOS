# Brasa OS — protótipo de instalador

Brasa é um protótipo x86-64 baseado em FreeBSD. O objetivo é oferecer uma instalação gráfica simples, KDE preservado, Wine e suporte a interfaces de áudio USB class-compliant. Ainda não está pronto para instalar num computador de uso diário.

## Estado da imagem experimental mais recente

A r9 retoma o cache live da r7 com fallback de rede e abre o assistente gráfico. Em QEMU, chegou à confirmação do disco virtual e extraiu base/kernel locais; o teste de 10 minutos terminou na configuração do KDE, sem concluir a instalação. A r8 sem cache falhou antes do gráfico ao tentar copiar `/usr/local` para ele mesmo. O KDE instalado foi reduzido para Plasma Desktop com KWin X11 e Breeze, SDDM, Dolphin, Konsole, Ark, áudio USB e Wine. No catálogo anterior, a estimativa cai de 960 para 683 pacotes e de 2.359 para 1.378 MiB; isso não é uma medição real de download ou de duração. Primeiro boot, KDE instalado, Wine e interfaces USB físicas não foram validados. Consulte `docs/RELEASES.md` para hashes e resultados. As imagens são experimentais; não use num computador com dados importantes. JWM é somente o ambiente temporário do instalador; KDE continua sendo o desktop pretendido no sistema instalado. Consulte `docs/PROTOTYPE.md` antes de testar.

## O que funciona nesta mídia

- A r9 inicia o assistente gráfico, confirma o disco virtual de teste e extrai base/kernel; a instalação não chegou ao fim.
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
