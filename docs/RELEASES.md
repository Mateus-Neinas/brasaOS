# Releases das ISOs

Toda imagem ISO criada deve receber uma release própria no GitHub, inclusive quando for experimental, incompleta ou sabidamente defeituosa. Não reutilize tags: use uma tag por artefato, anexe a ISO exata e registre data, hash SHA-256, estado conhecido, limitações e se passou por boot e teste de instalação.

Para publicar manualmente pelo GitHub, crie uma release em `https://github.com/Mateus-Neinas/brasaOS/releases/new`, informe a tag correspondente, copie as notas documentadas e anexe a ISO. A release não substitui o histórico de código: faça commits e push dos fontes e documentação separadamente.

## ISO progress-fix (27/10/2026)

- Tag pretendida: `brasa-progress-fix-2026-10-27`
- Arquivo: `Brasa-live-progress-fix.iso`
- Tamanho: 1.305.520.128 bytes
- SHA-256: `D4AF49B2D8B18F60DAD6204D4FE201FDBC84F438B61312179A0CA6D442313299`
- Estado: experimental. Abriu o ambiente gráfico e o assistente até a lista de discos; a seleção não avançou. O disco virtual permaneceu sem instalação. Contém a correção do monitor de processos do instalador.
- Não validado: instalação completa, login, KDE, áudio USB, Wine e hardware real.

## ISO disk-picker (27/10/2026)

- Tag pretendida: `brasa-disk-picker-2026-10-27`
- Arquivo: `Brasa-live-disk-picker.iso`
- Tamanho: 1.305.522.176 bytes
- SHA-256: `74AB22BF646DA22D1FDCA272D1F73BBF09EC224402B79ECA53D6A7FE84F97E8A`
- Estado: experimental, construída a partir da mídia Brasa existente com cache de pacotes e correção da estrutura de colunas Zenity para lista de discos com seleção por rádio, inicialmente marcando o primeiro disco elegível. Verificação estrutural confirmou catálogo El Torito e payload Brasa presente.
- Ainda não inicializada em QEMU após a correção. Não validado: instalação completa, primeiro login, KDE, áudio USB, Wine e hardware real.
