# Instalador Brasa — plano e estado verificável

## Meta de produto

Iniciar por uma mídia x86-64, escolher idioma, informar o nome e a senha da conta, selecionar o disco mostrando claramente modelo e tamanho e confirmar uma única vez a operação destrutiva. Depois, instalar o sistema, configurar desktop e conta, e reiniciar na tela de login. O mesmo segredo para conta pessoal e administração só deve ser oferecido com explicação clara; nenhum segredo deve ser predefinido ou gravado em texto simples.

## Estado atual

### Boot live e progresso visível (27/10/2026)

O teste com cache confirmou que a criação de um TAR de `/usr/local` no boot acrescentava uma cópia temporária de mais de 2 GB e trabalho extra em RAM. O script agora semeia o tmpfs diretamente dos pacotes incluídos na ISO e remove a cópia temporária depois, evitando gerar e depois desempacotar esse arquivo adicional. A janela do instalador agora usa o log do `bsdinstall` como texto principal e, se uma etapa não emitir linhas, mantém uma mensagem com o tempo decorrido em vez de parecer congelada.

A imagem `.build/Brasa-live-optimized-experimental.iso` preserva o boot da ISO Brasa existente, inclui a atualização e os pacotes cacheados, mede 1.305.520.128 bytes e tem SHA-256 `6D7DA61286CA0887F23576DDB25F87107176F97CFAE2398DE416D9D57192FCC3`. O QEMU usado para a inspeção foi iniciado com 8 GB de RAM e VGA de 128 MB; WHPX não funciona neste host, então o emulador usou TCG. O boot chegou à instalação de componentes e começou a extrair o pacote 57/191, mas ainda levou minutos em emulação por software. A tela de boas-vindas não apareceu nesta execução, o QCOW2 ficou em 197.632 bytes e foi removido após encerrar a VM. Nenhuma instalação de sistema ou alteração de disco foi feita.

Teste posterior documentado abaixo: no QEMU 11.1 deste host, WHPX com VGA padrão falha ao abrir o X; o driver VirtIO GPU FreeBSD elimina esse erro e abre a interface. O resultado não altera a compatibilidade de hardware real nem conclui a instalação.

O instalador gráfico seleciona o disco em uma janela e apresenta modelo, capacidade, identificador e confirmação explícita; depois usa `bsdinstall scriptedpart` para criar automaticamente o esquema de boot e as partições. Essa instalação real ainda não foi concluída. O acompanhamento do processo foi ajustado para reconhecer subprocessos encerrados, inclusive zumbis, em vez de deixar a barra aguardando um PID que já terminou. Essa correção está no código-fonte e exige uma nova ISO para validação em QEMU.

A ISO permanece experimental: KDE, instalação no disco, primeiro login, Wine e interfaces USB de áudio ainda não foram validados. Não instale em um disco real.

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
