"""Teste facultativo do servidor sem BitDogLab: execute em outro terminal."""
import socket
import time

with socket.create_connection(('127.0.0.1', 6666), timeout=5) as s:
    for n in (157, 160, 154):
        s.sendall(f'BITDOG_TESTE;{n}\n'.encode())
        print('Enviado:', n)
        time.sleep(1)
