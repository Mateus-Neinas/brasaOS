# Instalador Brasa — plano e estado verificável

## Meta de produto

Iniciar por uma mídia x86-64, escolher idioma, informar o nome e a senha da conta, selecionar o disco mostrando claramente modelo e tamanho e confirmar uma única vez a operação destrutiva. Depois, instalar o sistema, configurar desktop e conta, e reiniciar na tela de login. O mesmo segredo para conta pessoal e administração só deve ser oferecido com explicação clara; nenhum segredo deve ser predefinido ou gravado em texto simples.

## Estado atual

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
