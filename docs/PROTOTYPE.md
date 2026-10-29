# Instalador Brasa — plano e estado verificável

## Meta de produto

Iniciar por uma mídia x86-64, escolher idioma, informar o nome e a senha da conta, selecionar o disco mostrando claramente modelo e tamanho e confirmar uma única vez a operação destrutiva. Depois, instalar o sistema, configurar desktop e conta, e reiniciar na tela de login. O mesmo segredo para conta pessoal e administração só deve ser oferecido com explicação clara; nenhum segredo deve ser predefinido ou gravado em texto simples.

## Estado atual

### Candidata local alpha_1.38-rge-diagnostics (29/10/2026)

A ISO híbrida `.build/Brasa-live-alpha_1.38-rge-diagnostics-final-hybrid.iso` (1.285.317.120 bytes; SHA-256 `DC8634C33FFCEAE7C09768D71971EBAC092DFA1960496B15B13741247BCA234B`) amplia a tela de recuperação: tenta mostrar o estado do módulo `if_rge`, procura mensagens de associação do RTL8125 no log do kernel e inclui falhas de carregamento no resumo DHCP. Isso separa placa ausente no PCI, driver sem associação e driver associado sem link/DHCP. O builder validou o pacote do driver/ABI e a estrutura híbrida; a verificação de sintaxe dos scripts passou. A última execução do conjunto de smoke checks ficou presa em um teste simulado de áudio aguardando uma resposta do `zenity`; o teste anterior tinha passado.

Em QEMU TCG com 8 GiB, 4 vCPUs, VGA padrão de 128 MiB e e1000/NAT, a imagem híbrida iniciou por USB em BIOS, recebeu DHCP, preparou os pacotes e abriu a confirmação gráfica “Instalar Brasa”. Um QCOW descartável de 40 GiB foi conectado, mas o teste não avançou além da tela inicial e não iniciou a instalação; o QCOW não recebeu gravações e foi removido. Um boot novo da imagem final híbrida repetiu o caminho BIOS/USB e abriu o assistente gráfico. Isso verifica o live e a abertura do assistente, não uma instalação concluída, UEFI ou a associação do `rge` à placa física; a nova tela de diagnóstico ainda não foi acionada por um erro de rede real.

Não será publicada outra release antes da alpha final validada no PC real. A release `alpha_1.37` é a única referência a manter no GitHub; a limpeza de `alpha_1.37b` e a remoção de ISOs locais sem progresso continuam pendentes. O teste UEFI QEMU não iniciou porque a distribuição local do QEMU não inclui o arquivo de variáveis OVMF x86-64.

### Candidata local alpha_1.37g-network-diagnostics: boot USB e diagnóstico DHCP (29/10/2026)

A candidata inclui a mídia híbrida `.build/Brasa-live-alpha_1.37g-network-diagnostics-hybrid.iso` (1.285.308.928 bytes; SHA-256 `3F5B2C09864F645949EB3C0DA59CEF188E628F097649BC425BFEFBED6491E6E4`). O contêiner híbrido foi construído a partir da ISO óptica com GPT/MBR e catálogo El Torito. QEMU iniciou a própria imagem híbrida como dispositivo USB de armazenamento, exibiu o menu `Boot Brasa`, obteve DHCP e abriu a tela gráfica “Instalar Brasa”. Não havia disco de destino conectado e nenhuma instalação foi iniciada.

O início do `dhclient` live passou a rodar em modo foreground sob controle do bootstrap, registrando as mensagens DHCP no log recuperável. A tela de recuperação agora cabe no console e mostra a etapa que falhou, interface, estado de link, rota, DNS, PCI de rede e últimas respostas DHCP. Ao falhar, o live mantém essa tela em vez de cair silenciosamente no instalador texto do FreeBSD.

Testes de rede separados com a NIC virtual `e1000`: no VMware Workstation com NAT e 6 GiB, DHCP recebeu `192.168.102.129`, o catálogo FreeBSD foi atualizado, os pacotes gráficos foram completados e a tela “Instalar Brasa” abriu. A imagem ficou nessa primeira tela; não houve instalação. No VMware com bridge, `em0` ficou `active`, mas o cliente recebeu três `DHCPDISCOVER` e nenhum `DHCPOFFER`. No VirtualBox com NAT, `em0` ficou `no carrier` e a tela mostrou ausência de rota/DNS. Esses dados descrevem cada configuração virtual e não determinam ainda o que acontece com a NIC física do computador.

O inventário do Windows neste mesmo PC identificou a Ethernet física como Realtek RTL8125, PCI `10EC:8125` (subsystem `1043:87D7`, revisão 05). O [`rge(4)` do FreeBSD 15.1](https://man.freebsd.org/cgi/man.cgi?manpath=FreeBSD+15.1-RELEASE&query=rge&sektion=4) documenta suporte ao RTL8125/8125B; a candidata inclui `realtek-rge-kmod` com `if_rge.ko`. Isso alinha o driver empacotado ao hardware conhecido, mas ainda falta observar o attach do módulo, estado do link e DHCP no boot bare-metal.

No Windows deste PC, a mesma interface está `Up`, link 1 Gbps, DHCP habilitado e com IPv4, gateway e DNS. Assim, o cabo e a rede do host estão operacionais no Windows; isso não comprova que o `rge` anexará à placa no Brasa.

A ISO híbrida continua local, sem release, até validação na máquina física e instalação em disco virtual seguida do primeiro boot KDE. A ISO 1.37c e anteriores não foram alteradas. Os testes usaram mídia somente de leitura; nenhum disco de instalação foi anexado. O candidato óptico intermediário está em `.build/Brasa-live-alpha_1.37g-network-diagnostics.iso`.

### Candidata local alpha_1.37e-ethernet: Bluetooth opcional no live (28/10/2026)

A imagem `.build/Brasa-live-alpha_1.37e-ethernet.iso` parte do construtor Ethernet da 1.37d e substitui `/etc/devd/bluetooth.conf` apenas na mídia live, evitando que `devd` inicie automaticamente a pilha HCI de adaptadores Bluetooth opcionais. Isso não desativa os drivers USB HID de teclado e mouse. A instalação no disco recebe os arquivos upstream do FreeBSD; esse ajuste é exclusivo do ambiente live.

Em QEMU 11.1 com TCG, 8 GiB de RAM, 4 vCPUs, VGA padrão de 128 MiB e e1000, a ISO obteve DHCP, rota e DNS, baixou os 291 MiB ausentes do cache e abriu automaticamente a tela “Instalar Brasa”, sem escolher `Live System` nem entrar no instalador padrão do FreeBSD. Nenhuma instalação foi iniciada. O teste WHPX falhou antes da tela com `Unexpected VP exit code 4`; foi repetido com TCG. O QEMU foi encerrado sem disco virtual conectado.

O resultado confirma o fluxo de software com a NIC e1000 virtual, não a Ethernet física desta máquina nem o comportamento de um adaptador Bluetooth específico. O erro HCI observado na foto não é uma dependência necessária do assistente: o código de boot segue para rede e pacotes depois do início do sistema; o menu padrão aparece quando o bootstrap Brasa termina com erro. A candidata não foi publicada enquanto o teste físico de rede e a instalação completa não forem confirmados. Tamanho: 1.285.304.832 bytes; SHA-256 `D198AE36A7AC5C2B854DA6AC8CB70D0DC1FA0D8C5DEC3C9195D9A4F158811A0F`.

### Candidata local alpha_1.37d-ethernet: Ethernet automática (28/10/2026)

A imagem híbrida `.build/Brasa-live-alpha_1.37d-ethernet.iso` foi construída como candidata nova a partir do conteúdo da 1.37c, sem sobrescrever a 1.37c ou releases anteriores. Ela inclui o módulo FreeBSD `if_rge.ko` da ABI FreeBSD 15 para RTL8125/8126/8127 e inicia `devmatch` para carregar drivers do kernel que correspondam ao hardware. O boot tenta DHCP em todas as interfaces cabeadas que o FreeBSD identifica por `media: Ethernet`, valida a rota padrão e o DNS e usa tentativas curtas para não travar em portas sem cabo.

Teste QEMU pelo USB storage híbrido, 6 GiB, 2 vCPUs, VGA de 128 MiB, QEMU TCG e rede user-mode com placa virtual e1000. Depois de escolher `Live System` no menu inicial do FreeBSD, o sistema reconheceu `em0`, obteve DHCP, rota e DNS, atualizou os catálogos FreeBSD e baixou dependências ausentes. O assistente gráfico “Instalar Brasa” abriu na tela inicial. Nenhuma instalação foi iniciada; o QCOW2 descartável foi removido.

A instalação local dos pacotes gráficos tentou o cache e teve 10 pacotes recusados; o fallback online atualizou o catálogo e baixou 291 MiB. Assim, a rede e o caminho online foram verificados, mas o boot ainda depende da opção `Live System` no menu FreeBSD e o caminho de cache local pode ser melhorado. O driver extra RGE foi empacotado e carregado no teste, mas não foi conectado a um hardware RTL8125 real. O teste e1000 confirma o DHCP genérico, não compatibilidade física com toda placa Ethernet. O tamanho da ISO híbrida é 1.285.302.784 bytes; SHA-256 `A567AABC7D1DF327BBC281B5098FA886D1C6E1C1D76B26AC9975C47404325F1B`.

O SHA-256 da ISO óptica de referência 1.37c continuou `E2F0EE43BCEED2685502F4837E937B33B5176B03B0DC3BC29708B3A31845CB4`; a ISO híbrida 1.37c continuou `0CCCC9A4A17CC64FD6289FB41B259B6CE8870E9EABF6D536709C58CFB2D013BB`. O FreeBSD não possui um driver único universal: esta candidata usa a cobertura dos drivers FreeBSD GENERIC/devmatch e acrescenta o módulo RGE; outros chipsets sem driver FreeBSD compatível ainda exigirão módulo ou port específico.

### Correção candidata para o boot em máquina real (28/10/2026)

Na ISO alpha_1.37b, o boot físico ficou cerca de 20 minutos na mensagem “Preparando o espaço temporário para os componentes gráficos”. A função `say()` imprimia primeiro em `/dev/console` e depois abria `/dev/ttyu0` sempre que o nó serial existia. A mera existência desse nó não garante que haja um terminal conectado; a abertura de um TTY pode esperar pela portadora. Isso é uma causa plausível para a mensagem aparecer na tela enquanto o script para antes de executar `kldload tmpfs` ou montar `/usr/local`. Os avisos de ACPI, Bluetooth MediaTek e gravações recusadas pela raiz live somente leitura não identificam essa espera.

O código removeu as escritas diretas em `/dev/ttyu0` do início live e dos diagnósticos/progresso do instalador. A mensagem foi dividida em carregamento do módulo, montagem e conclusão do `tmpfs`, para mostrar precisamente a próxima etapa. A primeira candidata óptica de 1.284.984.832 bytes foi mantida como `.build/Brasa-live-alpha_1.37c-optical.iso`. Depois, `build-brasa-memstick.py` gerou `.build/Brasa-live-alpha_1.37c.iso` como imagem híbrida (1.285.001.728 bytes; SHA-256 `0cccc9a4a17cc64fd6289fb41b259b6ce8870e9eabf6d536709c58cfb2d013bb`). A verificação confirmou assinatura MBR, partição protetora, cabeçalho GPT, ISO9660 e scripts live atualizados sem aberturas diretas de `ttyu0`. Ainda falta iniciar esta candidata em QEMU e em máquina real; ela não foi publicada como release.

### r36: instalação concluída; primeiro boot pendente (28/10/2026)

A ISO `.build/Brasa-live-r36-install-progress-2026-10-28.iso` concluiu a instalação em QCOW2 de 40 GiB no QEMU com WHPX, 8 GiB de RAM, 4 vCPUs e VirtIO GPU de 128 MiB. Base/kernel local, conta, KDE Plasma, componentes de áudio e Wine foram instalados. A confirmação do assistente apareceu após cerca de 7 minutos. A barra e o texto acompanharam a extração de pacotes KDE e a instalação de Wine.

O primeiro boot pelo QCOW não chegou à tela de login gráfica. Após mensagens iniciais do kernel, a captura ficou preta e QEMU continuou ativo; a saída serial não trouxe dados. VGA padrão repetiu o mesmo resultado, então o problema não parece exclusivo do driver VirtIO. A comparação TCG também ficou preta, indicando que a falha não é específica ao acelerador WHPX. Causa ainda desconhecida. O QCOW fica em `%TEMP%\Brasa-r36-test.qcow2`, e a janela QEMU permanece aberta sem a ISO conectada. Nenhuma unidade física foi usada. KDE está instalado no destino, mas início de sessão, Wine funcional e áudio USB físico seguem sem validação.

A r36 também transmite a linha mais recente do script de pós-instalação para o progresso gráfico enquanto ele roda e remove diagnósticos seriais temporários. O instalador completo e a atualização da linha foram validados em QEMU; o primeiro boot continua sendo o bloqueio atual.

### Boot live e progresso visível (27/10/2026)

O teste com cache confirmou que a criação de um TAR de `/usr/local` no boot acrescentava uma cópia temporária de mais de 2 GB e trabalho extra em RAM. O script agora semeia o tmpfs diretamente dos pacotes incluídos na ISO e remove a cópia temporária depois, evitando gerar e depois desempacotar esse arquivo adicional. A janela do instalador agora usa o log do `bsdinstall` como texto principal e, se uma etapa não emitir linhas, mantém uma mensagem com o tempo decorrido em vez de parecer congelada.

A imagem `.build/Brasa-live-optimized-experimental.iso` preserva o boot da ISO Brasa existente, inclui a atualização e os pacotes cacheados, mede 1.305.520.128 bytes e tem SHA-256 `6D7DA61286CA0887F23576DDB25F87107176F97CFAE2398DE416D9D57192FCC3`. O QEMU usado para a inspeção foi iniciado com 8 GB de RAM e VGA de 128 MB; WHPX não funciona neste host, então o emulador usou TCG. O boot chegou à instalação de componentes e começou a extrair o pacote 57/191, mas ainda levou minutos em emulação por software. A tela de boas-vindas não apareceu nesta execução, o QCOW2 ficou em 197.632 bytes e foi removido após encerrar a VM. Nenhuma instalação de sistema ou alteração de disco foi feita.

Teste posterior documentado abaixo: no QEMU 11.1 deste host, WHPX com VGA padrão falha ao abrir o X; o driver VirtIO GPU FreeBSD elimina esse erro e abre a interface. O resultado não altera a compatibilidade de hardware real nem conclui a instalação.

O instalador gráfico seleciona o disco em uma janela e apresenta modelo, capacidade, identificador e confirmação explícita; depois usa `bsdinstall scriptedpart` para criar automaticamente o esquema de boot e as partições. Essa instalação real ainda não foi concluída. O acompanhamento do processo foi ajustado para reconhecer subprocessos encerrados, inclusive zumbis, em vez de deixar a barra aguardando um PID que já terminou. Essa correção está no código-fonte e exige uma nova ISO para validação em QEMU.

A ISO permanece experimental: KDE, instalação no disco, primeiro login, Wine e interfaces USB de áudio ainda não foram validados. Não instale em um disco real.

### r27–r28: descritores do script pós-instalação (28/10/2026)

No teste r27, o assistente abriu, aceitou a conta e listou somente `vtbd0` de 40 GiB, o QCOW descartável. Após a confirmação, o particionamento e a extração da base/kernel incluídos na ISO terminaram. O script de configuração falhou ao copiar o catálogo: `/tmp/installscript: 14: Syntax error: Bad fd number`. A linha 14 redirecionava `<&10`; o script também lia `<&11`. O `/bin/sh` do FreeBSD suporta descritores até 9. Isso identifica uma falha concreta do script de Brasa, depois da etapa `bsdinstall config`, não uma espera normal do `bsdconfig`.

A r28 altera esses descritores para 4 e 5 e foi compilada. O teste iniciou QEMU, mas a captura alternou entre o console e uma tela preta antes de confirmar a interface; por isso, a correção ainda não foi validada em instalação. O QCOW r27 e r28 foi descartado após cada tentativa; somente a ISO r28 permanece local. O próximo teste precisa confirmar a janela gráfica, repetir a instalação em QCOW descartável e verificar a criação do usuário e o bootstrap do desktop.

### r20–r21: erro explícito no pós-instalação (28/10/2026)

O diagnóstico de processos na r20 encontrou `bsddialog --title "Installation Error!"` consumindo CPU enquanto a janela Zenity de progresso o ocultava. Ao dispensar o progresso, o assistente Brasa informou que a instalação não terminou. A base/kernel e as etapas marcadas de `bsdinstall config` haviam terminado; a falha surgiu ao entrar na execução do script de pós-instalação. A mensagem exata do `bsdinstall.log` não foi preservada nessa execução. Portanto, a espera observada não é uma demora normal documentada: havia uma falha explícita escondida.

A r21 moveu o shebang para o início, mas essa mudança isolada fez as variáveis `PARTITIONS` e `DISTRIBUTIONS` deixarem de ser lidas pelo `bsdinstall`; a r22 restaurou o preâmbulo antes do shebang e a extração local de `base.txz`/`kernel.txz` voltou a funcionar. A falha capturada na r27 foi posterior e diferente: descritores 10/11 inválidos no `/bin/sh` do sistema-alvo. A correção r28 ainda aguarda validação gráfica e de instalação.

A documentação oficial diz que o `bsdinstall` exibe etapas de configuração após extrair as distribuições, e a implementação-fonte define um diálogo genérico para falhas de script; não descreve o diálogo como espera prolongada. Fontes: [FreeBSD Handbook — Installing FreeBSD](https://docs.freebsd.org/en/books/handbook/bsdinstall/), [código-fonte do bsdinstall](https://cgit.freebsd.org/src/tree/usr.sbin/bsdinstall/scripts/auto?id=5870d6a1ef4ec5d6fc91d0f1635bca59e09a040d) e [manual bsdinstall(8)](https://man.freebsd.org/cgi/man.cgi?manpath=freebsd-current&query=bsdinstall&sektion=8).

### r17: rastreio do script pós-instalação (28/10/2026)

A imagem acrescenta marcadores antes/depois das operações de cópia, permissão, execução e limpeza do script pós-instalação. No QEMU 11.1/WHPX (8 GiB, 4 vCPUs, VirtIO GPU 128 MiB), com somente um QCOW2 descartável de 40 GiB, a instalação gráfica abriu, aceitou conta/senha e confirmou `vtbd0`. A instalação local da base e do kernel terminou. A tela saiu de `bsdconfig` e mostrou o marcador “Iniciando a configuração do Brasa no sistema instalado”, que indica o começo do `chroot` do script. Ficou nessa subetapa por 624 s; os marcadores de retorno e limpeza não apareceram na tela nem no log serial. O QCOW não teve novas gravações durante a etapa (contador final de escrita QMP: 1.266.222.592 bytes). QEMU chegou a cerca de 6,3 GiB de RAM e foi encerrado; o QCOW descartável foi removido. O teste não concluiu o sistema nem iniciou o KDE.

Essa medição mostra que a demora não ficou restrita à tela rotulada `bsdconfig`: a interface avançou para a configuração pós-instalação, mas ainda não identifica qual comando está consumindo tempo. As fontes oficiais consultadas descrevem que o tempo de instalação varia com componentes, mídia e computador, e que `bsdconfig` é uma biblioteca de rotinas shell chamada por `bsdinstall`; não documentam uma espera normal de vários minutos nessa subetapa. Não encontrei relato verificável de que essa etapa costume demorar tanto. Isso não prova que a demora seja anormal em todas as máquinas, mas não há evidência para tratá-la como normal. Próxima investigação: capturar processos e conteúdo de `/tmp/brasa-install-phase` dentro do live durante essa espera, e verificar se a chamada do script pós-instalação foi alcançada.

Fontes: [FreeBSD Handbook — Installing FreeBSD](https://docs.freebsd.org/en/books/handbook/bsdinstall/) e [FreeBSD Foundation — Installer Usability](https://freebsdfoundation.org/our-work/journal/browser-based-edition/networking-3/installer-usability/).

### r18: reexibir a saída do bootstrap (28/10/2026)

O r18 corrige a mensagem de progresso que ficava fixa ao entrar no script pós-instalação; agora ela acompanha a última linha do instalador/`pkg` e os contadores de pacotes. No reteste, o assistente iniciou, confirmou só o QCOW2 `vtbd0` de 40 GiB e terminou de extrair a base/kernel locais em cerca de um minuto. Depois ficou em `bsdconfig` por 632 s, sem alteração do contador de gravação (QCOW em 1.261.305.856 bytes). QEMU usou cerca de 6,3 GiB de RAM e CPU acumulada continuou crescendo. O teste foi encerrado e o QCOW removido pelo limite de dez minutos. Assim, o gargalo r18 é anterior ao bootstrap; a correção do texto ainda não foi exercitada. O r17, em outra execução, avançou até o início do script pós-instalação em cerca de um minuto e ficou naquela subetapa por 624 s. A diferença confirma comportamento variável no trecho `bsdconfig`; a extração local da base/kernel não foi a espera longa nos testes r17/r18.

A saída que a interface chama `bsdconfig` ainda não revela o subcomando interno que consome CPU, e os marcadores dentro de `bsdinstall config` não foram mostrados. O próximo passo é obter o estado/processo dentro do live durante essa janela, além de preservar as linhas do bootstrap na interface quando a configuração chegar a essa fase.

### Progresso de extração de pacotes e reteste da base (27/10/2026)

O bootstrap do sistema instalado foi reduzido para o conjunto essencial do KDE Plasma (`plasma6-plasma`, Konsole, Dolphin e Ark), mantendo o KDE, SDDM, Xorg, `drm-kmod` e Zenity. O leitor de progresso também interpreta os contadores `[atual/total]` emitidos por `pkg` durante instalação e extração; a saída de serial mostrou esses contadores nos 133 componentes gráficos do ambiente live.

Na ISO `.build/Brasa-live-whpx-virtio-package-progress.iso`, QEMU 11.1/WHPX (8 GB, 4 vCPUs, VirtIO GPU) abriu o ambiente live e o assistente. Por teclado foram preenchidos os dados da conta, selecionado `vtbd0` de 40 GB e confirmada a instalação no QCOW2 descartável. O catálogo local foi atualizado, os pacotes live foram extraídos e a base `base.txz` (156 MB) foi baixada. Depois, a tela ficou sem nome de etapa e apenas atualizou o tempo decorrido; o QCOW2 chegou a 1.261.633.536 bytes alocados (1.270.431.744 bytes escritos), mas os contadores de I/O ficaram parados por mais de quatro minutos, enquanto a CPU do QEMU continuava aumentando. Encerramos a VM. Não foi possível determinar se a demora era descompressão, configuração ou bloqueio; a instalação, o primeiro boot e a sessão KDE não foram validados.

O QCOW2 deste teste permanece em `%TEMP%` até a próxima ISO ser versionada. A imagem base `dist/Brasa-15.1-amd64.iso` foi preservada. O ajuste da etapa de pacotes é experimental e a ausência de uma descrição útil durante a etapa da base continua aberta.

### WHPX com driver VirtIO GPU e extração (27/10/2026)

A variante `Brasa-live-whpx-virtio-test.iso` adiciona à mídia o módulo oficial `virtio-gpu-qemu-kmod` compatível com FreeBSD 15.1, configura o carregamento no início do boot e usa `xf86-video-scfb` para expor o framebuffer ao X. Isso resolveu o fechamento do QEMU que acontecia com VGA padrão. O pacote foi baixado de `pkg.freebsd.org` e validado por SHA-256 fixado no construtor.

No QEMU 11.1 em Windows 11, com WHPX, 6 GB de RAM, 4 vCPUs e VGA VirtIO, o boot chegou ao live gráfico, formulário de conta, lista do disco `vtbd0` de 40 GB e confirmação final. Após a confirmação, o QCOW2 cresceu até 1.261.961.216 bytes e a tela de progresso chegou a 97%. O texto exibiu `DEBUG: f_getvar: var=[width] value=[97]`, que é uma mensagem interna de `bsdinstall` (o valor 97 é a largura do terminal, não o progresso da instalação). A janela ficou nesse estado por quase sete minutos e o arquivo QCOW2 não recebeu novas gravações desde 17:37:10; o QEMU usou aproximadamente 5,9 GB de RAM e sua CPU avançou continuamente. Encerramos a VM por QMP para poupar recursos. O disco não foi apagado e permanece temporariamente em `%TEMP%` até a próxima release ser publicada.

O resultado comprova que a interface gráfica e a confirmação do disco funcionam com WHPX/VirtIO, mas não comprova a instalação da base nem do KDE. Não foi possível determinar se a última etapa é a cauda da extração da base ou sua configuração seguinte. O próximo ISO filtra linhas `DEBUG:` da caixa de progresso e mostra uma mensagem compreensível; será preciso retestar a instalação para identificar se a espera é trabalho lento ou bloqueio. Nenhum disco físico foi conectado.


### Cache dos componentes gráficos na mídia (27/10/2026)

O teste de boot da ISO compacta mostrou que, sem cache, o ambiente baixa 191 pacotes a cada inicialização. Uma segunda tentativa acumulou cerca de 8,3 GB de memória no processo QEMU e deixou só 0,3 GB livres no Windows enquanto usava TCG; encerramos o QEMU antes de iniciar a instalação. O disco QCOW2 temporário permaneceu com apenas 197.632 bytes e não recebeu uma instalação.

O construtor agora pode copiar o cache de pacotes presente numa ISO Brasa anterior usando `--package-cache-iso`. O script live detecta esse cache, evita reinstalar `pkg` quando ele já existe e atualiza o catálogo antes de instalar os arquivos locais. O primeiro teste apontou catálogos antigos; com `pkg update -f`, a instalação local prosseguiu, baixando apenas 3 MB de pacotes adicionais e extraindo os 191 componentes gráficos. A variante atual `.build/Brasa-live-cached-boot.iso` tem 1.305.520.128 bytes (SHA-256 `E3D62F62C94498C2B54EF41EFF1B32573DB7C9C6FBCA8ABC3C9008F348D2B306`).

Em QEMU com 6 GB de RAM, 128 MB de vídeo e TCG, o assistente chegou aos campos de conta e à lista de discos. A lista mostrou apenas o disco virtual `vtbd0` de 40 GB. A VM está deixada nessa tela para inspeção; não avançamos à confirmação destrutiva, não particionamos o disco e o QCOW2 continua com 197.632 bytes. Escolhi 6 GB para o teste porque a execução anterior com 8 GB deixou apenas 0,3 GB de memória livre no Windows; com 6 GB restaram aproximadamente 1,8 GB. A instalação do FreeBSD no disco, o login, o KDE e o áudio ainda não foram validados.

Para reconstruir a variante com cache, use `py scripts/build-brasa-live-prototype.py .build/Brasa-live-cached-boot.iso --package-cache-iso .build/Brasa-live-experimental.iso`. A ISO compacta continua disponível como `.build/Brasa-live-fastboot-fixed.iso` e depende da rede para carregar os componentes gráficos.

### Experimento de repetição do instalador (27/10/2026)

O assistente agora oferece **Tentar novamente** ou **Sair para o instalador FreeBSD** depois de mostrar os detalhes de uma falha. Isso evita encerrar o fluxo sem uma escolha clara e permite repetir sem reiniciar a mídia. O construtor também aceita um caminho de saída para produzir uma ISO de teste separada, sem sobrescrever a imagem usada pela VM.

Validação feita: a ISO de teste foi construída e sua estrutura/payload foram conferidos; o texto das duas opções foi localizado no pacote da ISO e `git diff --check` passou. A ISO ainda não foi validada em QEMU. Uma tentativa anterior em QEMU com a imagem antiga retornou ao instalador de texto depois que processos do sistema live foram encerrados por falta de memória com 4 GB. Com 6 GB o desktop live iniciou; a instalação sob TCG está muito lenta. No último acompanhamento, o processo QEMU ainda respondia e o disco descartável recebia gravações periódicas, então não foi classificado como travado nem removido.

A ISO intermediária `.build/Brasa-live-retry-test.iso` (SHA-256 `9D46B916826248CE1F1CD045D2ACDEC12E00C13915041F034FE22E94870D0464`) continha apenas o ajuste de repetição e ainda não validava a instalação completa, o primeiro login, a instalação do KDE ou o áudio USB.

### Progresso visível do instalador (27/10/2026)

A janela de instalação deixou de usar a animação indeterminada. Ela agora exibe uma linha com a etapa atual e uma barra numérica: a transferência usa o tamanho informado pelo servidor e os bytes já recebidos; a extração acompanha o espaço ocupado no destino; e a instalação de pacotes usa as etapas informadas pelo `pkg`. A janela consulta o log do `bsdinstall`, para que a tela continue explicando o trabalho durante operações demoradas. Percentuais durante etapas sem contador nativo são marcos estimados, não uma previsão de tempo.

A tentativa anterior foi encerrada normalmente a pedido do usuário. O controle automático de segurança recusou a exclusão do arquivo QCOW2 descartável, que permanece em `%TEMP%`; as tentativas seguintes usam arquivos separados. A sintaxe do script passou pelo `sh -n` do Git for Windows e `git diff --check`.

### Inicialização live reduzida (27/10/2026)

A inicialização anterior incluía e extraía um cache de pacotes de 759.193.600 bytes para `/var`, além de reservar tmpfs de 5 GB para `/usr/local`. O construtor agora omite esse cache, instala somente Xorg mínimo, Openbox, Zenity e fontes pela rede, e exibe no console as linhas recentes do gerenciador de pacotes. O tmpfs de `/usr/local` aceita até 5 GB porque o conjunto de pacotes excede 2 GB depois de descompactado; esse limite é capacidade máxima, não uma reserva de RAM. `/tmp` e `/var` continuam limitados a 1 GB. Isso exige conexão à internet para abrir o ambiente gráfico.

A ISO de teste `.build/Brasa-live-fastboot-test.iso` foi construída a partir da imagem Brasa existente e caiu de 1.305.511.936 para cerca de 546 MB. Em QEMU com 8 GB de RAM, 128 MB de VGA e TCG, o boot foi visivelmente mais rápido. A primeira instalação dos pacotes falhou ao encher o tmpfs de 2 GB em `/usr/local` (`pkg: Failed to extract ... Write error`). Com o limite aumentado para 5 GB, o `pkg` passou do pacote 157, concluiu a instalação e abriu a tela gráfica de boas-vindas do Brasa. O teto de 5 GB é capacidade máxima e não reserva RAM antecipadamente. O fluxo após a tela de boas-vindas, a instalação no disco, o login e o KDE ainda não foram verificados.

O QEMU WHPX pausou com `Unexpected VP exit code 4` tanto com `-cpu max` quanto com `-cpu host`; no teste em curso, usamos TCG multi-thread, 8 GB de RAM, VGA padrão com 128 MB e OpenGL desligado. Esse modo é mais lento, mas evita o caminho gráfico que havia falhado.

A ISO `dist/Brasa-15.1-amd64.iso` é uma mídia `bootonly` FreeBSD 15.1 com os fontes e utilitários Brasa anexados. Ela não inclui desktop live, KDE, Wine, servidor de pacotes local ou instalador gráfico integrado. O instalador que inicia nesta mídia é operado por menus de texto.

`scripts/brasa-install-assistant` define etapas visuais de boas-vindas, conta, senha, seleção de disco e confirmação destrutiva. O backend em desenvolvimento revalida o disco, delega o particionamento ao `bsdinstall` e passa a configuração de conta para o script executado dentro do sistema instalado, antes de o disco ser desmontado. Ele ainda exige `/var/run/brasa-live-environment`, Zenity e o pacote Brasa em `/brasa/BRASA_PROJECT_TAR_GZ`. Esses componentes não estão integrados ao ambiente live desta ISO; o código não pode ser iniciado por um usuário desta mídia. O script de build só substitui o README e o pacote no ISO; ele não modifica o ambiente raiz embutido.

O assistente tenta obter uma conexão Ethernet via DHCP antes de particionar, porque a mídia `bootonly` baixa o sistema e os pacotes KDE pela rede. A passagem dos descritores de senha, os diálogos de terminal internos do `bsdinstall`, a proteção da mídia de boot USB, Wi-Fi, acessibilidade, recuperação após queda de energia e o ciclo até o primeiro login ainda exigem validação real. `scripts/bootstrap-freebsd.sh` configura pacotes dentro de um FreeBSD já instalado e conectado.

## Caminho de implementação

1. Construir um ambiente live FreeBSD amd64 com desktop leve, Zenity, ferramentas de disco, backend `bsdinstall`, rede e drivers de armazenamento; incorporar o assistente ao menu inicial e criar o marcador de live.
2. Criar fluxo de instalação em etapas: boas-vindas, idioma/teclado, identidade, disco com modelo e capacidade, confirmação explícita, progresso, sucesso/falha e reinicialização.
3. Enumerar os discos com identificadores estáveis e excluir a mídia live, dispositivos removíveis e discos sem capacidade de instalação do alvo padrão. Mostrar exatamente o disco e o que será apagado na tela de confirmação.
4. Usar mecanismos suportados do sistema para GPT/EFI e ZFS ou UFS, instalação da base, conta e bootloader. Manter o segredo apenas em memória ou em arquivo temporário com permissões restritas durante o processo; removê-lo ao terminar ou falhar.
5. Instalar desktop, login gráfico, suporte de áudio e utilitários. Oferecer Wine como componente opcional e deixar claro que compatibilidade varia por aplicativo.
6. Testar o ciclo completo em QEMU/VirtualBox com disco descartável e UEFI/BIOS, cancelamento antes da gravação, falhas de rede e primeiro login. Depois validar interfaces de áudio em hardware real.
7. Construir a ISO live final a partir da árvore fonte configurada e verificar boot BIOS/UEFI, integridade, tamanho, checksums e inventário de pacotes.

## Segurança e experiência

- Nunca começar a gravar ou apagar um disco antes de confirmação visível do alvo.
- Cancelar ou fechar o instalador antes da confirmação deve deixar discos intactos.
- Não usar senha padrão, nem assumir que dois campos foram preenchidos apenas porque o usuário local os preencheu.
- Exibir progresso e uma instrução recuperável se rede ou instalação falhar.
- A ISO de desenvolvimento atual não atende a esses requisitos; não a instalar em hardware com dados importantes.

### ISO com correção da seleção de disco (27/10/2026)

A lista anterior não fornecia ao Zenity os dados no formato de uma tabela com uma coluna de seleção; por isso, a confirmação não retornava um dispositivo ao assistente. O código agora prepara a coluna de rádio seguida pelo nome do disco, modelo, capacidade, identificador e bytes, deixa pré-selecionado o primeiro disco elegível e lê a segunda coluna para obter o dispositivo selecionado. O acompanhamento dos processos também trata estados de processo encerrado/zumbi como finalizados, evitando manter o progresso preso após a conclusão.

Foi construída `.build/Brasa-live-disk-picker.iso` (1.305.522.176 bytes, SHA-256 `74AB22BF646DA22D1FDCA272D1F73BBF09EC224402B79ECA53D6A7FE84F97E8A`) usando o cache de pacotes de `.build/Brasa-live-cached-boot.iso`. O catálogo El Torito e o payload foram verificados. Esta nova ISO ainda não foi iniciada em QEMU; a alteração da lista não tem confirmação em execução. A ISO anterior `.build/Brasa-live-progress-fix.iso` parou na lista antes de iniciar qualquer gravação e o disco virtual de teste permaneceu com 197.632 bytes. A VM foi desligada ao detectar que a execução TCG de 8 GB deixava cerca de 1 GB livre no Windows.

O inventário de tags, hashes, estado, links e assets publicados está em `docs/RELEASES.md`. As seis ISOs produzidas neste ciclo têm releases experimentais próprias, inclusive as imagens com defeitos observados durante os testes.


### Retorno do Zenity e terceira ISO experimental (27/10/2026)

O boot em QEMU da ISO `Brasa-live-disk-picker.iso` funcionou com 6 GB de RAM e 128 MB de vídeo, mas, ao avançar da lista que mostrava o disco virtual `vtbd0`, o instalador rejeitou a seleção. Nenhuma gravação começou. A VM foi encerrada e o QCOW2 temporário de 197.632 bytes foi removido. O defeito estava na interpretação do valor impresso pelo Zenity: a seleção de coluna única não localizava corretamente o dispositivo na saída da lista.

O código foi alterado para pedir todas as colunas da linha selecionada e localizar nelas o nome exato de um dispositivo elegível; se não encontrar, mostra um erro seguro sem tocar no disco. A terceira imagem `.build/Brasa-live-picker-output-fix.iso` foi construída com o cache da mídia Brasa, preservando as imagens anteriores. Tamanho: 1.305.524.224 bytes; SHA-256: `5728AF6539F5FA2E2E5AA84934BA2635033945F5C409149DCC78E5680369B025`. A estrutura El Torito e o payload foram conferidos. O boot e a nova leitura da seleção ainda precisam ser testados antes de qualquer instalação.


### Entrada da lista Zenity em colunas (27/10/2026)

O segundo boot da ISO `Brasa-live-picker-output-fix.iso` confirmou que a interface inicia, mas o botão de avanço apresentou “A seleção do disco não foi reconhecida”. O QCOW2 de 40 GB continuou sem instalação. A lógica de correspondência foi simulada isoladamente e retornou `vtbd0`; o valor impresso pelo Zenity na execução real ainda não foi decodificado como esperado. Para evitar a ambiguidade do formato de múltiplas colunas pela entrada padrão, a quarta variante constrói os argumentos Zenity coluna por coluna e deixa apenas o primeiro disco elegível inicialmente marcado. Nenhuma alteração ao disco ocorre até à confirmação explícita.


### Seleção confirmada e travamento durante instalação (27/10/2026)

A quarta variante `Brasa-live-zenity-argv-fix.iso` foi inicializada em QEMU com 6 GB de RAM, 128 MB de VGA, TCG e disco QCOW2 de 40 GB. O assistente mostrou `vtbd0` como primeira opção selecionada; após Tab/Tab/Enter, a confirmação final exibiu o disco correto. Isso confirma o fluxo gráfico de seleção e a passagem do nome do disco ao assistente.

Após a confirmação, o instalador baixou e verificou os arquivos e começou a extração da base. A janela então ficou preta. O QMP mostrou QEMU ainda em execução, mas as estatísticas de escrita do dispositivo ficaram em 782.883.840 bytes sem alteração em dois intervalos de 30 segundos, e a CPU quase não avançou; o Windows tinha aproximadamente 1,2 GB livres. A VM foi encerrada e o QCOW2 descartável foi removido. Portanto, o particionamento/instalação completa, o boot instalado, a conta, o KDE e o áudio continuam sem validação. Investigar o desaparecimento da janela e a memória durante a extração é o próximo passo.


### Redução das dependências do ambiente gráfico (27/10/2026)

Openbox puxava dependências pesadas para decorar a única interface do live: a instalação cacheada tinha 191 pacotes, entre eles FFmpeg, codecs e ferramentas de compilação. O construtor agora resolve o catálogo SQLite e inclui na ISO somente os arquivos de pacote da árvore usada pelo Xorg mínimo, Zenity, fontes e drivers de vídeo. O live usa TWM; os componentes que faltam no cache são obtidos pelo repositório FreeBSD. O conjunto cacheado passou de 191 para 131 dependências, e o espaço instalado calculado pela base do repositório caiu de aproximadamente 4,21 GB para 2,83 GB. O KDE continua previsto para o sistema instalado e não foi trocado.

A ISO `.build/Brasa-live-twm.iso` foi gerada a partir da mídia Brasa existente. Seu hash e os metadados de publicação ficam registrados em `docs/RELEASES.md`. Em QEMU/TCG com 4 GB de RAM, iniciou, baixou a atualização do catálogo, extraiu os 132 pacotes e executou o X. O processo chegou a aproximadamente 4,7 GB de memória residente no Windows durante a extração; após terminar, o desktop/assistente continuou preto e sem conteúdo legível. Comandos enviados exclusivamente pelo teclado não tornaram a tela utilizável. O QCOW2 descartável ficou em 197.632 bytes e foi removido após desligar a VM pelo monitor QMP. Não houve particionamento, instalação da base, login, teste de KDE, Wine ou áudio.

A imagem, inclusive com essa falha, está registrada como release experimental própria em `docs/RELEASES.md`. A próxima investigação é corrigir a renderização/gerenciamento das janelas no X antes de avançar a etapa de instalação.


### JWM e renderização do assistente (27/10/2026)

A sexta variante troca TWM por JWM no ambiente live. A alteração corrigiu a tela preta: em QEMU/TCG com 4 GB de RAM e VGA de 128 MB, o assistente abriu com texto, botões e formulários legíveis. O cache inclui 133 dependências; JWM e os pacotes não presentes no cache são baixados pelo repositório FreeBSD. A primeira tela avançou com Enter, e os formulários de nome, usuário e senha apareceram.

O teste de senha digitada via QMP terminou na mensagem de senhas diferentes e retornou ao instalador FreeBSD em texto. Como a entrada automatizada enviou caracteres um a um sob TCG, não foi possível distinguir erro de envio de um defeito no assistente. Não foi possível verificar a lista de discos nesta variante e nenhuma ação de particionamento aconteceu. O QCOW2 descartável ficou em 197.632 bytes e foi removido após encerrar QEMU. Instalação completa, KDE, Wine, áudio USB e hardware real seguem sem validação.

A imagem `.build/Brasa-live-jwm.iso` tem 1.072.138.240 bytes e SHA-256 `CB0C908BD2014336BE915EDFD90DED412D4E9A35DCAF03AFD10218CB441B593C`. Ela foi publicada em release experimental própria, registrada em `docs/RELEASES.md`.

### Teste de instalação confirmado no disco descartável (27/10/2026)

Na ISO `Brasa-live-jwm.iso` (release `brasa-jwm-live-boot-2026-10-27`), o assistente alcançou a confirmação final e iniciou a instalação em `vtbd0`, um QCOW2 descartável de 40 GB. A base FreeBSD foi baixada (cerca de 574 MB lidos do CD virtual no total), e o disco recebeu aproximadamente 568.698.368 bytes de escrita. A tela ficou preta durante a extração; em duas verificações espaçadas por 30 segundos, as escritas não avançaram e o processo consumiu apenas cerca de 2 segundos adicionais de CPU. QEMU foi encerrado pelo monitor QMP e o QCOW2 descartável foi removido. Nenhum disco físico foi conectado.

Resultado: instalação da base não concluída; nenhuma instalação inicializável foi verificada. O progresso da tela do instalador não está acompanhando ou exibindo a etapa longa de extração, e há uma pausa efetiva depois do download. A próxima investigação deve capturar a saída/log de `bsdinstall` e identificar se o extrator está bloqueado ou se o X/JWM está ocultando a tela, antes de gerar outra ISO. KDE, login instalado, Wine, áudio USB class-compliant e hardware real permanecem sem validação.

### Extração não interativa visível (27/10/2026)

A ISO `.build/Brasa-live-noninteractive-extract.iso` foi construída a partir da ISO Brasa existente com cache gráfico reduzido. O assistente agora chama `bsdinstall script` com a entrada padrão em `/dev/null`. No código do FreeBSD, isso seleciona a extração por `tar` quando não há TTY, em vez do extrator interativo de terminal; a saída do processo continua no log que alimenta o progresso gráfico.

Em QEMU 11.1/TCG com 8 GB de RAM, 2 vCPUs e VGA de 128 MB, o boot live e o assistente abriram. As credenciais de teste e a seleção de `vtbd0`/40 GB passaram; após confirmação, a janela mostrou a etapa de extração da base. O disco virtual recebeu aproximadamente 1.272.521.216 bytes; a CPU continuou avançando, mas as escritas ficaram sem mudança por vários minutos e o instalador ainda não havia começado a configuração do desktop Brasa quando o teste foi parado por lentidão. O disco QCOW2 temporário foi removido depois do encerramento do QEMU. A ISO não concluiu uma instalação inicializável.

O host Windows informou `VirtualizationFirmwareEnabled=False` para o Intel i5-12400F, então este teste executou em TCG (emulação por software). As tentativas WHPX registradas anteriormente terminaram com `WHPX: Unexpected VP exit code 4` e erros de estado xsave; repetir com aceleração exige habilitar VT-x no firmware e revalidar WHPX. KDE, Wine, áudio USB class-compliant, primeiro boot e hardware real continuam sem validação.


### ISO WHPX offline-catalog-progress (27/10/2026)

A imagem exporta o catálogo FreeBSD-ports embutido separadamente do cache dos pacotes e tenta fornecê-lo ao instalador, além de apresentar uma mensagem compreensível quando o texto interno do `bsdinstall` está vazio. Em QEMU 11.1/WHPX com 8 GB de RAM, 4 vCPUs e VirtIO GPU, o ambiente live iniciou, o cadastro e a seleção/confirmação do QCOW2 de 40 GB funcionaram e o assistente iniciou a instalação com barra de progresso. O caminho `pkg install -l` não aceitou os pacotes locais; o script atualizou o catálogo online, extraiu os 133 componentes gráficos e abriu o instalador. A base `base.txz` começou a ser baixada. Encerramos QEMU antes de concluir para liberar memória do Windows (uso do processo aproximou-se de 6 GB). A instalação final e o primeiro boot não foram validados.

O QCOW2 `Brasa-offline-catalog-3b07855cda984206be73ff68da3a5cd7.qcow2` foi removido após releases posteriores. A ISO base `dist/Brasa-15.1-amd64.iso` e `.build/freebsd-bootonly.iso` permanecem preservadas.


### ISO WHPX pkgbase para medir a instalação base (27/10/2026)

Para evitar a extração monolítica de `base.txz` e `kernel.txz`, esta variante deixa `DISTRIBUTIONS` vazio e pede `COMPONENTS=base` ao `bsdinstall script` do FreeBSD 15.1. O código upstream encaminha essa configuração ao fluxo de instalação FreeBSD-base por pacotes. O construtor também passou a recuperar o catálogo de pacotes de uma ISO que já o exporta separadamente, para que novas imagens continuem reproduzíveis.

QEMU 11.1/WHPX, 8 GB RAM, 4 vCPUs, VirtIO GPU: o boot live, o assistente, a conta e a confirmação de `vtbd0` funcionaram. A correção experimental copia `/etc/resolv.conf` para o destino antes de chamar pkgbase. O QCOW de 40 GB foi particionado, mas a tela ficou em `FreeBSD Installer`, em 94%, por mais de dois minutos sem crescimento adicional do disco nem erro visível. A instalação base não concluiu; o ajuste DNS e a velocidade não foram confirmados. QEMU foi encerrado via QMP. A ISO de correção foi publicada na release `brasa-whpx-pkgbase-resolver-fix-2026-10-27`.

### ISO WHPX pkgbase no-hidden-retry (27/10/2026)

A mídia evita perguntas de repetição ocultas caso `pkg update` ou `pkg install` falhe dentro do `bsdinstall pkgbase --non-interactive`, para que o assistente possa mostrar o erro. O teste QEMU 11.1/WHPX com 8 GB chegou à etapa da base, mas o QCOW permaneceu em 334.036.992 bytes por mais de dois minutos depois do particionamento; não houve mensagem de erro antes de encerrar. A correção de repetição ainda não foi exercitada e a instalação continua sem velocidade medida ou primeiro boot validado. Ver release `brasa-whpx-pkgbase-no-hidden-retry-2026-10-27`.


### Redução do conjunto pkgbase e diagnóstico por fase (27/10/2026)

A última instalação que chegou ao `pkgbase` ficou por cerca de 24 minutos em “Configurando o sistema instalado...” sem gravações novas no QCOW; a CPU continuou ocupada. O assistente passava `COMPONENTS=base`. A descrição do FreeBSD para `base` inclui os componentes `devel` e `optional`, além do necessário para inicializar. A alteração passa a selecionar `COMPONENTS=minimal`; o script do FreeBSD continua incluindo `minimal`, `pkg` e o kernel, e o bootstrap Brasa instala o desktop e os aplicativos em etapa separada. Foram acrescentadas mensagens para quatro fases do pkgbase: consulta de componentes, atualização do catálogo, download e instalação. Os downloads também mantêm o limite `FETCH_TIMEOUT=30` e uma repetição.

A ISO `.build/Brasa-live-whpx-pkgbase-minimal-phases.iso` foi construída a partir da mídia Brasa existente e verificada: contém `COMPONENTS="minimal"`, os quatro marcadores de fase e o limite de download. Em QEMU/WHPX, 8 GiB, quatro vCPUs, VirtIO GPU de 128 MiB, a execução com `qemu64,-svm` e a comparação com `core2duo` pararam no mesmo último texto do kernel (`random: unblocking device.`). Em ambas, o QCOW não recebeu gravações e o instalador não chegou a iniciar. Portanto a redução do conjunto é uma otimização plausível, mas ainda não há medição de instalação nem confirmação de boot completo. Os QCOWs descartáveis foram removidos após encerrar cada VM. A ISO base `dist/Brasa-15.1-amd64.iso` e a imagem de referência `.build/freebsd-bootonly.iso` permanecem preservadas.

A variante anterior `.build/Brasa-live-whpx-pkgbase-bounded-fetch-diagnostic.iso` preserva os tempos-limite de download e a tentativa única, mas ainda seleciona o conjunto `base`. Em QEMU/WHPX, 8 GiB e quatro vCPUs, ela passou pelo live e pelo particionamento; ficou mais de 24 minutos na fase de instalação da base, com zero gravações novas no QCOW após o particionamento. A VM foi encerrada antes de concluir.

### Instalador gráfico automático no primeiro boot (27/10/2026)

A ISO `.build/Brasa-live-graphical-firstboot-audio-r5-2026-10-27.iso` agora chega automaticamente ao assistente Zenity Brasa; o menu textual FreeBSD só aparece se houver falha no live. O teste chegou à janela “Instalar Brasa” sem escolher “Live System”. A origem do erro `set: Illegal option --` era o arquivo `brasa-install-assistant` empacotado com finais CRLF; o construtor passa a normalizar os arquivos de projeto para LF. A chamada de `xinit` também usa o servidor X padrão, e o assistente localiza as raízes dos pacotes em uma lista LF separada.

A ISO mantém os conjuntos oficiais locais `base.txz` e `kernel.txz`; o kernel inclui `snd_uaudio.ko` para USB Audio Class. O catálogo/cache gráfico original estava sem cinco arquivos e a construção agora os baixa do repositório FreeBSD. No teste, a instalação de pacotes locais ainda recorreu à atualização online do catálogo e baixou 11 componentes restantes; essa espera ainda precisa ser reduzida. Em QEMU/TCG com 8 GiB, quatro vCPUs, VGA de 128 MiB e QCOW2 SATA descartável de 40 GiB, a janela de boas-vindas abriu em cerca de sete minutos. O disco não foi particionado nem alterado. A sessão QEMU foi deixada aberta na primeira tela segura para teste manual.

WHPX ficou parado após `random: unblocking device.` com VGA padrão e VirtIO; este teste foi feito em TCG. A instalação no disco, primeiro boot, KDE instalado, Wine/Proton e interfaces USB reais não foram testados. O suporte USB Audio está presente no kernel da mídia, mas ainda não foi verificado num dispositivo físico.

### Cache local reduzido: variante r6 rejeitada (27/10/2026)

Para evitar o fallback de rede na r5, a r6 renomeou os arquivos do cache local para o formato nome-versão e reduziu a ISO de 1.285.003.264 para 837.859.328 bytes. No boot com TCG, 8 GiB e VGA de 128 MiB, o `pkg` foi preparado e o catálogo embarcado foi encontrado, mas a inicialização gráfica falhou antes de abrir o Zenity; a VM voltou ao menu textual FreeBSD. O QCOW2 novo continuou com 197.632 bytes. Como o resultado regrediu em relação à r5, o código foi restaurado ao caminho de fallback pela internet, e a r6 foi preservada como artefato experimental com a falha documentada.

O código de construção voltou ao comportamento de fallback pela internet. Na repetição da r5, a interface gráfica abriu e o fluxo chegou à confirmação de `ada0`, mas a chamada do helper `bsdinstall` falhou antes de escrever no QCOW2. A seção seguinte registra a causa e o teste da correção.

### Correção do helper bsdinstall e extração local (27/10/2026)

A r5 havia chegado à confirmação do disco, mas o `bsdinstall` devolveu `Permission denied` ao executar `/usr/libexec/bsdinstall/script`. A causa foi confirmada nos registros Rock Ridge: o modo gravado era `0555`, sem o tipo de arquivo regular `0100000`. O construtor agora escreve `0100555` para `script` e `pkgbase`. Também se passou `pkg install -U` após `pkg update -f`, para evitar uma segunda atualização automática do catálogo.

Na r7, QEMU/TCG com 8 GiB e 4 vCPUs avançou pelo particionamento, verificação e extração local da base e kernel. O disco virtual recebeu 1.259.339.776 bytes e a etapa mudou para “Configurando KDE, áudio USB e suporte do computador”. A gravação do QCOW não avançou por mais de cinco minutos nessa etapa; o QEMU permaneceu ativo, consumiu cerca de 6,7 GiB de memória e foi fechado a pedido do usuário. O disco ficou em `%TEMP%` como QCOW2 parcial. A falha de permissão foi removida, mas ainda não há confirmação de que KDE, Wine ou PipeWire terminem a instalação nem que o primeiro boot funcione. A ausência de gravações nessa etapa sugere investigar o acesso DNS/rede do sistema-alvo, que executa `pkg` no chroot.

### Correção da primeira sessão KDE (28/10/2026)

O teste de r36 mostrou que o login SDDM funcionava, mas o desktop carregava sem painel. No QCOW foram instalados o conjunto `plasma6-plasma` recomendado pelo FreeBSD Handbook, o gerenciador de atividades e o widget de áudio; também se corrigiu a propriedade de `/home/brasa/.config`, que havia sido criada como root. Com isso, o painel e o Konsole apareceram. O bootstrap passa a instalar esse conjunto de sessão e a garantir que `.config` pertence ao usuário antes de criar os arquivos de inicialização automática. A próxima ISO precisa ser testada por instalação limpa antes de considerar o fluxo reproduzível.

No catálogo trimestral incluído na ISO de referência r6, a dependência transitiva estimada passa de 960 pacotes/2.358,5 MiB para 683 pacotes/1.378,3 MiB. Esse número descreve o catálogo consultado, não uma medição de tempo ou bytes efetivamente baixados durante a instalação.

A ISO r8 `.build/Brasa-live-graphical-firstboot-audio-r8-minimal-kde-2026-10-27.iso` (756.109.312 bytes; SHA-256 `dbddae317ec8345e997dd9b89bf5da3804ff7a66df86b8e46bed206f31bb2a8f`) foi criada sem o cache de pacotes gráficos live. Em QEMU/TCG com 8 GiB, 8 vCPUs, VGA de 128 MiB e QCOW2 descartável de 40 GiB, falhou antes de abrir o assistente. O log mostra `cp: /usr/local/. and /usr/local/. are identical (not copied)`: o caminho sem cache tentava copiar o diretório sobre ele próprio. O QCOW2 permaneceu em 197.632 bytes e nenhum disco foi particionado ou alterado. O kernel inclui `snd_uaudio.ko` e a mídia contém os conjuntos FreeBSD locais. A release `brasa-r8-minimal-kde-no-cache-boot-failed-2026-10-27` preserva esse artefato defeituoso.

### ISO r9: cache live r7 com fallback de rede e KDE reduzido (27/10/2026)

A r9 foi construída usando a r7 como referência para o cache live; manteve o fallback pela internet. O início do live usou os 133 pacotes locais e baixou os 11 componentes que faltavam. O assistente abriu e foi controlado somente pelo teclado. A lista identificou apenas o disco virtual `ada0`, QEMU HARDDISK, 40 GB, identificador `QM00001`. Após a confirmação explícita desse QCOW descartável, o instalador particionou o disco e extraiu base/kernel locais.

O teste QEMU 11.1/TCG usou 8 GiB de RAM, 8 vCPUs, VGA de 128 MiB e disco QCOW2 de 40 GiB. Com 10 minutos, o QCOW chegou a 1.259.208.704 bytes e a interface mostrava “Configurando KDE, áudio USB e suporte do computador”. O contador dessa etapa chegou a cerca de dois minutos; o QCOW não mudou por pelo menos 55 segundos. A VM foi encerrada pelo limite de teste via QMP e o QCOW parcial em `%TEMP%` foi preservado. Não foi confirmado se o `pkg` ainda resolvia dependências ou se havia iniciado o download/extração do desktop.

A ISO mede 1.284.970.496 bytes (SHA-256 `f80389c31c65b4f3db4679970733a79c0555e6d9ded1e2cfcc8743a4f1989f57`) e inclui `snd_uaudio.ko`, base/kernel FreeBSD e cache live. A release é `brasa-r9-kde-reduced-cache-fallback-2026-10-27`. O fluxo completo, o KDE instalado, primeiro boot, Wine e áudio USB em hardware físico continuam sem validação. A estimativa de dependências do conjunto KDE menor veio do catálogo trimestral da r6, não desse teste de 10 minutos.


### r13: uma passagem de cache e diagnóstico da configuração (27/10/2026)

O r13 evita desempacotar o TAR de cache numa árvore temporária que não contém arquivos instalados; os arquivos do cache são extraídos uma única vez para `/var`, e `pkg add` instala os pacotes a partir dali. O construtor confere a saída do `rc.local` para que uma saída normal do assistente gráfico não caia no instalador de texto.

O teste foi controlado somente pelo teclado. O boot gráfico, o formulário, a confirmação do único QCOW2 descartável `vtbd0`/40 GiB, o particionamento e a instalação local de base/kernel avançaram. O marcador “Configurando KDE, áudio USB e suporte do computador” é escrito pelo `bsdinstall` imediatamente antes de chamar o script pós-instalação; ele não prova que KDE, áudio ou suporte específico já tenham iniciado. A barra ficou em 92% por cerca de dez minutos, sem novas gravações no QCOW, embora a CPU de QEMU permanecesse ocupada. O arquivo do projeto descompactado no destino tem apenas 33.544 bytes; depois disso o script prepara as contas, configura a rede e entra no bootstrap. O QMP registrou 1.266.393.088 bytes escritos acumulados antes da parada; esse contador não mudou durante a fase. Em seis amostras de rede, QEMU não tinha conexões TCP externas. `pkg.freebsd.org` resolvia no host Windows. Não foi possível localizar o comando parado nem confirmar download, resolução de dependências KDE ou configuração de hardware.

A ordem no bootstrap é KDE/Xorg (incluindo o pacote `drm-kmod`), áudio PipeWire opcional, Wine e ajustes finais da máquina. Áudio USB não explica o marcador amplo, pois seu grupo vem depois do KDE. A próxima imagem preserva a saída real no diálogo e inclui marcadores entre extração do projeto, criação das contas, preparação do `pkg`, consultas de disponibilidade e cada grupo de pacotes, para identificar onde para.

QEMU foi encerrado e o QCOW2 temporário removido; a ISO experimental foi preservada para release. Instalação completa, KDE final, primeiro boot, Wine, áudio class-compliant físico e drivers num PC real ainda não foram validados. A ISO base permanece intacta.


### Pesquisa e instrumentação de `bsdconfig` (28/10/2026)

Não encontrei relatos que indiquem que `bsdconfig` normalmente leve muitos minutos. O Handbook oficial mostra a etapa de busca por arquivos de mapa de teclado, mas não recomenda uma espera longa. A FreeBSD Foundation descreve `bsdconfig` como rotinas de shell usadas por `bsdinstall`; isso não caracteriza uma etapa pesada por si só. Encontrei um relato comunitário de `pkg` levando 4–6 minutos ao atualizar o catálogo, mas é uma operação diferente e não explica esta tela. Fontes: [FreeBSD Handbook](https://docs.freebsd.org/en/books/handbook/book/), [FreeBSD Foundation — Installer Usability](https://freebsdfoundation.org/our-work/journal/browser-based-edition/networking-3/installer-usability/) e [FreeBSD Forums — pkg takes too long to start](https://forums.freebsd.org/threads/pkg-takes-too-long-time-to-start.103903/).

Na r14, a etapa mostrava `bsdconfig` por cerca de dez minutos; o QCOW não recebia gravações desde 23:46 e não havia novas linhas no log serial depois do marcador. A r15 reproduziu a parada: QEMU confirmou apenas `vtbd0`, QCOW2 descartável de 40 GiB, extraiu a base/kernel e parou em `bsdconfig`. Não houve gravação no QCOW desde 00:09:10 até o encerramento às 00:17; a CPU continuou ocupada e o processo chegou a cerca de 6,3 GiB de RAM. Os marcadores impressos no `/usr/libexec/bsdinstall/config` não apareceram no log; portanto o subcomando exato continua indeterminado e a mensagem na tela, isoladamente, não prova que o código interno de `bsdconfig` seja o responsável.

A r15 `.build/Brasa-live-r15-bsdconfig-trace-2026-10-27.iso` foi compilada (1.285.009.408 bytes; SHA-256 `30C09815403F60DAA9602C3BD33E5F80D9D89D8A529FCC60103A48A028CB8C87`). O QCOW foi encerrado via QMP e removido; a r14 antiga também foi removida, mantendo localmente só a r15 e as duas imagens-base. A instalação e o primeiro boot do disco não passaram. Próximo passo: gravar subfases de `bsdinstall config` num arquivo de estado lido pelo progresso gráfico, antes de fazer outra instalação longa.

A r16 implementou esse arquivo de estado e mensagens traduzidas para início/fim de `bsdinstall config`, cópia de configuração/boot e `newaliases`. No teste QEMU, a tela continuou exibindo apenas `bsdconfig` por dez minutos; nenhum desses marcadores ficou visível. O QCOW não teve gravações depois de 00:28:03, enquanto a CPU continuou ocupada. O teste terminou sem concluir a instalação. Isso deixa duas hipóteses em aberto: o script instrumentado não foi alcançado, ou o estado compartilhado não está sendo lido/mostrado pelo assistente. A próxima investigação precisa consultar o estado/processos dentro do live enquanto a etapa está parada, em vez de aumentar o tempo de espera.
