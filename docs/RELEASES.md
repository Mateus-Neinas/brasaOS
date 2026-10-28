# Releases das ISOs

Todas as alterações de código e os resultados de cada build devem ser versionados e documentados no Git. Preserve as ISOs-base e mantenha o total de ISOs abaixo de 10 GB. A primeira versão com login gráfico confirmado recebe o título alpha solicitado pelo usuário; as versões beta começam quando ele considerar o sistema do seu gosto e seguro.

## ISO alpha_1.37: correção da sessão Plasma (28/10/2026)

- Arquivo local: `.build/Brasa-live-r37-plasma-session-2026-10-28.iso`
- Tamanho: 1.284.982.784 bytes
- SHA-256: `FF215E6CAD3AE4998A9865CEEFCFBB1F369971E84A13EB9C3DC3DC6635849084`
- Código de instalação: usa o meta pacote `plasma6-plasma` e inclui explicitamente o gerenciador de atividades, o widget de áudio e o serviço de atalhos; garante que `/home/<usuário>/.config` pertence à conta gráfica.
- r37 foi reconstruída e validada pelo construtor; ISO local acumulada (incluindo imagens-base) ocupa 3.662.972.928 bytes, abaixo do limite de 10 GB.
- Teste limpo r37: QEMU TCG com 8 GiB RAM, 4 vCPUs, vídeo std/128 MiB e QCOW novo de 40 GiB. O instalador mostrou somente o disco virtual `vtbd0`, extraiu os 860 pacotes, concluiu as configurações adicionais e mostrou a confirmação de sucesso.
- O primeiro boot foi feito pelo QCOW, com a ISO ejetada e a ordem de boot alterada para disco. O FreeBSD 15.1 iniciou, SDDM apareceu e autenticou com sucesso a conta `brasa` (nome visível `mateus`). O desktop Plasma carregou com papel de parede e painel no VT9; abrir o Konsole pelo atalho `Ctrl+Alt+T` mostrou o prompt `brasa`. O primeiro diagnóstico de tela preta veio de observar os VTs de console em texto (VT1/VT2); o desktop estava no VT9. Os avisos de portal DBus, KWin e PulseAudio no log da sessão não impediram o uso do desktop.
- Instalação limpa r37, boot pelo disco, login gráfico, painel KDE e Konsole estão confirmados. A validação de áudio USB class-compliant em interface física e instalação em hardware real seguem pendentes.
- Áudio USB class-compliant em interface física e instalação em hardware real seguem sem validação.

### Primeiro login KDE confirmado no QCOW r36 (28/10/2026)

- O instalador r36 concluiu em cerca de 7 minutos em QEMU/WHPX e gravou base, kernel, usuário, KDE, áudio e Wine no disco de 40 GiB.
- No primeiro boot, SDDM autenticou o usuário `brasa`; o rótulo exibido para a conta era `mateus`. No disco de teste, instalaram-se `plasma6-plasma`, `plasma6-kactivitymanagerd`, `plasma6-plasma-pa` e `plasma6-kglobalacceld`, e corrigiu-se a propriedade de `/home/brasa/.config`.
- Após essas alterações manuais, o desktop KDE carregou com painel e Konsole. Isso confirma que o bloqueio estava no conjunto/configuração dos componentes da sessão, e que QEMU/VGA consegue exibir Plasma; não prova ainda uma instalação limpa pela ISO.
- As correções foram incorporadas ao bootstrap da r37. A instalação limpa dessa ISO em um QCOW novo ainda será necessária para confirmar que o instalador aplica o conjunto completo sem intervenção manual. Áudio USB físico e instalação em hardware real continuam sem teste.

## ISO de referência: r36 (28/10/2026)

- Arquivo local: `.build/Brasa-live-r36-install-progress-2026-10-28.iso`
- Tamanho: 1.285.017.600 bytes
- SHA-256: `D9A931F7F741326A1791A6A02EC70AED4418F57BC2E81E90DE0099AA4A483475`
- Mudanças: preserva a correção de DNS da r35 e transmite para a janela de progresso a linha atual do script pós-instalação. A saída serial de diagnóstico foi removida.
- Build validado pelo construtor. Em QEMU/WHPX com 8 GiB RAM, 4 vCPUs e VirtIO GPU de 128 MiB, o assistente abriu, mostrou somente `vtbd0` de 40 GiB e instalou a base/kernel, conta, KDE, componentes de áudio e Wine. A confirmação de sucesso apareceu após cerca de 7 minutos.
- A linha da interface acompanhou as etapas de pacote, inclusive a extração de KDE e instalação de Wine; o disco recebeu gravações durante a instalação.
- Primeiro boot exibiu o wallpaper sem painel e sem os serviços essenciais da sessão. No QCOW, a instalação manual dos componentes indicados acima e a correção da propriedade de `~/.config` permitiram iniciar painel e Konsole.
- Nenhuma unidade física foi conectada. Instalação limpa corrigida, Wine funcional e áudio USB físico ainda não foram validados. r36 permanece como ISO de referência até a próxima imagem; as imagens-base foram preservadas.

### r29–r35: correções do fluxo pós-instalação (28/10/2026)

As tentativas r29–r34 corrigiram problemas sucessivos na passagem de dados e no DNS. O r30 criou a conta e iniciou o bootstrap, mas falhou ao resolver o repositório. A r35 salvou o `resolv.conf` live antes de `bsdinstall config` e o restaurou no sistema-alvo; a resolução de `pkg.freebsd.org` no chroot e a instalação completa foram confirmadas. As ISOs intermediárias foram substituídas localmente, sem assets de release.

### Resultado do r20: erro do bsdinstall oculto (28/10/2026)

A inspeção de processos encontrou `bsddialog --title "Installation Error!"` ativo dentro de `bsdinstall`, atrás da janela Brasa de progresso. Ao sair da janela de progresso, o assistente informou que a instalação não terminou. O log visível confirmou a conclusão de `bsdinstall config` e parou em “preparando o script de instalação no sistema-alvo”. A mensagem exata do diálogo não foi recuperada, pois o arquivo temporário foi removido na saída. Isso confirma falha explícita, não espera normal do `bsdconfig`. A r21 contém a correção provável do shebang e instrumentação para preservar o log numa nova tentativa.

## ISO experimental r18 (28/10/2026)

- Arquivo local: `.build/Brasa-live-r18-bootstrap-output-2026-10-28.iso`
- Tamanho: 1.285.011.456 bytes
- SHA-256: `4F4F51A778D93B6E861D49CB458CE18654EDB8400B17BE080C79970A93B345A4`
- Mudança: preserva no progresso gráfico as linhas do instalador e do `pkg` enquanto o script pós-instalação roda, em vez de manter a mensagem inicial fixa.
- Teste: QEMU 11.1/WHPX, 8 GiB RAM, 4 vCPUs, VirtIO GPU 128 MiB e QCOW2 descartável de 40 GiB. O assistente abriu, aceitou os dados de conta, confirmou somente `vtbd0` e instalou base/kernel locais em cerca de um minuto. Depois permaneceu em `bsdconfig` por 632 s, sem novas gravações no QCOW; QEMU usou cerca de 6,3 GiB de RAM. A etapa do bootstrap em que o novo texto preserva a saída não foi alcançada nesse reteste. Instalação incompleta; KDE, primeiro boot, Wine, áudio USB físico e hardware real não testados.
- O processo QEMU foi encerrado e o QCOW de teste removido. A ISO r18 é a única ISO experimental Brasa mantida no diretório `.build`; as imagens-base foram preservadas. Nenhum asset experimental foi publicado como release.

### Resultado do r17

A r17 mostrou a mensagem da subetapa `bsdinstall-postinstall-start`, indicando que a chamada do script pós-instalação começou. Essa mensagem permaneceu por 624 s sem novas gravações no QCOW; os marcadores de retorno/limpeza não apareceram. O novo r18 muda a tela para refletir a última linha de saída do script quando essa fase for alcançada.

As entradas abaixo são registros históricos de builds e testes. A prioridade de versionamento é o código-fonte e a documentação no Git; uma ISO para download público só será publicada depois de passar pela instalação e pelo boot KDE previstos.

Em 27/10/2026, as 23 releases alpha/experimentais e seus 23 assets ISO foram removidos do GitHub a pedido do usuário para liberar armazenamento (26.319.869.952 bytes de assets). Os commits e tags Git foram mantidos. O histórico abaixo documenta os builds, mas os objetos de release e links de download já não existem.

## ISO r13: uma passagem de cache e retorno normal do instalador (27/10/2026)

- Tag: `brasa-r13-single-cache-pass-2026-10-27`
- Arquivo: `Brasa-live-staged-install-r13-single-cache-pass-2026-10-27.iso`
- Tamanho: 1.285.007.360 bytes
- SHA-256: `277ED8B68D703C901B22D9A252E182EC80BF85343BB8E846400C58FBBCEE97B2`
- Mudanças: elimina uma extração temporária redundante de aproximadamente 450 MB do cache de pacotes no boot live; impede que uma saída normal/cancelamento do assistente abra em seguida o instalador texto do FreeBSD; o construtor valida essas duas condições na ISO.
- Teste em QEMU 11.1/WHPX, `core2duo`, 8 GiB RAM, quatro vCPUs, VirtIO GPU 128 MiB e QCOW2 descartável de 40 GiB: boot live, cadastro por teclado, seleção do único disco virtual `vtbd0` e confirmação de apagamento passaram. A base e o kernel locais foram instalados. O marcador `Configurando KDE, áudio USB e suporte do computador` é escrito antes do script pós-instalação, portanto não prova que o KDE já estava sendo instalado. A barra ficou perto de 10 minutos em 92%; o QCOW parou em 1.259.864.064 bytes e não houve escrita de bloco por vários minutos. O processo QEMU continuou usando CPU. Em seis verificações não havia conexão TCP externa do QEMU; o DNS no host resolvia `pkg.freebsd.org`. A tela/log não identificam o comando interno. QEMU foi encerrado no limite de diagnóstico e o QCOW descartável removido.
- O script pós-instalação descompacta primeiro um arquivo de projeto de 33.544 bytes e prepara contas; em seguida o bootstrap verifica/instala `pkg` e começa as consultas de pacotes. A espera pode ter ocorrido antes ou depois dessas operações. Não foi possível confirmar download, resolução de dependências KDE ou suporte de hardware.
- Não validado: conclusão do KDE, configuração final de suporte à máquina, primeiro boot, Wine, áudio USB class-compliant em hardware real e instalação em computador físico. O driver `snd_uaudio` permanece incluído na base/kernel da mídia. Release experimental; não use em disco com dados importantes. A ISO base `dist/Brasa-15.1-amd64.iso` foi preservada.
- O título temporário no GitHub foi `alpha_1.22`; a release e o asset foram removidos na limpeza de armazenamento solicitada.

## ISO r14: saída do bootstrap no progresso (27/10/2026)

- Título de versão interno: `alpha_1.23` (sem release/asset no GitHub).
- Arquivo local: `.build/Brasa-live-r14-pkg-trace-2026-10-27.iso` (removido após gerar a r15).
- Tamanho: 1.285.007.360 bytes; SHA-256 `FA9A822775E0676E4F7B736684E707E2B0846207FF6B8F9F533E1E2FE0324B13`.
- Mudanças: imprime as etapas de preparação do `pkg`, consultas de disponibilidade e grupos de KDE, áudio e Wine; o diálogo de progresso preserva a última linha útil.
- QEMU 11.1/WHPX, `core2duo`, 8 GiB, 4 vCPUs, VirtIO GPU 128 MiB e QCOW2 descartável de 40 GiB: o fluxo gráfico e a seleção de `vtbd0` funcionaram. A etapa mostrou `bsdconfig` por cerca de dez minutos, sem gravações no QCOW desde 23:46 e sem avanço no log serial. Instalação não concluiu. QCOW removido.

## ISO r15: rastreamento do `bsdinstall config` (28/10/2026)

- Título de versão interno: `alpha_1.24` (sem release/asset no GitHub).
- Arquivo local mais recente: `.build/Brasa-live-r15-bsdconfig-trace-2026-10-27.iso`.
- Tamanho: 1.285.009.408 bytes; SHA-256 `30C09815403F60DAA9602C3BD33E5F80D9D89D8A529FCC60103A48A028CB8C87`.
- Mudanças: acrescenta marcadores no script `bsdinstall config` para localizar cópias de configuração, chamada de `newaliases` e fim da etapa; valida que os marcadores estão dentro da ISO.
- QEMU 11.1/WHPX, `core2duo`, 8 GiB, 4 vCPUs, VirtIO GPU 128 MiB e QCOW2 descartável de 40 GiB: boot live e assistente gráfico passaram; só `vtbd0`/40 GiB foi listado e confirmado. Base/kernel locais foram extraídos. A tela permaneceu em `bsdconfig` por cerca de dez minutos; o QCOW ficou sem gravações desde 00:09:10 até encerrar às 00:17, e QEMU continuou usando CPU. Os marcadores inseridos em `bsdinstall config` não apareceram no serial; o subcomando exato ainda não foi identificado. QCOW removido.
- Pesquisa: documentação oficial descreve busca de arquivos de mapa de teclado no `bsdconfig`, sem indicar espera de vários minutos. Há relatos de atualização lenta do catálogo `pkg` (4–6 minutos), mas essa atividade distinta não explica a espera observada. KDE instalado, primeiro boot, Wine e USB Audio físico continuam sem validação.
- Nenhuma release/asset experimental foi publicada. As ISOs antigas foram removidas localmente; r15 é a única ISO Brasa experimental mantida junto das imagens-base.

## ISO r16: estado por subetapa do `bsdinstall config` (28/10/2026)

- Título de versão interno: `alpha_1.25` (sem release/asset no GitHub).
- Arquivo local mais recente: `.build/Brasa-live-r16-bsdconfig-state-trace-2026-10-28.iso`.
- Tamanho: 1.285.011.456 bytes; SHA-256 `8DC301EB6B80D56A33B0E7B5D1488F93006D3A7CD7CD7922D73C07A1D7AF3168`.
- Mudanças: o instalador acompanha subfases de `bsdinstall config` pelo arquivo de estado compartilhado e troca a mensagem de progresso conforme cada marcador.
- QEMU 11.1/WHPX, `core2duo`, 8 GiB, 4 vCPUs, VirtIO GPU 128 MiB e QCOW2 descartável de 40 GiB: boot, assistente, senha e confirmação do único disco `vtbd0` passaram; base/kernel locais foram extraídos. A tela permaneceu em `bsdconfig` por 10 minutos. O QCOW não recebeu gravações desde 00:28:03; QEMU manteve uso alto de CPU e chegou a cerca de 6,4 GiB de RAM. Nenhuma nova mensagem de subetapa apareceu; a instrumentação ainda não localizou o comando parado. VM encerrada por QMP e QCOW removido.
- r16 é a única ISO Brasa experimental local, além das imagens-base. Não foi publicada release; as alterações de código e documentação seguem no Git. Instalação completa, boot do disco, KDE, Wine e áudio USB real continuam sem validação.


## ISO r9: KDE reduzido e cache live restaurado (27/10/2026)

- Tag da release: [`brasa-r9-kde-reduced-cache-fallback-2026-10-27`](https://github.com/Mateus-Neinas/brasaOS/releases/tag/brasa-r9-kde-reduced-cache-fallback-2026-10-27)
- Arquivo: `Brasa-live-graphical-firstboot-audio-r9-kde-cache-2026-10-27.iso`
- Tamanho: 1.284.970.496 bytes
- SHA-256: `f80389c31c65b4f3db4679970733a79c0555e6d9ded1e2cfcc8743a4f1989f57`
- QEMU 11.1/TCG, 8 GiB RAM, 8 vCPUs, VGA 128 MiB e QCOW2 de 40 GiB: o cache live da r7 instalou 133 dependências locais e buscou 11 pacotes restantes pela rede. O assistente abriu, aceitou a criação da conta pelo teclado e mostrou apenas `ada0` QEMU HARDDISK, 40 GB, `QM00001`. Depois da confirmação destrutiva do disco virtual, particionou e extraiu base/kernel. Com 10 minutos, estava na configuração de KDE; o QCOW chegou a 1.259.208.704 bytes e ficou sem mudança por pelo menos 55 segundos, com o contador em cerca de dois minutos nessa etapa. A VM foi fechada via QMP pelo limite; QCOW parcial preservado.
- Inclui `snd_uaudio.ko`, base/kernel locais e cache de pacotes live com fallback online. O conjunto KDE reduzido estima 683 pacotes/1.378 MiB no catálogo da r6, contra 960/2.358,5 MiB na configuração anterior; o tempo real e a transação KDE ainda não foram validados. Não validado: instalação completa, primeiro boot, KDE, Wine e interfaces USB físicas.

## ISO r8: KDE menor, boot gráfico falhou sem cache (27/10/2026)

- Tag da release: [`brasa-r8-minimal-kde-no-cache-boot-failed-2026-10-27`](https://github.com/Mateus-Neinas/brasaOS/releases/tag/brasa-r8-minimal-kde-no-cache-boot-failed-2026-10-27)
- Arquivo: `Brasa-live-graphical-firstboot-audio-r8-minimal-kde-2026-10-27.iso`
- Tamanho: 756.109.312 bytes
- SHA-256: `dbddae317ec8345e997dd9b89bf5da3804ff7a66df86b8e46bed206f31bb2a8f`
- Estado: experimental e defeituosa. Em QEMU/TCG com 8 GiB, 8 vCPUs, VGA de 128 MiB e QCOW2 descartável de 40 GiB, não abriu o assistente gráfico. O log identificou uma cópia de `/usr/local` para o mesmo diretório no caminho sem cache. O QCOW2 permaneceu em 197.632 bytes; nenhum disco foi particionado nem alterado. A sessão foi encerrada e o QCOW mantido em `%TEMP%`.
- A ISO contém `base.txz`, `kernel.txz` e o driver `snd_uaudio.ko`. Seu bootstrap Brasa usa um conjunto Plasma Desktop/KWin X11 menor e uma única transação, mas o instalador nem chegou a essa etapa. Primeiro boot, KDE, Wine, áudio USB real e instalação completa não foram testados. O próximo build volta a usar o cache live da r7 com fallback pela internet.

## ISO r7: permissão do instalador corrigida (27/10/2026)

- Tag: `brasa-install-permission-2026-10-27`
- Arquivo: `Brasa-live-graphical-firstboot-audio-r7-install-permission-2026-10-27.iso`
- Tamanho: 1.284.968.448 bytes
- SHA-256: `B41AC6D49AD17EB853A009762FEE6089E7FFB2AC76EEFEC723873D1ABFEB2AAD`
- Estado: experimental. No QEMU TCG (8 GiB, 4 vCPUs, VGA 128 MiB, QCOW2 de 40 GiB), iniciou direto no assistente gráfico, permitiu criar a conta, selecionar `ada0` e confirmar o disco virtual. A correção dos modos ISO removeu o erro `Permission denied`; o particionamento e a extração local de base/kernel avançaram até a configuração do KDE. O QCOW chegou a 1.259.339.776 bytes, depois ficou sem novas gravações por mais de cinco minutos na configuração de desktop; a VM foi encerrada a pedido do usuário. Instalação completa, primeiro boot, KDE, Wine, áudio USB funcional e hardware real não foram validados.
- A imagem contém `snd_uaudio.ko` (133.368 bytes) e os conjuntos oficiais FreeBSD locais. O fallback de rede permaneceu ativo; foi removida uma segunda atualização redundante do catálogo. O código atual inclui a correção do helper executável; a próxima etapa investiga a rede/DNS usada ao instalar KDE dentro do sistema-alvo.

## ISO local-package-cache experimental (27/10/2026)

- Tag: `brasa-local-pkg-cache-failed-2026-10-27`
- Arquivo: `Brasa-live-graphical-firstboot-audio-r6-local-packages-2026-10-27.iso`
- Tamanho: 837.859.328 bytes
- SHA-256: `FD52196D9AE93DCCDA5E4AAEF0BF99467997D49FC23AB1FF34B7A554E6AC00AA`
- Estado: experimental e não recomendada para teste. A variante reduziu o cache ao conjunto de 133 pacotes com nomes normalizados, mas no QEMU TCG (8 GiB, VGA 128 MiB, QCOW2 de 40 GiB) voltou ao menu textual antes de abrir a interface gráfica. O QCOW2 permaneceu em 197.632 bytes e não foi instalado. O método de cache local foi revertido; a ISO r5 continua sendo a última variante que chegou à tela gráfica.
- `snd_uaudio.ko` e os conjuntos oficiais `base.txz`/`kernel.txz` foram herdados da r5. Instalação completa, KDE, Windows/Wine/Proton, áudio USB real e hardware físico não foram validados.

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


## ISO WHPX pkgbase bounded-fetch diagnostic (27/10/2026)

- Tag: [`brasa-whpx-pkgbase-bounded-fetch-diagnostic-2026-10-27`](https://github.com/Mateus-Neinas/brasaOS/releases/tag/brasa-whpx-pkgbase-bounded-fetch-diagnostic-2026-10-27)
- Arquivo: `Brasa-live-whpx-pkgbase-bounded-fetch-diagnostic.iso`
- Tamanho: 1.072.187.392 bytes
- SHA-256: `6494E69475B10592DE8F32CDD407C8677D889AE7E66AE9FFC02B02B6ED5EBBBE`
- Mudança: limita a espera de download de pkg a 30 segundos e uma repetição; inclui o ajuste de DNS e a saída sem pergunta oculta no modo não interativo.
- Teste em QEMU/WHPX com 8 GiB e quatro vCPUs: o ambiente live, assistente, conta, seleção/confirmação de disco e particionamento funcionaram. A instalação da base permaneceu sem novas gravações no QCOW por cerca de 24 minutos, com consumo crescente de CPU; não concluiu e nenhum erro de pkg foi visível. A ISO não foi instalada nem produziu sistema inicializável. KDE, Wine, USB Audio e hardware real não foram validados.
- Release experimental. As imagens base foram preservadas.

## ISO WHPX pkgbase minimal phases (27/10/2026)

- Tag: [`brasa-whpx-pkgbase-minimal-phases-2026-10-27`](https://github.com/Mateus-Neinas/brasaOS/releases/tag/brasa-whpx-pkgbase-minimal-phases-2026-10-27)
- Arquivo: `Brasa-live-whpx-pkgbase-minimal-phases.iso`
- Tamanho: 1.072.191.488 bytes
- SHA-256: `4C8992E5DD058E5BB941F939C3081734D59325A887504BF2137E13F540CACE9A`
- Mudança: troca `COMPONENTS=base` por `COMPONENTS=minimal` para evitar resolver e instalar os conjuntos `devel` e `optional` durante a instalação inicial; adiciona mensagens que identificam as quatro fases do pkgbase. Mantém os limites de fetch em 30 segundos e uma repetição.
- Teste QEMU/WHPX com 8 GiB, quatro vCPUs e VirtIO GPU 128 MiB: tanto `qemu64,-svm` quanto `core2duo` pararam no boot no mesmo texto `random: unblocking device.`. O QCOW não recebeu gravações; o fluxo gráfico e a instalação pkgbase não foram alcançados. A troca de modelo de CPU não alterou o resultado. A redução `minimal` ainda precisa ser testada depois de corrigir o bloqueio de boot/ambiente QEMU.
- Release experimental. Não use num computador com dados importantes. As ISOs base foram preservadas.

## ISO graphical firstboot audio r5 (27/10/2026)

- ISO: `Brasa-live-graphical-firstboot-audio-r5-2026-10-27.iso`
- Tamanho: 1.285.003.264 bytes
- SHA-256: `353F226C9E5F78400F579393931DC5E3721D13885BD0C5ABCC6996DE39AA0B98`
- Mudanças: auto-inicia o live Brasa e a interface gráfica, normaliza scripts empacotados para LF para evitar falha de shell no FreeBSD e completa cinco arquivos ausentes do cache gráfico no momento da construção. Mantém os conjuntos base/kernel locais e `snd_uaudio.ko`.
- Teste QEMU/TCG: 8 GiB RAM, 4 vCPUs, VGA 128 MiB, disco SATA/QCOW2 descartável. A janela de boas-vindas Brasa abriu automaticamente. O teste ainda atualizou catálogos e baixou 11 componentes gráficos; não houve instalação nem gravação no QCOW. A sessão foi deixada aberta na tela inicial.
- WHPX parou em `random: unblocking device.` em duas combinações de vídeo. KDE pós-instalação, Wine/Proton, áudio USB em hardware e instalação em disco continuam sem validação. Release experimental.

## ISO Brasa staged install r10 (27/10/2026)

- Tag: [`brasa-r10-staged-install-2026-10-27`](https://github.com/Mateus-Neinas/brasaOS/releases/tag/brasa-r10-staged-install-2026-10-27)
- Arquivo: `Brasa-live-staged-install-r10-2026-10-27.iso`
- Tamanho: 1.284.970.496 bytes
- SHA-256: `D82808D8951835D5CDB15237F81BA5D7D54792DBA2A598BF06D052A47BFCAAB3`
- Mudanças: limita os downloads do `pkg` a 30 segundos por arquivo e uma repetição; separa a configuração pós-instalação em KDE/aplicativos essenciais, áudio USB/PipeWire e Wine/Gecko/Mono, com mensagens de etapa. Mantém `snd_uaudio` habilitado e usa o cache gráfico r7 como base do ambiente live, preservando fallback online.
- Teste QEMU/TCG com 8 GiB RAM, 4 vCPUs, VGA 128 MiB e QCOW2 descartável de 40 GB: o live processou o catálogo de 38.288 pacotes, extraiu os componentes gráficos locais e completou 11 dependências restantes pela rede; o assistente gráfico abriu e o menu Installer do FreeBSD foi alcançado. A sessão foi interrompida antes de escolher ou alterar o disco. WHPX parou em `random: unblocking device.` nesta máquina.
- As três transações novas de pós-instalação, a instalação completa, primeiro boot, KDE instalado, Wine, áudio USB em hardware e estabilidade em máquina real não foram validados. Release experimental; não use num disco com dados importantes. A imagem base foi preservada.

## ISO Brasa staged install r11 WHPX VirtIO (27/10/2026)

- Tag: `brasa-r11-whpx-virtio-2026-10-27`
- Arquivo: `Brasa-live-staged-install-r11-whpx-2026-10-27.iso`
- Tamanho: 1.285.005.312 bytes
- SHA-256: `1BFFE9477FB3C68CA6CADFF16AE2FE7DD3108F8FE487B5E493A2AB6AFAAD3D41`
- Mudança: inclui o módulo oficial `virtio-gpu-qemu-kmod` e configuração do framebuffer para testar a interface live com VGA VirtIO sob WHPX; preserva o KDE planejado, `snd_uaudio`, instalador gráfico e fallback online.
- Testada em QEMU 11.1/WHPX, 8 GiB RAM, 4 vCPUs, VirtIO GPU com 128 MiB e QCOW2 descartável de 40 GiB. O boot avançou além da mensagem `random: unblocking device`, preparou a rede, instalou dependências gráficas locais e buscou 11 componentes restantes pela rede; a janela de boas-vindas do Brasa abriu. O canal de teclado/QMP deixou de responder na tela inicial. Nenhuma conta ou partição foi criada e o instalador FreeBSD não foi iniciado. O QCOW2 descartável foi removido.
- Não validados: instalação completa, primeiro boot, KDE instalado, Wine/Proton, áudio USB em equipamento físico e instalação em hardware real. Release experimental; não use num disco com dados importantes. A ISO base permanece preservada.
