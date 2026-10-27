# Brasa OS — mídia de desenvolvimento

Brasa é um protótipo x86-64 baseado em FreeBSD. Esta ISO é a imagem **bootonly do instalador FreeBSD 15.1**, com os arquivos de desenvolvimento Brasa anexados. Ela **não é um instalador gráfico Brasa pronto para uso** e não deve ser usada para instalar o desktop Brasa num computador de produção.

## O que funciona nesta mídia

- Inicia o instalador padrão do FreeBSD pelo menu **Boot Brasa**.
- Permite testar a base FreeBSD e consultar o pacote Brasa em `/BRASA/BRASA_PROJECT_TAR_GZ`.
- Inclui o código-fonte do assistente gráfico Brasa, mas não o instala no ambiente live.
- Não contém sessão live gráfica, KDE, Wine ou repositório local de pacotes.

## Limitações conhecidas

- A instalação da base FreeBSD acontece em menus de texto.
- `scripts/brasa-install-assistant` tem etapas visuais para conta, senha, seleção de disco e confirmação destrutiva, com o backend planejado para `bsdinstall`. Ele ainda exige um ambiente live com Zenity e um marcador especial, ausentes nesta ISO; portanto não inicia a partir desta mídia.
- A instalação e o primeiro login ainda precisam ser validados num ambiente live real antes de usar em um computador com dados importantes.
- O driver FreeBSD `uaudio` fornece suporte a parte dos dispositivos USB Audio Class; a compatibilidade depende do dispositivo e não foi validada contra toda a classe ou contra o macOS.
- Wine executa alguns programas Windows em espaço de usuário. Não executa drivers Windows nem garante compatibilidade geral.

## Desenvolvimento

Leia `docs/PROJECT.md`, `docs/PROTOTYPE.md` e `docs/USB-AUDIO.md` antes de tentar instalar. Mantenha qualquer teste de instalação numa máquina virtual descartável. Esta mídia é para desenvolvimento; ela ainda não instala Brasa com a facilidade de um instalador de Mac.
