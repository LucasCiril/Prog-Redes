# 📝 Exercício 1 — Arquivo de nomes
# Crie um programa que solicite cinco nomes, armazene-os em uma lista e 
# salve cada nome em uma linha do arquivo nomes.txt. 
# Depois, abra o arquivo novamente e mostre os nomes na tela.

nomes = []

for i in range(5):
    nomes.append(str(input('Nomes: ')))

with open('nomes.txt', 'w') as arquivo:
    for c in nomes:
        arquivo.write(f'{c} ')


with open('nomes.txt', 'r') as arquivo:
    for linha in arquivo:
        print(linha.strip())