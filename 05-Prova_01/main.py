import network
import socket
import time
from machine import I2C, Pin
from vl53l0x import VL53L0X

WIFI_SSID = 'NOME_DO_WIFI'
WIFI_SENHA = 'SENHA_DO_WIFI'
IP_SERVIDOR = '192.168.1.100'  # ALTERAR para o IPv4 do computador
PORTA = 6666
DISPOSITIVO = 'BITDOG01'
INTERVALO_SEGUNDOS = 2

# Barramento I2C0 da BitDogLab com SDA=GP0 e SCL=GP1.
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)
print('Endereços I2C encontrados:', [hex(x) for x in i2c.scan()])
if 0x29 not in i2c.scan():
    raise RuntimeError('VL53L0X não detectado no I2C0. Verifique os fios.')
sensor = VL53L0X(i2c, io_timeout_ms=1500)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)


def conectar_wifi():
    if wlan.isconnected():
        return
    print('Conectando ao Wi-Fi...')
    wlan.connect(WIFI_SSID, WIFI_SENHA)
    inicio = time.ticks_ms()
    while not wlan.isconnected():
        if time.ticks_diff(time.ticks_ms(), inicio) > 15000:
            raise OSError('Tempo limite da conexão Wi-Fi')
        time.sleep_ms(500)
    print('Wi-Fi conectado. IP:', wlan.ifconfig()[0])


while True:
    conexao = None
    try:
        conectar_wifi()
        conexao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conexao.settimeout(5)
        conexao.connect((IP_SERVIDOR, PORTA))
        print('Conectado ao servidor.')
        while True:
            if not wlan.isconnected():
                raise OSError('Wi-Fi desconectado')
            distancia = int(sensor.range)
            # Alguns drivers retornam 65535 em leitura sem alcance confiável.
            if 0 < distancia < 65535:
                mensagem = '{};{}\n'.format(DISPOSITIVO, distancia)
                conexao.sendall(mensagem.encode('utf-8'))
                print('Enviado:', mensagem.strip())
            else:
                print('Leitura fora de alcance:', distancia)
            time.sleep(INTERVALO_SEGUNDOS)
    except (OSError, RuntimeError) as erro:
        print('Falha de conexão/leitura:', erro)
        time.sleep(3)
    finally:
        if conexao is not None:
            try:
                conexao.close()
            except OSError:
                pass
