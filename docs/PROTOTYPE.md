# Instalador Brasa — plano e estado verificável

## Meta de produto

Iniciar por uma mídia x86-64, escolher idioma, informar o nome e a senha da conta, selecionar o disco mostrando claramente modelo e tamanho e confirmar uma única vez a operação destrutiva. Depois, instalar o sistema, configurar desktop e conta, e reiniciar na tela de login. O mesmo segredo para conta pessoal e administração só deve ser oferecido com explicação clara; nenhum segredo deve ser predefinido ou gravado em texto simples.

## Estado atual

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
