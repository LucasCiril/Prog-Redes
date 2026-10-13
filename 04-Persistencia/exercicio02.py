# 📝 Exercício 2 — Cadastro de alunos
# Crie um programa que mantenha uma lista de alunos. 
# Cada aluno deverá possuir nome, idade e curso. 
# Os dados deverão ser salvos em alunos.json.

# O programa deverá possuir:
# 1 - Cadastrar aluno
# 2 - Listar alunos
# 0 - Sair
# Os alunos cadastrados devem continuar existindo mesmo depois 
# que o programa for encerrado.

import json

#==============================
# INÍCIO DO PROGRAMA
#==============================
try:
    with open('alunos.json', 'r', encoding='utf-8') as arquivo:
        alunos = json.load(arquivo)

except FileNotFoundError:
    alunos = []

#=============================
# CADASTRO DE NOVOS ALUNOS
#=============================
def cadastrar_aluno():
    nome = (input('Nome: '))
    idade = int(input('Idade: '))
    curso = (input('Curso: '))

    novo_aluno = {
        'nome': nome,
        'idade': idade,
        'curso': curso
    }

    alunos.append(novo_aluno)

    # Salva a lista atualizada no arquivo
    with open('alunos.json', 'w', encoding='utf-8') as arquivo:
        json.dump(alunos, arquivo, indent = 4 ,ensure_ascii = False)

#==============================
# LISTAGEM DOS ALUNOS
#==============================

def mostra_aluno():
    if not alunos:
        print('Nenhum aluno cadastrado!')
        print()
        return

    for aluno in alunos:
        print(aluno.get('nome', 'Não encontrado'))
        print(aluno.get('idade', 'Não encontrado'))
        print(aluno.get('curso', 'Não encontrado'))
        print()

#==============================
# MENU PRINCIPAL
#==============================

def menu():  
    return """
=========================
      BEM VINDO!
=========================
1- CADASTRAR NOVO ALUNO
2- LISTAR ALUNOS
0- SAIR
"""

#========================
# PROGRAMA PRINCIPAL
#========================

while True:
    print(menu())
    escolha = (input('\nEscolha uma opção: '))

    if escolha == '1':
        cadastrar_aluno()
        print()
        print('Aluno cadastrado com sucesso!')

    elif escolha == '2':
        mostra_aluno()

    elif escolha == '0':
        print('Finalizando o programa...')
        break

    else:
        print('Opção inválida!')