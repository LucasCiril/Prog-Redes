# Telemetria BitDogLab: TCP e SQLite (entrega parcial)

## Estado dos testes e limitação

Esta entrega contém a implementação **prevista para o sensor VL53L0X** em `main.py` e um teste alternativo `teste_simulado.py` que gera valores **simulados** de distância na BitDogLab. **O aluno não teve acesso ao VL53L0X para ensaios físicos**, portanto a aquisição de distância real não foi validada e os valores transmitidos pelo teste alternativo **não são medições reais**. O professor poderá conferir comunicação TCP, persistência SQLite e consultas de médias com o teste simulado. Não executar `main.py` sem o VL53L0X, pois ele verifica a presença do sensor `0x29` e interrompe com mensagem de erro.

## Arquivos

- `main.py`: cliente MicroPython projetado para ler o VL53L0X no I2C0, GPIO0/GPIO1, e enviar dados via TCP.
- `vl53l0x.py`: driver MicroPython do sensor, derivado do projeto citado no arquivo.
- `teste_simulado.py`: cliente MicroPython alternativo para validar rede e servidor sem o sensor.
- `servidor.py`: servidor TCP Python, valida protocolo, grava no SQLite e calcula duas médias via SQL.
- `criar_banco.sql`: esquema SQL; `leituras.db` é criado automaticamente pelo servidor.
- `teste_sem_placa.py`: teste opcional, realizado inteiramente no computador.
- `evidencia.png`: incluir captura **real** do servidor após a execução de `teste_simulado.py`. Identificar como simulação.

## Configurar e executar

1. Instalar Python 3 no computador, MicroPython na BitDogLab e usar o Thonny para transferir arquivos.
2. Colocar computador e BitDogLab na mesma rede Wi-Fi de 2,4 GHz, quando aplicável. Em Windows, encontrar o IP do computador com `ipconfig`.
3. Editar `WIFI_SSID`, `WIFI_SENHA` e `IP_SERVIDOR` em `teste_simulado.py` (ou em `main.py` para sensor real); configurar o IP do **computador** como endereço do servidor.
4. No computador, na pasta do projeto, executar `python servidor.py` (ou `py servidor.py`). A porta TCP é **6666**; permitir acesso pelo firewall na rede privada, se solicitado.
5. No Thonny, salvar e **executar** `teste_simulado.py` na BitDogLab. Não renomear este arquivo para `main.py` na entrega, para manter os modos separados. O cliente transmite `BITDOG_SIMULADO;157\n`, e assim por diante, a cada dois segundos.
6. Verificar no terminal do computador as leituras e as médias dos últimos cinco minutos e da última hora. O SQLite cria `leituras.db` com `dispositivo`, `distancia_mm` e `instante` (UTC).
7. Tirar captura do terminal **durante a execução real** e salvar como `evidencia.png` na pasta. **Não usar saídas inventadas** como evidência de execução.
8. Compactar os arquivos citados e enviar o ZIP no Moodle.

## Uso futuro com sensor real

Conectar VL53L0X ao I2C0: SDA GP0, SCL GP1, GND e alimentação compatível com o módulo; copiar `vl53l0x.py` e `main.py` para a raiz da placa. `main.py` exige detecção do sensor no endereço `0x29`, realiza leituras e envia no formato `BITDOG01;distancia_mm\n`. **Não foi testado fisicamente nesta entrega**.

## Observações técnicas

- Servidor escuta em `0.0.0.0:6666`, atende uma conexão por vez e volta a aguardar nova conexão quando a anterior termina.
- Mensagens inválidas são descartadas. As estatísticas são calculadas no **SQLite**, e não apenas em memória.
- A data/hora usa `CURRENT_TIMESTAMP` (UTC); quando ainda não há registros recentes, a saída informa ausência de leituras.
- `teste_sem_placa.py` pode ser executado em um segundo terminal, com `servidor.py` rodando, para isolar e verificar o servidor antes de usar Wi-Fi.
- Não publicar SSID/senha no ZIP; restaure placeholders antes de compactar, se tiver preenchido credenciais pessoais.
