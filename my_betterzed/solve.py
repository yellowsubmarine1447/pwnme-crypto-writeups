from requests import get, post
from json import loads, dumps
import zlib
import io

server = "https://mybetterzed-0f026d746b013d85.deploy.phreaks.fr" # replace with actual instance url

def split_g(request_response):
    return loads(request_response[4:request_response.index(b"}")+1]), zlib.decompress(request_response[304:])

def p(j, to_enc, username="", password="", iv=""):
    first = b"OZED" + dumps(j).encode()
    padding = b"\x00" * (304 - len(first))
    return split_g(post(f"{server}/encrypt/", {"username": username, "password": password, "iv": iv},files={"file": io.BytesIO(to_enc)}).content)

def get_enc_flag():
    return split_g(get(f"{server}/encrypt_flag/").content)

base_json, enc_flag = get_enc_flag()
iv = bytes.fromhex(base_json["iv"])
base_json["iv"] = "0" * 32

_, enc_iv = p(base_json, iv + b"\x00" * 16, iv=b"0" * 32) # some redundant data at the end
print(bytes(enc_iv[i] ^ enc_flag[i] for i in range(min(len(enc_flag), len(enc_iv)))))