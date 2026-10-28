# Brasa OS — especificação do produto

Brasa OS é um desktop para PCs x86-64 baseado em FreeBSD. A direção de produto combina uma interface visual refinada, áudio class compliant com seleção simples de dispositivo e um fluxo claro para aplicativos Windows compatíveis.

O requisito de áudio é genérico: reconhecer dispositivos pelos descritores USB Audio Class, sem lista fixa de fabricantes ou modelos, e permitir agregá-los usando um membro como referência de cadência. A meta inclui as versões da classe; o protótipo cobre apenas os caminhos UAC1/UAC2 do FreeBSD e ainda precisa implementar UAC3 e demonstrar estabilidade em hardware. A seleção de clock e os testes simulados atuais não comprovam esse requisito completo.

## Arquitetura escolhida

- **Base:** FreeBSD amd64. O projeto usa o kernel e drivers FreeBSD; não usa Linux como sistema base.
- **Desktop inicial:** KDE Plasma + SDDM, para construir uma sessão de desktop e testar o produto.
- **Áudio:** `uaudio(4)` para dispositivos USB Audio Class 1 e 2 no FreeBSD 15.1; a classe 3 não é suportada pelo driver atual. `sound(4)`/OSS acessa o hardware. PipeWire + WirePlumber com `pipewire-spa-oss-ng` oferece mistura, seleção de nós, servo/reamostragem adaptativa de relógios e agregados virtuais. A configuração Brasa cria uma saída estéreo espelhada e uma entrada multicanal que concatena os mapas de canais ativos publicados pelas fontes (até 64 canais), e prioriza o membro eleito como driver do grafo. O sincronismo entre clocks independentes é por ajuste de taxa, não por word clock compartilhado nem alinhamento de fase garantido. A lista de formatos suportados pelo kernel não garante que todas as funções ou firmware de cada modelo funcionem.
- **Apps Windows:** Wine amd64 com prefixos separados por app. O fluxo de importação e execução está no protótipo; não existe promessa de compatibilidade universal.
- **Recuperação:** ZFS boot environments e rollback seguem como parte da arquitetura pretendida, ainda não configurados pelo bootstrap.

## O que significa rodar apps Windows

Wine implementa interfaces de usuário do Windows e traduz chamadas para o sistema hospedeiro. Ele não fornece kernel Windows nem executa drivers de Windows. Apps com anti-cheat, DRM, drivers ou APIs específicas podem não funcionar. Cada app deve ter uma ficha de compatibilidade com versão, hardware, estado de instalação e funções que foram verificadas.

## Áudio como requisito de primeira classe

O protótipo usa o driver nativo do FreeBSD e oferece lista de dispositivos `pcm`, escolha da saída virtual agregada, teste de tom via SoX e agregação PipeWire. O backend `pipewire-spa-oss-ng` mede a cadência do hardware e expõe compensação de taxa; WirePlumber prioriza a fonte de relógio escolhida pelo usuário entre os nós ativos do grafo. Onde o OSS-ng expõe a localização USB na descrição, o perfil pode reencontrar o dispositivo após mudança de `pcmN`; caso contrário, requer recriação do perfil. Diagnóstico Brasa mostra propriedades de clock e prioridade para inspeção. Dispositivos com relógios independentes podem derivar em fase; a reamostragem adaptativa evita sobre/subfluxos, mas não equivale a sincronismo físico comum. Para captura multicanal com fase coerente, use interfaces ligadas por word clock ou outra sincronização de hardware. Há um bug aberto relatado para alguns UAC2 com clock compartilhado no FreeBSD 15.1, em que a captura ociosa pode reprogramar o clock de reprodução; a correção candidata ainda não foi integrada nem validada (detalhes em [patches/README.md](../patches/README.md)). Validar entrada e saída, canais, taxas das famílias 44,1/48 kHz, MIDI, hotplug, suspensão, latência, drift e coexistência com Wine em hardware real. UAC compliance não implica acesso a controles proprietários, baixa latência garantida ou suporte a ASIO.

## Marcos de produto

1. Inicializar uma instalação FreeBSD amd64 e usar a sessão Plasma.
2. Validar áudio interno e duas interfaces USB UAC em várias conexões e após suspensão, incluindo deriva, xruns e recuperação de hotplug no agregado.
3. Criar um tema visual Brasa para o Plasma, dock/painel, onboarding e central de controle próprios.
4. Testar aplicativos Windows escolhidos e publicar resultados por app/hardware.
5. Construir imagem bootável, atualização reproduzível, assinatura e rollback ZFS.
6. Rodar testes de regressão em hardware antes de distribuir.

## Estado verificável

O workspace possui uma ISO Brasa baseada no FreeBSD 15.1 `bootonly`, bootstrap, tema KDE, utilitários de áudio, importador Wine e um fluxo visual de instalação em desenvolvimento. A release r7 inicia o ambiente live JWM e o assistente gráfico, particiona um QCOW descartável e extrai os conjuntos locais `base`/`kernel`, mas a configuração do KDE não terminou. O próximo perfil reduz o conjunto KDE para Plasma Desktop/KWin X11 e agrupa os pacotes numa transação, preservando o caminho de download pela rede. A redução estimada usa o catálogo embutido numa ISO de referência e ainda não mede a duração real. O sistema instalado, sessão KDE, áudio USB e Wine seguem sem validação. `scripts/self-check.sh` usa comandos simulados e não substitui esses testes. Veja [docs/PROTOTYPE.md](PROTOTYPE.md).

## Referências

- [FreeBSD Handbook — desktops](https://docs.freebsd.org/en/books/handbook/desktop/)
- [FreeBSD Handbook — som e multimídia](https://docs.freebsd.org/en/books/handbook/multimedia/)
- [FreeBSD Handbook — Wine](https://docs.freebsd.org/en/books/handbook/wine/)
- [FreeBSD `snd_uaudio(4)` manual](https://man.freebsd.org/cgi/man.cgi?query=snd_uaudio&sektion=4)
- [Driver `uaudio.c` da série FreeBSD 15.1](https://github.com/freebsd/freebsd-src/blob/releng/15.1/sys/dev/sound/usb/uaudio.c)
- [PipeWire FreeBSD OSS-ng backend](https://github.com/kev009/pw-oss)
- [PipeWire Combine Stream](https://pipewire.pages.freedesktop.org/pipewire/page_module_combine_stream.html)
- [PipeWire driver clocks](https://docs.pipewire.org/1.6/page_driver.html)
- [WirePlumber node priorities](https://pipewire.pages.freedesktop.org/wireplumber/daemon/configuration/priorities.html)

