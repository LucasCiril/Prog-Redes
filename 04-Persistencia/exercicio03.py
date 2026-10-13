#📝 Exercício 3 — Gerenciador de figurinhas
#Crie um programa para gerenciar uma coleção de figurinhas. Cada figurinha deverá possuir:

#{
#    "codigo": 1,
#    "nome": "Jogador",
#   "nacionalidade": "Brasil",
#    "posicao": "Atacante"
#}
#Utilize uma lista de dicionários e salve os dados no arquivo figurinhas.json.

#O menu deverá possuir:

#1 - Adicionar figurinha
#2 - Listar figurinhas
#3 - Buscar figurinha por código
#4 - Excluir figurinha
#0 - Sair

import json

try:
    with open('figurinhas.json', 'r', encoding='utf-8') as arquivo:
        figurinhas = json.load(arquivo)

except FileNotFoundError:
    figurinhas = []

def cadastrar_figurinha():
    while True:
        cod = int(input('Código: '))
        existe = False

        for i in figurinhas:
            if cod == i.get('codigo'):
                existe = True
                break

        if existe:
            print('Já existe uma figurinha com esse código!')
        else:
            break
                              
    nome = str(input('Nome: '))
    nacionalidade = str(input('Nacionalidade: '))
    posicao = str(input('Posição: '))

    nova_figu = {
        'codigo': cod,
        'nome': nome,
        'nacionalidade': nacionalidade,
        'posicao': posicao
    }

    figurinhas.append(nova_figu)

    with open('figurinhas.json', 'w', encoding='utf-8') as arquivo:
        json.dump(figurinhas, arquivo, indent=4, ensure_ascii=False)

def listar_figu():
    if not figurinhas:
        print('\nNenhuma figurinha cadastrada!')
        print()
        return

    for linha in figurinhas:
        print(linha.get('codigo', 'Não encontrado'))
        print(linha.get('nome', 'Não encontrado'))
        print(linha.get('nacionalidade', 'Não encontrado'))
        print(linha.get('posicao', 'Não encontrado'))
        print()

def buscar_codigo():
    buscador = int(input('Informe o número da figurinha: '))
    limit = False

    for i in figurinhas:
        if buscador == i.get('codigo'):
            print(i.get('nome', 'Não encontrado'))
            print(i.get('nacionalidade', 'Não encontrado'))
            print(i.get('posicao', 'Não encontrado'))

            limit = True
            break
    if not limit:
        print('\nNão existe figurinha com esse código!')

def excluir_figurinha():
    buscador = int(input('Informe o código para excluir a figurinha: '))

    for i in figurinhas:
        if buscador == i.get('codigo'):
            figurinhas.remove(i)

            with open('figurinhas.json', 'w', encoding='utf-8') as arquivo:
                json.dump(figurinhas, arquivo, indent=4, ensure_ascii=False)

            print('\nFigurinha excluída com sucesso!')
            return
    print('\nNão existe figurinha com esse código!')

def menu():
    return """
===============
FIGURINHAS
===============
1- ADICIONAR FIGURINHAS
2- LISTAR FIGURINHAS
3- BUSCAR FIGURINHAS POR CÓDIGO
4- EXCLUIR FIGURINHA
0- SAIR
"""

while True:
    print(menu())
    escolha = input('>>> ')

    if escolha == '1':
        cadastrar_figurinha()
        print('\nFigurinha cadastrada com sucesso!')
        print()
    elif escolha == '2':
        listar_figu()
        print()

    elif escolha == '3':
        buscar_codigo()
        print()

    elif escolha == '4':
        excluir_figurinha()
        print()

    elif escolha == '0':
        print('Finalizando o programa...')
        break