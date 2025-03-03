from Crypto.Util.number import long_to_bytes
from Crypto.Util.Padding import unpad
from Crypto.Cipher import AES
from hashlib import sha256


with open("output.txt") as f:
    p = int(f.readline().strip().split("= ")[1])
    f.readline()
    ciphertext = long_to_bytes(int(f.readline().strip().split("= ")[1], 16))

C = p-1

key = long_to_bytes(C)
key = sha256(key).digest()[:16]

cipher = AES.new(key, AES.MODE_ECB)
print(unpad(cipher.decrypt(ciphertext), AES.block_size).decode())