from Crypto.Cipher import AES
from hashlib import sha256


def decrypt(m: str, secret_key: int) -> str:
    hash_secret_key = sha256(str(secret_key).encode()).digest()
    cipher = AES.new(hash_secret_key, AES.MODE_ECB)
    return cipher.decrypt(bytes.fromhex(m))

with open("output.txt") as f:
    n, g, k, A, B = [int(f.readline().strip().split("= ")[1]) for _ in range(5)]
    enc = f.readline().strip().split("= ")[1][1:-1] # remove quotes

a = (((A - 1) * pow(k,-1,n)) % (n*n)) // n
gab = (a*(B-1) + 1) % (n*n)
print(decrypt(enc, gab))