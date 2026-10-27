# Brasa OS — protótipo de instalador

Brasa é um protótipo x86-64 baseado em FreeBSD. O objetivo é oferecer uma instalação gráfica simples, KDE preservado, Wine e suporte a interfaces de áudio USB class-compliant. Ainda não está pronto para instalar num computador de uso diário.

## Estado da imagem experimental mais recente

A [ISO experimental com JWM](https://github.com/Mateus-Neinas/brasaOS/releases/tag/brasa-jwm-live-boot-2026-10-27) inicializa em uma VM com 4 GB e exibe as telas do assistente legivelmente. O teste chegou às telas de credenciais, mas a confirmação de senha falhou durante a entrada por teclado remoto; a seleção do disco e a instalação ainda não foram verificadas nesta variante. O menu padrão do FreeBSD continua disponível. Consulte `docs/RELEASES.md` e `docs/PROTOTYPE.md` antes de testar.

## O que funciona nesta mídia

- Inicia o instalador padrão do FreeBSD pelo menu **Boot Brasa**; também tenta abrir o assistente gráfico experimental.
- Permite testar a base FreeBSD e consultar o pacote Brasa em `/BRASA/BRASA_PROJECT_TAR_GZ`.
- Inclui o assistente gráfico Brasa e tenta iniciá-lo no ambiente live.
- O KDE, Wine e os aplicativos de áudio pertencem ao sistema instalado e ainda não foram validados nesta ISO.

## Limitações conhecidas

- A instalação da base FreeBSD ainda não foi concluída pelo assistente gráfico.
- `scripts/brasa-install-assistant` tem etapas visuais para conta, senha, seleção de disco e confirmação destrutiva, com o backend planejado para `bsdinstall`. A tela do assistente agora está legível com JWM, mas a passagem pelas credenciais, a seleção de disco e a instalação completa ainda precisam de validação.
- A instalação e o primeiro login ainda precisam ser validados num ambiente live real antes de usar em um computador com dados importantes.
- O driver FreeBSD `uaudio` fornece suporte a parte dos dispositivos USB Audio Class; a compatibilidade depende do dispositivo e não foi validada contra toda a classe ou contra o macOS.
- Wine executa alguns programas Windows em espaço de usuário. Não executa drivers Windows nem garante compatibilidade geral.

## Desenvolvimento

Leia `docs/PROJECT.md`, `docs/PROTOTYPE.md`, `docs/RELEASES.md` e `docs/USB-AUDIO.md` antes de tentar instalar. Mantenha qualquer teste numa máquina virtual descartável. A compatibilidade de áudio USB depende do dispositivo, e a instalação completa, o primeiro login, KDE e Wine ainda precisam ser validados.
