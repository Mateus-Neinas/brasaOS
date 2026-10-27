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
