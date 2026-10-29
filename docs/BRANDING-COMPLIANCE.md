# Conformidade de marca e redistribuição

Brasa está sendo construído para uso próprio e privado, baseado no Kubuntu. Nenhuma ISO modificada será publicada ou distribuída nesta fase. Este documento registra a identidade e os cuidados caso esse escopo mude; não constitui parecer jurídico.

## Identidade Brasa preparada

- Nome de produto: Brasa OS.
- Wordmark vetorial criado para este repositório: `branding/brasa-wordmark.svg`.
- Texto informativo para documentação e interface: `branding/NOTICE.txt`.
- A marca deve ser aplicada no branding do live system, instalador, tela de login, sessão Plasma, metadados do sistema e materiais de download.

## Se o projeto passar a redistribuir uma imagem modificada

1. Não apresentar a imagem como Kubuntu oficial nem sugerir aprovação da Canonical.
2. Substituir os elementos visuais e textuais de marca do Kubuntu/Ubuntu em todo o sistema modificado, inclusive no instalador e nos binários que os incorporam, seguindo a política vigente da Canonical.
3. A política da Canonical diz que a redistribuição de Ubuntu modificado associado às marcas requer aprovação/certificação/fornecimento pela Canonical; sem essa associação, as marcas devem ser removidas e o código-fonte recompilado para criar binários próprios. A equipe precisa avaliar essa exigência para cada componente afetado e buscar esclarecimento da Canonical quando necessário.
4. Preservar avisos de direitos autorais e licenças de cada pacote. Fazer inventário dos pacotes, firmware, codecs, fontes, artwork e arquivos de licença; “open source” não implica que todo firmware ou conteúdo da ISO seja software livre.
5. Distribuir o código-fonte correspondente quando a licença de um componente exigir. Registrar origem, versão, patches, configuração de build e checksums dos artefatos.
6. Revisar nomes/ícones de aplicativos, telas de boot, metadados de pacotes, repositórios, domínios e capturas de tela para não haver confusão de origem ou aprovação.
7. Fazer revisão jurídica e técnica da imagem final antes de publicar ISO/release.

## Limite do estado atual

`dist/kubuntu-26.04.1-desktop-amd64.iso` é uma cópia intacta da mídia oficial e permanece como referência de upstream. O SVG e os textos Brasa ainda não foram injetados na imagem. A ISO Brasa será local e privada; não será publicada como release.

## Fontes oficiais

- [Política de propriedade intelectual da Canonical](https://ubuntu.com/legal/intellectual-property-policy)
- [Marcas registradas Ubuntu/Canonical](https://ubuntu.com/legal/trademarks)
- [Imagem oficial Kubuntu 26.04.1](https://cdimage.ubuntu.com/cdimage/kubuntu/releases/26.04.1/release/)
