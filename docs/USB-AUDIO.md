# Áudio USB: requisito e evidências

O requisito do Brasa é aceitar interfaces pelos descritores USB Audio Class, sem lista fixa de marcas, oferecer agregação com um dispositivo como referência e demonstrar estabilidade comparável à do macOS. Este requisito permanece em aberto. Uma configuração gerada corretamente e testes com comandos simulados não demonstram estabilidade do transporte USB nem de relógios independentes.

| Parte do requisito | Implementação atual | Evidência disponível e trabalho pendente |
| --- | --- | --- |
| USB Audio Class 1 e 2 | Driver `snd_uaudio` do FreeBSD | Os caminhos existem no driver upstream. O Brasa ainda precisa compilar e executar sua instalação e exercitar interfaces reais. |
| USB Audio Class 3 e revisões posteriores | Ausente no protótipo | O parser FreeBSD ainda pula descritores de áudio das revisões 3 ou superiores. Exige implementação no driver, incluindo descoberta de formatos, canais, clocks e controles. |
| Escolha de referência | Prioridades WirePlumber para o membro escolhido e sua direção oposta | Verificação simulada da regra. O monitor distingue driver/seguidor no formato real do `pw-top`; falta demonstrar o papel escolhido durante agregação real. |
| Cadência dos seguidores | Servo de taxa OSS-ng e reamostragem PipeWire | Recurso do backend usado pelo Brasa; falta medir drift, sobre/subfluxo e qualidade com relógios físicos independentes. |
| Captura multicanal agregada | Concatenação dos mapas das fontes, até 64 canais | Teste simulado de duas fontes de 32 canais verifica o mapa combinado e nomes de destino únicos. A tentativa de 65 canais falha preservando os dois arquivos anteriores e removendo a configuração parcial. Falta executar a captura real. |
| Recuperação e estabilidade | Correspondência por descrição física quando única; diagnóstico e monitor | Fixtures cobrem renumeração, reset intermediário de contador, troca de ID e uma atualização sem o dispositivo. O monitor marca a janela interrompida. Recuperação de USB, suspensão e reprodução/gravação prolongadas continuam sem validação em hardware. |

## Trabalho necessário no driver para UAC3

O caminho atual não deve ser liberado simplesmente tratando UAC3 como UAC2. A detecção de revisão precisa considerar o protocolo da interface e o layout correto do cabeçalho. Descritores de streaming e de canais precisam ser decodificados com seus próprios tamanhos e referências; controles de clock, formatos e clusters precisam ser resolvidos antes de anunciar capacidades ao PCM. Leitura de comprimentos e referências deve rejeitar dados incompletos ou inválidos antes de acessar campos. Depois são necessários compilação do módulo, ensaios de descritores e testes de transporte USB real.

A revisão 4.0 também está publicada pela USB-IF e precisa de uma avaliação própria antes de qualquer declaração de compatibilidade. A meta genérica não termina no subconjunto UAC1/UAC2 hoje disponível no FreeBSD.

## Evidência necessária para concluir estabilidade

Executar entrada, saída e duplex nas taxas e mapas anunciados por cada interface; repetir início/parada, hotplug do mestre e dos seguidores e suspensão/retomada. Agregar interfaces com osciladores independentes, manter carga real prolongada e medir xruns, continuidade de amostras, drift, latência e recuperação. Comparar com macOS sob o mesmo hardware, formato e carga antes de declarar estabilidade equivalente. Para fases fisicamente coerentes entre interfaces, também é necessário testar sincronismo de hardware compatível; reamostragem e compensação de latência não provam alinhamento físico de fase.

## Fontes da auditoria

- [FreeBSD 15.1: uaudio.c](https://github.com/freebsd/freebsd-src/blob/releng/15.1/sys/dev/sound/usb/uaudio.c)
- [OSS-ng: servo e configuração](https://github.com/kev009/pw-oss)
- [PipeWire: formato produzido por pw-top](https://github.com/PipeWire/pipewire/blob/master/src/tools/pw-top.c)
- [PipeWire: limite e posições de canais](https://github.com/PipeWire/pipewire/blob/master/spa/include/spa/param/audio/raw.h)
- [USB-IF: Audio Devices Release 4.0](https://www.usb.org/document-library/usb-audio-devices-release-40-and-adopters-agreement)
