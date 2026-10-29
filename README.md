# Brasa OS — protótipo de instalador

Brasa é um protótipo x86-64 baseado em FreeBSD. O objetivo é oferecer instalação gráfica simples, desktop KDE, suporte a áudio USB class-compliant e execução de alguns aplicativos Windows por Wine. Ainda não está pronto para instalar num computador de uso diário.

## Estado da ISO

A release publicada de referência continua sendo `alpha_1.37`. A candidata USB híbrida 1.45 está em `.build/Brasa-live-alpha_1.45-rge-link-recovery-hybrid.iso` e em `Downloads/Brasa-alpha_1.45-rge-link-recovery-hybrid.iso` (1.285.331.456 bytes; SHA-256 `AFBFE52B9670C63CD337B44F469B25EF4980C40AF4D173C43431561A931A6BE4`). QEMU UEFI abriu o assistente gráfico; depois, o usuário confirmou instalação física bem-sucedida e início do KDE. Candidatas intermediárias ficam no histórico do código, sem releases ou assets ISO.

O usuário confirmou que a instalação física da candidata 1.45 terminou e iniciou o KDE. A RX 6600 não iniciou aceleração; comandos manuais seguidos de reboot deixaram a tela preta. O áudio analógico frontal funcionou; HDMI e USB ainda precisam de teste. Essa validação é do resultado relatado pelo usuário, não de um teste automatizado local.

A próxima candidata separa recursos opcionais do fluxo de instalação: o primeiro login KDE oferece automaticamente o assistente “Aplicar extras do Brasa”, que também fica no menu. Ele instala Firefox, PipeWire/WirePlumber, ferramentas de áudio e Wine depois de o sistema já iniciar. Assim a extração desses pacotes não ocorre durante a instalação do sistema base. O assistente pede a senha administrativa numa janela Konsole e mostra o progresso dos pacotes. O app de teste de áudio passa a mostrar o resultado em uma janela gráfica, sem abrir Konsole. Em UEFI, o KMS AMD segue desativado; o assistente instala apenas o firmware da RX 6600 e não aplica comandos que já deixaram a tela preta.

A candidata híbrida `Brasa-beta_1.1.iso` está em `Downloads/Brasa-beta_1.1.iso` (1.285.335.552 bytes; SHA-256 `3D1026D73B7FB8486CCAB3B09B87F161FE09A3E1F97DCA608DA62211C6209293`). No QEMU, iniciou por USB virtual, recebeu rede e abriu o instalador; não foi conectada unidade de destino. A instalação e o assistente de primeiro login desta nova candidata ainda não foram repetidos.

O desktop KDE Plasma continua sendo o desktop instalado pretendido. O módulo `snd_uaudio` está habilitado, mas dispositivos USB Audio Class ainda não foram testados em equipamento físico. O assistente de extras precisa de internet no primeiro login.

O Windows identifica a Ethernet física deste PC como Realtek RTL8125 (`PCI 10EC:8125`). A candidata inclui `realtek-rge-kmod`; o manual [`rge(4)` do FreeBSD 15.1](https://man.freebsd.org/cgi/man.cgi?query=rge&manpath=FreeBSD+15.1-RELEASE+and+Ports.quarterly) lista RTL8125/8125B. O usuário confirmou que conseguiu instalar a 1.45 e entrar no KDE no computador real.

## Objetivos e limitações

- KDE Plasma continua sendo o desktop instalado pretendido.
- Wine oferece compatibilidade parcial com aplicativos Windows; não executa drivers Windows.
- O driver FreeBSD `uaudio` cobre parte dos dispositivos USB Audio Class, sem garantia universal nem paridade com macOS.
- Áudio USB e HDMI, aceleração AMD, compatibilidade de aplicativos Windows e o novo assistente de extras beta_1.1 ainda precisam de validação.

Leia `docs/PROJECT.md`, `docs/PROTOTYPE.md`, `docs/RELEASES.md` e `docs/USB-AUDIO.md`. A ISO beta_1.1 é candidata local; o QEMU foi iniciado sem disco de destino para verificar o boot e abrir o instalador.
