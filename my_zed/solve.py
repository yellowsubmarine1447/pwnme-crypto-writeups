from openzedlib import openzed_patched as openzed
import os
import zlib



file = openzed.Openzed(b'zed', os.urandom(16), 'flag.txt', 16)
file.secure_container = open("flag.txt.ozed", "rb").read()
metadata = file.read_metadata()
file.user = metadata["user"].encode()
file.password_hash = metadata["password_hash"]
file.filename = metadata["filename"]
file.size = metadata["size"]
file.metadata = metadata

print(file.decrypt_container(file.secure_container)["data"].decode())