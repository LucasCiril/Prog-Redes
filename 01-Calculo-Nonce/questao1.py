import hashlib
import time

def find_nonce(data_to_hash, bits_to_be_zero):
    tempo = time.time()
    nonce = 0
    while True:

        nonce_to_bytes = nonce.to_bytes(4 , 'big')
        agroup = nonce_to_bytes + data_to_hash
        resulted = hashlib.sha256(agroup).digest()
        hash_int = int.from_bytes(resulted, 'big')
        hash_bin = bin(hash_int)[2:].zfill(256)

        if hash_bin.startswith('0' * bits_to_be_zero):
            finish = time.time() - tempo
            return hash_bin, finish
        nonce += 1