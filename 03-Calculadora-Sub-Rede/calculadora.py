import sys

#Pega o IP e o traduz para bytes:
def traducao(x):   
    ipbin = [int(z) for z in x.split('.')]
    ipbin = bytes(ipbin)
    ipbin = int.from_bytes(ipbin)
    return ipbin

#Pega os bits do host e devolve em uma variável:
def net(y):
    bitsHost = 32 - y
    return bitsHost

#Pega a máscara em notação CIDR, transforma-a em bits e em decimal, traz de volta "humanamente":
def cidr_to_mask(z):
    mask_int = (2**z -1) << (32-z)
    mask_bin = f'{mask_int:032b}'

    octetos_bin = [mask_bin[i:i+8] for i in range(0,32,8)]
    octeto_dec = [str(int(o , 2))for o in octetos_bin]

    return {
        'binario' : '.'.join(octetos_bin),
        'decimal' : '.'.join(octeto_dec)
    }
#Apenas para transformar tudo em "humano":
def brd_and_ip(l):
    mask_bin = f'{l:032b}'
    octetos_bin = [mask_bin[i:i+8] for i in range(0,32,8)]
    octeto_dec = [(int(o , 2))for o in octetos_bin]

    return {
        'binario' : '.'.join(octetos_bin),
        'decimal' : '.'.join(str(n) for n in octeto_dec)
        }

def verify(p):
    ipbin = p.split('.')
    if len(ipbin) != 4:
        print('IP inválido! Informe um que contenha 4 Octetos!')
        sys.exit()
    for part in ipbin:
        if not part.isdigit():
            print('Octetos contém letras! Inválido!')
            sys.exit()
        call= int(part)
        if call < 0 or call > 255:
            print('Octetos com números fora do range correto!')
            sys.exit()  

#Programa principal:
print('Bem vindo à Calculadora de Sub-Redes.')
ip1 = str(input ("Digite o endereço IP: ")).strip()
verify(ip1)
entrada = str(input ("Digite o tamanho da máscara de rede em CIDR: ")).strip()

#Tratamento da Camada 8:
if entrada[0] == '/':
    entrada = entrada[1:]
    mask = int(entrada)
else:
    mask = int(entrada)

a = traducao(ip1)  
b = net(mask)
c = cidr_to_mask(mask)

rede1 = a >> b << b
broadcast1 = a | ((1 << net(mask)) -1)
roteador = rede1 | (1 << 0)

d = brd_and_ip(roteador)
e = brd_and_ip(rede1)
f = brd_and_ip(broadcast1)

print(f'IP informado: {ip1}\n')
print(f'Endereço de rede: {e['decimal']}')
print(f'Endereço de rede (em bits): {e['binario']}\n')
print(f'Endereço de Broadcast: {f['decimal']}')
print(f'Endereço de Broadcast (em bits): {f['binario']}\n')
print(f'Endereço do Roteador: {d['decimal']}')
print(f'Endereço do Roteador (em bits): {d['binario']}\n')
print(f'Máscara de rede : {c['decimal']}')
print(f'Máscara de rede em binário: {c['binario']}')