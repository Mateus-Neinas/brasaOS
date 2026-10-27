# Releases das ISOs

Toda imagem ISO criada deve receber uma release própria no GitHub, inclusive quando for experimental, incompleta ou sabidamente defeituosa. Não reutilize tags: use uma tag por artefato, anexe a ISO exata e registre data, hash SHA-256, estado conhecido, limitações e se passou por boot e teste de instalação.

Para publicar manualmente pelo GitHub, crie uma release em `https://github.com/Mateus-Neinas/brasaOS/releases/new`, informe a tag correspondente, copie as notas documentadas e anexe a ISO. A release não substitui o histórico de código: faça commits e push dos fontes e documentação separadamente.

## ISO progress-fix (27/10/2026)

- Tag publicada: [`brasa-progress-fix-2026-10-27`](https://github.com/Mateus-Neinas/brasaOS/releases/tag/brasa-progress-fix-2026-10-27)
- Arquivo: `Brasa-live-progress-fix.iso`
- Tamanho: 1.305.520.128 bytes
- SHA-256: `D4AF49B2D8B18F60DAD6204D4FE201FDBC84F438B61312179A0CA6D442313299`
- Estado: experimental. Abriu o ambiente gráfico e o assistente até a lista de discos; a seleção não avançou. O disco virtual permaneceu sem instalação. Contém a correção do monitor de processos do instalador.
- Não validado: instalação completa, login, KDE, áudio USB, Wine e hardware real.

## ISO disk-picker (27/10/2026)

- Tag publicada: [`brasa-disk-picker-2026-10-27`](https://github.com/Mateus-Neinas/brasaOS/releases/tag/brasa-disk-picker-2026-10-27)
- Arquivo: `Brasa-live-disk-picker.iso`
- Tamanho: 1.305.522.176 bytes
- SHA-256: `74AB22BF646DA22D1FDCA272D1F73BBF09EC224402B79ECA53D6A7FE84F97E8A`
- Estado: experimental, construída a partir da mídia Brasa existente com cache de pacotes e correção da estrutura de colunas Zenity para lista de discos com seleção por rádio, inicialmente marcando o primeiro disco elegível. Verificação estrutural confirmou catálogo El Torito e payload Brasa presente.
- Validada em boot no QEMU (6 GB de RAM, 128 MB de vídeo, TCG): abriu o ambiente live e a lista exibiu `vtbd0`, mas o assistente rejeitou o valor retornado, antes de qualquer gravação. A VM foi fechada e o QCOW2 descartável de 197.632 bytes foi removido. Não validado: instalação completa, primeiro login, KDE, áudio USB, Wine e hardware real.


## ISO picker-output-fix (27/10/2026)

- Tag publicada: [`brasa-picker-output-fix-2026-10-27`](https://github.com/Mateus-Neinas/brasaOS/releases/tag/brasa-picker-output-fix-2026-10-27)
- Arquivo: `Brasa-live-picker-output-fix.iso`
- Tamanho: 1.305.524.224 bytes
- SHA-256: `5728AF6539F5FA2E2E5AA84934BA2635033945F5C409149DCC78E5680369B025`
- Estado: experimental. O assistente agora lê todas as colunas devolvidas pelo Zenity e encontra nelas o nome exato do disco elegível, em vez de depender da posição da coluna impressa.
- Validada em QEMU: o live iniciou, mas o Zenity ainda não devolveu o dispositivo ao assistente; a caixa informou que não reconheceu a seleção. Nenhuma gravação ocorreu. A causa provável é a forma de alimentar linhas de múltiplas colunas por entrada padrão; a próxima variante passa as células como argumentos separados. Não validado: instalação completa, primeiro login, KDE, áudio USB, Wine e hardware real.


## ISO zenity-argv-fix (27/10/2026)

- Tag publicada: [`brasa-zenity-argv-fix-2026-10-27`](https://github.com/Mateus-Neinas/brasaOS/releases/tag/brasa-zenity-argv-fix-2026-10-27)
- Arquivo: `Brasa-live-zenity-argv-fix.iso`
- Tamanho: 1.305.524.224 bytes
- SHA-256: `560B3AE1E5BDEFCA26CAC390A30725CE4F1341E90E850B0A734474BFE2DCBC0C`
- Estado: experimental. A lista de discos passa as linhas como argumentos individuais do Zenity e marca somente o primeiro disco elegível. A seleção resultante continua sendo comparada com os nomes de disco obtidos pelo sistema antes de qualquer operação destrutiva.
- Validada em QEMU: inicialização live, seleção pré-marcada de `vtbd0` e abertura da confirmação final com o disco e a capacidade visíveis. A instalação começou após a confirmação. A tela ficou preta durante a extração da base, sem progresso de escrita por dois intervalos de 30 s; o QCOW2 registrava 782.883.840 bytes gravados e a memória livre do Windows caiu para cerca de 1,2 GB. A VM foi encerrada e o disco temporário removido. A instalação não terminou; primeiro login, KDE, áudio USB, Wine e hardware real não foram testados.


## ISO twm-live-reduction (27/10/2026)

- Tag publicada: [`brasa-twm-live-reduction-2026-10-27`](https://github.com/Mateus-Neinas/brasaOS/releases/tag/brasa-twm-live-reduction-2026-10-27)
- Arquivo: `Brasa-live-twm.iso`
- Tamanho: 1.072.136.192 bytes
- SHA-256: `D24CD799B92D842C08CF4B1D4005533CC2CFA988AE5E839B204DF8BC7597A2E0`
- Mudança: substitui Openbox por TWM no ambiente temporário do instalador e mantém KDE como desktop pretendido no sistema instalado. O construtor reduz o cache para as dependências gráficas do live: 131 pacotes cacheados, em vez dos 191 instalados na variante anterior. A imagem caiu de cerca de 1,31 GB para 1,07 GB.
- Validada em QEMU/TCG com 4 GB de RAM e VGA de 128 MB: o boot aconteceu, o catálogo de pacotes foi atualizado, os 132 componentes (131 dependências cacheadas e TWM baixado) foram extraídos e o X tentou abrir o assistente. A tela gráfica ficou preta/ilegível e não foi possível validar a navegação do assistente. O disco QCOW2 ficou em 197.632 bytes; nenhuma etapa de particionamento ou instalação da base aconteceu. A VM foi encerrada e o disco descartável removido.
- Continua sem validação: instalação completa, boot do sistema instalado, login, KDE, áudio USB class-compliant, Wine e hardware real.


## ISO jwm-live-boot (27/10/2026)

- Tag publicada: [`brasa-jwm-live-boot-2026-10-27`](https://github.com/Mateus-Neinas/brasaOS/releases/tag/brasa-jwm-live-boot-2026-10-27)
- Arquivo: `Brasa-live-jwm.iso`
- Tamanho: 1.072.138.240 bytes
- SHA-256: `CB0C908BD2014336BE915EDFD90DED412D4E9A35DCAF03AFD10218CB441B593C`
- Mudança: substitui TWM por JWM, mantendo a cache gráfica reduzida e o KDE como desktop planejado do sistema instalado.
- Validada em QEMU/TCG com 4 GB de RAM e VGA de 128 MB: boot, atualização do catálogo e instalação do conjunto gráfico com 133 dependências. A janela do assistente ficou legível. O teste avançou pelo teclado até os campos de conta e a confirmação de senha; a verificação acusou senhas diferentes e voltou ao instalador FreeBSD em texto. Como os caracteres foram enviados por QMP sob TCG, não está determinado se a diferença veio da entrada automatizada ou do assistente. A lista de discos não foi alcançada nesta variante.
- O QCOW2 descartável ficou em 197.632 bytes; nenhuma operação de disco ocorreu. QEMU foi encerrado e o disco temporário removido.
- Continua sem validação: seleção de disco nesta variante, instalação completa, boot do sistema instalado, login, KDE, áudio USB class-compliant, Wine e hardware real.

## Reteste de instalação na release JWM (27/10/2026)

O teste com a ISO publicada chegou à confirmação explícita e iniciou no disco QCOW2 descartável `vtbd0` de 40 GB. Após baixar a base, o instalador deixou a tela preta durante a extração. O disco acumulou ~568,7 MB de gravações, mas ficou sem novas gravações por pelo menos 30 segundos; a CPU também quase não avançou. QEMU foi encerrado com segurança e o QCOW2 temporário foi removido; nenhum disco do Windows foi conectado. A falha foi documentada em `docs/PROTOTYPE.md`.


## ISO noninteractive-extract (27/10/2026)

- Tag da release: [`brasa-noninteractive-extract-2026-10-27`](https://github.com/Mateus-Neinas/brasaOS/releases/tag/brasa-noninteractive-extract-2026-10-27)
- Arquivo: `Brasa-live-noninteractive-extract.iso`
- Tamanho: 1.072.138.240 bytes
- SHA-256: `D58BA3B63A75302AFCEAB78713FE5E70771BBD022844CA00D09F45E7C5FD05B8`
- Mudança: força a entrada padrão não interativa para `bsdinstall script`, mantendo a extração e a saída em log sob a janela gráfica de progresso.
- Validada em QEMU/TCG com 8 GB de RAM, 2 vCPUs e VGA de 128 MB: boot live, campos de conta, lista/seleção de `vtbd0` de 40 GB e confirmação destrutiva. A etapa “Extracting distributions” apareceu. O teste foi encerrado por lentidão após ~1,27 GB de gravações, antes de começar a configuração do Brasa. O Windows reportou VT-x desativado; WHPX não foi utilizável neste host. O QCOW2 descartável foi removido ao fechar QEMU.
- Continua sem validação: instalação completa, boot do sistema instalado, KDE, primeiro login, Wine, áudio USB class-compliant e hardware real. A ISO é experimental e não deve ser usada em um disco com dados importantes.

## ISO WHPX VirtIO com progresso legível (27/10/2026)

- Tag da release: [`brasa-whpx-virtio-progress-2026-10-27`](https://github.com/Mateus-Neinas/brasaOS/releases/tag/brasa-whpx-virtio-progress-2026-10-27)
- Arquivo: `Brasa-live-whpx-virtio-progress.iso`
- Tamanho: 1.072.173.056 bytes
- SHA-256: `22EE9AEBA637385982D8427A3F4C21969B0765782833CBAA3DE00B04F8C20C20`
- Mudança: inclui o módulo oficial FreeBSD 15.1 `virtio-gpu-qemu-kmod`, configura o framebuffer para Xorg e mantém JWM apenas no ambiente temporário do instalador. A correção do progresso oculta linhas internas `DEBUG:` do `bsdinstall`, mostra a saída corrente do instalador e reinicia o contador de tempo quando a mensagem muda. KDE permanece o desktop pretendido do sistema instalado.
- Testada em QEMU 11.1/WHPX com 6 GB de RAM, 4 vCPUs, VGA VirtIO e QCOW2 descartável de 40 GB: live gráfico, cadastro de usuário, seleção de `vtbd0` e confirmação do disco funcionaram. A instalação chegou a 97%, mas a tela permaneceu nessa etapa por quase sete minutos e o QCOW2 não teve novas gravações por mais de quatro minutos. O teste foi encerrado por QMP. O sistema instalado não foi validado; o novo texto de progresso desta compilação foi verificado estruturalmente na ISO, mas ainda precisa de reteste em QEMU.
- O QCOW2 descartável foi removido depois de releases posteriores. A imagem base `dist/Brasa-15.1-amd64.iso` não foi alterada.
- Continua sem validação: instalação completa e inicializável, login, KDE, Wine, áudio USB class-compliant e hardware real. Não use num disco com dados importantes.

## ISO WHPX VirtIO package-progress (27/10/2026)

- Tag publicada: [`brasa-whpx-virtio-package-progress-2026-10-27`](https://github.com/Mateus-Neinas/brasaOS/releases/tag/brasa-whpx-virtio-package-progress-2026-10-27)
- Arquivo: `Brasa-live-whpx-virtio-package-progress.iso`
- Tamanho: 1.072.175.104 bytes
- SHA-256: `65A3658D6F91FC560ADF59BD79AA8A78E844D2F8DC282DAD26FEFCDE09671229`
- Mudanças: o progresso interpreta os contadores `[atual/total]` das linhas de instalação e extração do `pkg`; o bootstrap usa Plasma KDE com Konsole, Dolphin e Ark em vez do metapacote completo `kde`. KDE permanece o desktop instalado pretendido.
- Testada em QEMU 11.1/WHPX com 8 GB de RAM, 4 vCPUs, VirtIO GPU e QCOW2 descartável de 40 GB. O boot gráfico, o cadastro, a seleção de `vtbd0`, a confirmação destrutiva e a extração dos pacotes live passaram. O instalador baixou `base.txz` (156 MB), mas a escrita no QCOW2 parou em 1.270.431.744 bytes por mais de quatro minutos, com CPU do QEMU ainda ocupada; a janela só mostrava o tempo da etapa, sem explicar a atividade. A VM foi encerrada. Instalação concluída, primeiro boot, KDE, áudio USB, Wine e hardware real não foram validados.
- O QCOW2 descartável deste reteste foi removido depois de releases posteriores. A ISO base `dist/Brasa-15.1-amd64.iso` permanece preservada. A imagem é experimental e não deve ser usada em disco com dados importantes.


## ISO WHPX offline-catalog-progress (27/10/2026)

- Tag da release: [`brasa-whpx-offline-catalog-progress-2026-10-27`](https://github.com/Mateus-Neinas/brasaOS/releases/tag/brasa-whpx-offline-catalog-progress-2026-10-27)
- Arquivo: `Brasa-live-whpx-offline-catalog-progress.iso`
- Tamanho: 1.072.185.344 bytes
- SHA-256: `46128E44AE12515E2386B6E406198E8FC7420E71C921C27978964627FAC3EED8`
- Mudanças: exporta o catálogo FreeBSD-ports embutido separadamente do cache para o sistema live e preserva o fallback para pacotes pela internet. A mensagem de progresso agora usa rótulos compreensíveis quando `bsdinstall` não informa a etapa.
- Testada em QEMU 11.1/WHPX com 8 GB de RAM, 4 vCPUs, VirtIO GPU e QCOW2 descartável de 40 GB. O ambiente gráfico, cadastro, seleção/confirmação de `vtbd0` e início da instalação passaram. `pkg install -l` não usou os pacotes locais, então houve atualização do catálogo online e extração dos 133 componentes gráficos. O assistente iniciou o download de `base.txz` com progresso visível. QEMU foi encerrado antes da conclusão para liberar memória do Windows, com uso de memória perto de 6 GB. A instalação completa, primeiro boot, KDE, Wine, áudio USB e hardware real não foram validados.
- O QCOW2 descartável deste teste foi removido depois de uma release posterior. `dist/Brasa-15.1-amd64.iso` e `.build/freebsd-bootonly.iso` são imagens base e permanecem preservadas. A ISO experimental não deve ser usada em disco com dados importantes.


## ISO WHPX pkgbase extract-test (27/10/2026)

- Tag da release: [`brasa-whpx-pkgbase-extract-test-2026-10-27`](https://github.com/Mateus-Neinas/brasaOS/releases/tag/brasa-whpx-pkgbase-extract-test-2026-10-27)
- Arquivo: `Brasa-live-whpx-pkgbase-extract-test.iso`
- Tamanho: 1.072.185.344 bytes
- SHA-256: `DCDEAD1F597C598386940EDF0FDAA5348C278D622CA20AF51FD007BF9D4657A5`
- Mudança: experimenta `bsdinstall script` com `COMPONENTS=base` e sem distribuições `.txz`, para evitar a extração monolítica. O construtor também lê o catálogo FreeBSD-ports separado da ISO de referência, sem duplicá-lo no cache.
- QEMU 11.1/WHPX, 8 GB RAM, 4 vCPUs, VirtIO GPU e QCOW descartável de 40 GB: boot live, fallback de pacotes gráficos e assistente passaram. A etapa pkgbase falhou ao atualizar o repositório com `Transient resolver failure`; não baixou os pacotes da base e não mediu extração. O QCOW foi particionado, mas nenhum sistema inicializável foi instalado. KDE, Wine, áudio USB e hardware real não foram validados.
- O QCOW descartável deste teste foi removido após a publicação da release pkgbase resolver-fix. As imagens base foram preservadas. A ISO experimental não deve ser usada em computador com dados importantes.


## ISO WHPX pkgbase resolver-fix (27/10/2026)

- Tag da release: [`brasa-whpx-pkgbase-resolver-fix-2026-10-27`](https://github.com/Mateus-Neinas/brasaOS/releases/tag/brasa-whpx-pkgbase-resolver-fix-2026-10-27)
- Arquivo: `Brasa-live-whpx-pkgbase-resolver-fix.iso`
- Tamanho: 1.072.187.392 bytes
- SHA-256: `B77B83D3B14A1FC578E3CA8E9994EBD94939DB696154E06FCBE41EC3C45FE36B`
- Mudança: semeia `/mnt/etc/resolv.conf` no script pkgbase modificado, para que o `pkg --rootdir /mnt` tenha DNS antes de buscar a base.
- QEMU 11.1/WHPX, 8 GB RAM, 4 vCPUs, VirtIO GPU e QCOW descartável de 40 GB: boot live, instalação local dos componentes gráficos e fallback de rede passaram; cadastro, senha, seleção/confirmação de `vtbd0` e particionamento passaram. A etapa `FreeBSD Installer` permaneceu em 94% por mais de dois minutos, sem crescimento adicional do QCOW ou mensagem de erro visível; a instalação base não concluiu. O ajuste de resolver ainda não está confirmado como eficaz para pkgbase, não houve medição de velocidade e não há sistema inicializável. KDE, Wine, áudio USB e hardware real não foram validados.
- A ISO é experimental. Não use num computador com dados importantes. `dist/Brasa-15.1-amd64.iso` e `.build/freebsd-bootonly.iso` são imagens base e permanecem preservadas.
- Após publicar esta release, foram removidos os dois QCOWs de teste pkgbase anteriores, as duas ISOs experimentais antigas e os logs/capturas temporários. A ISO desta release foi mantida localmente; as imagens base foram conferidas por SHA-256.


## ISO WHPX pkgbase no-hidden-retry (27/10/2026)

- Tag da release: [`brasa-whpx-pkgbase-no-hidden-retry-2026-10-27`](https://github.com/Mateus-Neinas/brasaOS/releases/tag/brasa-whpx-pkgbase-no-hidden-retry-2026-10-27)
- Arquivo: `Brasa-live-whpx-pkgbase-no-hidden-retry.iso`
- Tamanho: 1.072.187.392 bytes
- SHA-256: `CF0C89903D7D6BAE843DAD22C1EFA4C6350B4E043A08C1C18D9E825EA64BE1A0`
- Mudança: se a atualização do catálogo ou o download dos pacotes FreeBSD-base falhar no modo não interativo, a mídia sai com erro claro em vez de tentar abrir a pergunta de repetição do `bsddialog`. Também substitui um título genérico específico no texto da barra.
- Testada em QEMU 11.1/WHPX com 8 GB RAM, 4 vCPUs, VirtIO GPU e QCOW descartável de 40 GB: boot live, componentes gráficos locais/rede, assistente, conta e particionamento passaram. A instalação da base permaneceu sem gravações adicionais no QCOW após criar as partições por mais de dois minutos; nenhum erro foi capturado antes de encerrar, então a correção de saída em erro ainda não foi exercitada. Não houve instalação concluída nem medição de velocidade. KDE, Wine, áudio USB e hardware real não foram validados.
- Release experimental; não use num disco com dados importantes. As ISOs base permanecem preservadas.
