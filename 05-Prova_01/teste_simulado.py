"""Teste de integração SEM VL53L0X: valores de distância SIMULADOS.
Execute na BitDogLab com MicroPython; não substitui a leitura real exigida.
"""
import network
import socket
import time

WIFI_SSID = 'NOME_DO_WIFI'
WIFI_SENHA = 'SENHA_DO_WIFI'
IP_SERVIDOR = '192.168.1.100'  # trocar pelo IPv4 do PC
PORTA = 6666
DISPOSITIVO = 'BITDOG_SIMULADO'
INTERVALO_SEGUNDOS = 2
DISTANCIAS_SIMULADAS = (157, 160, 154, 170, 145)

wifi = network.WLAN(network.STA_IF)
wifi.active(True)


def conectar_wifi():
    if wifi.isconnected():
        return
    print('Conectando ao Wi-Fi...')
    wifi.connect(WIFI_SSID, WIFI_SENHA)
    inicio = time.ticks_ms()
    while not wifi.isconnected():
        if time.ticks_diff(time.ticks_ms(), inicio) >= 15000:
            raise OSError('Timeout Wi-Fi; confira rede/senha')
        time.sleep_ms(500)
    print('Wi-Fi conectado, IP:', wifi.ifconfig()[0])

indice = 0
while True:
    cliente = None
    try:
        conectar_wifi()
        cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente.settimeout(8)
        cliente.connect((IP_SERVIDOR, PORTA))
        print('Conectado ao servidor. MODO SIMULADO (sem sensor).')
        while wifi.isconnected():
            distancia = DISTANCIAS_SIMULADAS[indice % len(DISTANCIAS_SIMULADAS)]
            indice += 1
            mensagem = '{};{}\n'.format(DISPOSITIVO, distancia)
            cliente.sendall(mensagem.encode())
            print('SIMULADO enviado:', mensagem.strip())
            time.sleep(INTERVALO_SEGUNDOS)
        raise OSError('Wi-Fi desconectado')
    except OSError as erro:
        print('Falha, nova tentativa em 5s:', erro)
        time.sleep(5)
    finally:
        if cliente is not None:
            try:
                cliente.close()
            except OSError:
                pass
