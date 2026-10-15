import socket
import sqlite3
from pathlib import Path

HOST = '0.0.0.0'
PORTA = 6666
BANCO = Path(__file__).with_name('leituras.db')


def criar_banco():
    with sqlite3.connect(BANCO) as db:
        db.execute('''CREATE TABLE IF NOT EXISTS leituras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dispositivo TEXT NOT NULL,
            distancia_mm INTEGER NOT NULL,
            instante DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')


def registrar(dispositivo, distancia):
    with sqlite3.connect(BANCO) as db:
        db.execute('INSERT INTO leituras (dispositivo, distancia_mm) VALUES (?, ?)',
                   (dispositivo, distancia))


def estatisticas():
    with sqlite3.connect(BANCO) as db:
        media5 = db.execute("SELECT AVG(distancia_mm) FROM leituras WHERE instante >= datetime('now', '-5 minutes')").fetchone()[0]
        media60 = db.execute("SELECT AVG(distancia_mm) FROM leituras WHERE instante >= datetime('now', '-1 hour')").fetchone()[0]
    return media5, media60


def mostrar_media(valor):
    return f'{valor:.1f} mm' if valor is not None else 'Sem leituras no período'


def processar_linha(linha):
    partes = linha.strip().split(';')
    if len(partes) != 2:
        print('Mensagem inválida (formato):', repr(linha))
        return
    dispositivo, texto_distancia = partes
    if not dispositivo or len(dispositivo) > 32 or not all(c.isalnum() or c in '_-' for c in dispositivo):
        print('Identificador inválido:', repr(dispositivo))
        return
    try:
        distancia = int(texto_distancia)
    except ValueError:
        print('Distância inválida:', repr(texto_distancia))
        return
    if not 0 <= distancia <= 65535:
        print('Distância fora do intervalo:', distancia)
        return
    registrar(dispositivo, distancia)
    media5, media60 = estatisticas()
    print(f'{dispositivo} -> {distancia} mm')
    print('Média - últimos 5 minutos:', mostrar_media(media5))
    print('Média - última 1 hora:', mostrar_media(media60))
    print('-' * 45)


def executar():
    criar_banco()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((HOST, PORTA))
        servidor.listen(5)
        print(f'Servidor escutando em {HOST}:{PORTA}')
        while True:
            cliente, endereco = servidor.accept()
            print('Cliente conectado:', endereco[0])
            with cliente:
                cliente.settimeout(30)
                buffer = b''
                try:
                    while True:
                        pedaco = cliente.recv(1024)
                        if not pedaco:
                            break
                        buffer += pedaco
                        while b'\n' in buffer:
                            linha, buffer = buffer.split(b'\n', 1)
                            try:
                                processar_linha(linha.decode('utf-8'))
                            except UnicodeError:
                                print('Mensagem com codificação inválida')
                        if len(buffer) > 2048:
                            print('Mensagem excessivamente longa; cliente desconectado')
                            break
                except (ConnectionError, OSError) as exc:
                    print('Conexão encerrada:', exc)
            print('Cliente desconectado:', endereco[0])


if __name__ == '__main__':
    try:
        executar()
    except KeyboardInterrupt:
        print('\nServidor finalizado.')
