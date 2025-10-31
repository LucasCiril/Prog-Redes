from questao1 import find_nonce
import csv

entrada = [
    "Esse é fácil",
    "Texto maior muda o tempo?",
    "É possível calcular esse?"
]

entrada_bits = {
    "Esse é fácil":[8,10,15],
    "Texto maior muda o tempo?":[8,10,15],
    "É possível calcular esse?":[18,19,20]
}

with open("resultado.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Texto", "Bits em zero", "Nonce", "Tempo (s)"])

    for texto in entrada:
        for bits in entrada_bits[texto]:
            data = texto.encode("utf-8")
            nonce, tempo = find_nonce(data, bits)
            writer.writerow([texto, bits, nonce, f"{tempo:.4f}"])