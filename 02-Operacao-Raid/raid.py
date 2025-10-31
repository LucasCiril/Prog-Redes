import os
import sys
from typing import List, Optional


def xor_bytes(a: bytes, b: bytes) -> bytes:
    la = len(a)
    lb = len(b)
    L = max(la, lb)
    A = a.ljust(L, b"\x00")
    B = b.ljust(L, b"\x00")
    return bytes(x ^ y for x, y in zip(A, B))


class RAID4:
    def __init__(self, base_dir: str, num_disks: int, disk_size: int, block_size: int):
        if num_disks < 2:
            raise ValueError("É necessário pelo menos 2 discos (1 dado + 1 paridade)")
        self.base_dir = base_dir
        self.num_disks = num_disks
        self.disk_size = disk_size
        self.block_size = block_size
        self.parity_idx = num_disks - 1
        self.data_disks = list(range(0, self.parity_idx))

    def disk_path(self, idx: int) -> str:
        return os.path.join(self.base_dir, f"disco{idx}.bin")

    def logical_size(self) -> int:
        return (self.num_disks - 1) * self.disk_size

    def ensure_dir(self):
        os.makedirs(self.base_dir, exist_ok=True)

    def create_empty_disk_file(self, idx: int):
        path = self.disk_path(idx)
        with open(path, "wb") as f:
            f.write(b"\x00" * self.disk_size)

    def disk_exists(self, idx: int) -> bool:
        return os.path.exists(self.disk_path(idx))

    def read_disk_block(self, idx: int, block_no: int) -> bytes:
        """Read block (block_size bytes) from disk idx at block_no (0-based).
        If file missing, returns zeros. If beyond disk_size, returns zeros for missing part.
        """
        path = self.disk_path(idx)
        offset = block_no * self.block_size
        if not os.path.exists(path):
            # missing disk treated as zeros
            return b"\x00" * self.block_size
        with open(path, "rb") as f:
            f.seek(offset)
            data = f.read(self.block_size)
            if len(data) < self.block_size:
                data += b"\x00" * (self.block_size - len(data))
            return data

    def write_disk_block(self, idx: int, block_no: int, data: bytes):
        """Write exactly block_size bytes to disk idx at block_no. If disk file missing, raise.
        """
        path = self.disk_path(idx)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Disco {idx} ausente: {path}")
        if len(data) != self.block_size:
            raise ValueError("data length must equal block_size")
        offset = block_no * self.block_size
        with open(path, "r+b") as f:
            f.seek(offset)
            f.write(data)

    def compute_parity_block_for_stripe(self, stripe_no: int) -> bytes:
        # parity = XOR over data disks' block for this stripe
        acc = b"\x00" * self.block_size
        for d in self.data_disks:
            blk = self.read_disk_block(d, stripe_no)
            acc = xor_bytes(acc, blk)
        return acc

    def initialize(self):
        self.ensure_dir()
        # create data disks zeroed
        for d in range(self.num_disks):
            self.create_empty_disk_file(d)
        # compute parity (all zeros => zeros)
        for stripe in range(self.disk_size // self.block_size):
            pblk = self.compute_parity_block_for_stripe(stripe)
            # write to parity file
            self.write_disk_block(self.parity_idx, stripe, pblk)
        print("RAID inicializado com sucesso.")

    def open_existing(self):
        # verify files exist
        for d in range(self.num_disks):
            if not self.disk_exists(d):
                raise FileNotFoundError(f"Arquivo do disco{d} nao encontrado em {self.base_dir}")
        print("RAID obtido com sucesso (todos os arquivos existem).")

    def logical_to_physical(self, position: int):
        """Return tuple (disk_idx, block_no, offset_within_block)
        for the logical byte position.
        """
        stripe_unit = self.block_size * (self.num_disks - 1)  # bytes per stripe across data disks
        stripe = position // stripe_unit
        offset_in_stripe = position % stripe_unit
        data_disk_num = offset_in_stripe // self.block_size  # 0..num_data_disks-1
        offset_within_block = offset_in_stripe % self.block_size
        disk_idx = data_disk_num
        block_no = stripe
        return disk_idx, block_no, offset_within_block

    def read(self, position: int, length: int) -> bytes:
        if position < 0 or length < 0 or position + length > self.logical_size():
            raise ValueError("Leitura fora dos limites lógicos do RAID")
        result = bytearray()
        remaining = length
        pos = position
        while remaining > 0:
            disk_idx, block_no, off = self.logical_to_physical(pos)
            take = min(remaining, self.block_size - off)
            # read the whole block from the disk (or reconstruct if missing)
            block = self.read_or_reconstruct_data_block(disk_idx, block_no)
            result.extend(block[off:off + take])
            pos += take
            remaining -= take
        return bytes(result)

    def read_or_reconstruct_data_block(self, disk_idx: int, block_no: int) -> bytes:
        path = self.disk_path(disk_idx)
        if os.path.exists(path):
            return self.read_disk_block(disk_idx, block_no)
        # reconstruct using parity and other data disks
        # data_missing = parity XOR XOR(all other data blocks)
        acc = self.read_disk_block(self.parity_idx, block_no)
        for d in self.data_disks:
            if d == disk_idx:
                continue
            acc = xor_bytes(acc, self.read_disk_block(d, block_no))
        return acc

    def write(self, position: int, data: bytes):
        if position < 0 or position + len(data) > self.logical_size():
            raise ValueError("Escrita fora dos limites lógicos do RAID")
        remaining = len(data)
        pos = position
        idx_data_offset = 0
        while remaining > 0:
            disk_idx, block_no, off = self.logical_to_physical(pos)
            take = min(remaining, self.block_size - off)
            # read old data block (if disk exists else reconstruct)
            old_block = self.read_or_reconstruct_data_block(disk_idx, block_no)
            new_block = bytearray(old_block)
            new_block[off:off + take] = data[idx_data_offset:idx_data_offset + take]
            new_block = bytes(new_block)

            # read old parity
            old_parity = self.read_disk_block(self.parity_idx, block_no)

            # compute new parity = old_parity XOR old_block XOR new_block
            parity_delta = xor_bytes(old_block, new_block)
            new_parity = xor_bytes(old_parity, parity_delta)

            # write new data block if disk is present
            data_path = self.disk_path(disk_idx)
            if os.path.exists(data_path):
                # write full block
                self.write_disk_block(disk_idx, block_no, new_block)
            else:
                # disk missing -> per spec, only parity should be updated so we skip data write
                pass

            # write parity block if parity disk exists
            parity_path = self.disk_path(self.parity_idx)
            if os.path.exists(parity_path):
                self.write_disk_block(self.parity_idx, block_no, new_parity)
            else:
                # parity missing -> cannot update parity now
                pass

            pos += take
            remaining -= take
            idx_data_offset += take

    def remove_disk(self, idx: int):
        path = self.disk_path(idx)
        if os.path.exists(path):
            os.remove(path)
            print(f"disco{idx}.bin removido (simulado defeito).")
        else:
            print(f"disco{idx}.bin nao existe (ja removido).")

    def reconstruct_disk(self, idx: int):
        # create file and fill with reconstructed content
        if idx < 0 or idx >= self.num_disks:
            raise ValueError("Indice de disco invalido")
        path = self.disk_path(idx)
        total_blocks = self.disk_size // self.block_size
        with open(path, "wb") as f:
            # reserve full size with zeros first
            f.write(b"\x00" * self.disk_size)
        # reconstruct block by block
        for blk in range(total_blocks):
            if idx == self.parity_idx:
                # parity = XOR of data disks
                pblk = self.compute_parity_block_for_stripe(blk)
                self.write_disk_block(idx, blk, pblk)
            else:
                # reconstruct data block: parity XOR XOR(other data)
                acc = self.read_disk_block(self.parity_idx, blk)
                for d in self.data_disks:
                    if d == idx:
                        continue
                    acc = xor_bytes(acc, self.read_disk_block(d, blk))
                self.write_disk_block(idx, blk, acc)
        print(f"disco{idx}.bin reconstruido com sucesso.")


def ask_int(prompt: str) -> int:
    while True:
        try:
            v = int(input(prompt))
            return v
        except ValueError:
            print("Valor invalido. Digite um número inteiro.")


def main_menu():
    raid: Optional[RAID4] = None
    while True:
        print("\n=== RAID4 Simulator ===")
        print("1 - inicializaRAID")
        print("2 - obtemRAID")
        print("3 - escreveRAID")
        print("4 - leRAID")
        print("5 - removeDiscoRAID")
        print("6 - constroiDiscoRAID")
        print("0 - sair")
        opt = input("Escolha: ")
        if opt == "1":
            base_dir = input("Pasta onde criar os discos: ")
            num_disks = ask_int("Numero total de discos (dados + paridade): ")
            disk_size = ask_int("Tamanho de cada disco em bytes: ")
            block_size = ask_int("Tamanho do bloco em bytes: ")
            raid = RAID4(base_dir, num_disks, disk_size, block_size)
            raid.initialize()
        elif opt == "2":
            base_dir = input("Pasta onde os discos foram criados: ")
            num_disks = ask_int("Numero total de discos (dados + paridade): ")
            disk_size = ask_int("Tamanho de cada disco em bytes: ")
            block_size = ask_int("Tamanho do bloco em bytes: ")
            raid = RAID4(base_dir, num_disks, disk_size, block_size)
            try:
                raid.open_existing()
            except FileNotFoundError as e:
                print("Erro:", e)
                raid = None
        elif opt == "3":
            if not raid:
                print("RAID nao foi inicializado/obtido. Use inicializaRAID ou obtemRAID primeiro.")
                continue
            pos = ask_int("Posicao inicial logica (0-based): ")
            data_hex = input("Dados a gravar (hex, ex: 0a1b2c) ou texto (prefixe com t:): ")
            if data_hex.startswith("t:"):
                data = data_hex[2:].encode("utf-8")
            else:
                # assume hex
                try:
                    data = bytes.fromhex(data_hex)
                except Exception:
                    print("Formato invalido. Use texto com prefixo 't:' ou hex puro.")
                    continue
            try:
                raid.write(pos, data)
                print("Escrita concluida.")
            except Exception as e:
                print("Erro durante escrita:", e)
        elif opt == "4":
            if not raid:
                print("RAID nao foi inicializado/obtido. Use inicializaRAID ou obtemRAID primeiro.")
                continue
            pos = ask_int("Posicao inicial logica (0-based): ")
            length = ask_int("Quantos bytes ler: ")
            try:
                data = raid.read(pos, length)
                print("Dados lidos (hex):", data.hex())
                try:
                    print("Como texto (utf-8):", data.decode("utf-8"))
                except Exception:
                    pass
            except Exception as e:
                print("Erro durante leitura:", e)
        elif opt == "5":
            if not raid:
                print("RAID nao foi inicializado/obtido. Use inicializaRAID ou obtemRAID primeiro.")
                continue
            idx = ask_int("Indice do disco a remover (0..N-1): ")
            raid.remove_disk(idx)
        elif opt == "6":
            if not raid:
                print("RAID nao foi inicializado/obtido. Use inicializaRAID ou obtemRAID primeiro.")
                continue
            idx = ask_int("Indice do disco a reconstruir (0..N-1): ")
            try:
                raid.reconstruct_disk(idx)
            except Exception as e:
                print("Erro durante reconstrução:", e)
        elif opt == "0":
            print("Saindo...")
            break
        else:
            print("Opcao invalida")


if __name__ == '__main__':
    main_menu()