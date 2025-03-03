import hashlib
from challenge import CustomSHA
from pwn import *

# """ # uncomment this when sending to server multiple times, similarly below
def hash_block(chunk, h):
    return hashlib.sha256(chunk + h).digest()[:5]

def preprocess(bruh) -> bytes:
    data = bruh
    data = bytearray(data)

    data.append(0x80)
    while len(data) % 8 != 0:
        data.append(0x00)

    data += struct.pack('>Q', 8 * len(bruh))

    return bytes(data)

with open("Hack.zip", "rb") as f:
    buffer = f.read()

def get_block(i):
    return buffer[i*8:i*8+8]

s = {}

dummy = b"0" * 8
h0 = 0x674523EFCD.to_bytes(5, byteorder='big')
h = h0

for i in range(0, len(buffer) // 8): # ignore annoying leftover after last full block
    h = hash_block(get_block(i), h)
    s[h] = i

k = 0
while (k + 2 ** k - 1 < len(buffer) // 8):
    k += 1

print(f"We will create {k} choices")
block_choices = []
h = h0
for i in range(k):
    print(f"Generating expandable block of size {2**i + 1 = }...")
    A = {}
    for j in range(2**20):
        block = j.to_bytes(8, "big")
        A[hash_block(block, h)] = block
    htmp = h
    for _ in range(2**i):
        htmp = hash_block(dummy, htmp)
    j = 0
    new_block = j.to_bytes(8, "big")
    hashnew = hash_block(new_block, htmp)
    while hashnew not in A:
        j += 1
        new_block = j.to_bytes(8, "big")
        hashnew = hash_block(new_block, htmp)

    block = A[hashnew]
    print(f"Done! Collision with {block} and {new_block}")
    second_block = []
    for _ in range(2**i):
        second_block.append(dummy)
    second_block.append(new_block)
    second_block = b"".join(second_block)
    assert len(second_block) == 8 * (2**i+1)
    assert CustomSHA(block).sha_custom(h) == CustomSHA(second_block).sha_custom(h)
    block_choices.append((block, second_block))
    h = hashnew

i = 0
block_coll = i.to_bytes(8, "big")
hnew = hash_block(block_coll, h)

# our block cannot be on any index k-1 or lower since those are reserved for our k extendable blocks -> block sits thus at least on k, which we can accomodate
while hnew not in s or s[hnew] < k:
    i += 1
    block_coll = i.to_bytes(8, "big")
    hnew = hash_block(block_coll, h)

newstream = []
diff = s[hnew] - k
b = 0
mult = 1
for i in range(k):
    if diff % 2:
        diff -= 1
        b += mult
        newstream.append(block_choices[i][1])
    else:
        newstream.append(block_choices[i][0])
    mult *= 2
    diff //= 2

newstream.append(block_coll)
newstream.append(buffer[8 * s[hnew] + 8:])

with open("Hack_collide.zip", "wb") as g:
    g.write(b"".join(newstream))


# """ # uncomment this when sending to server repeatedly, similarly above

assert open("Hack.zip", "rb").read() != open("Hack_collide.zip", "rb").read()
assert CustomSHA(open("Hack.zip", "rb").read()).sha_custom(h0) == CustomSHA(open("Hack_collide.zip", "rb").read()).sha_custom(h0)
print("Wooo we've got a collision!")

answer_hex = open("Hack_collide.zip", "rb").read().hex() # now send to server, might have to do multiple times cause their server is unstable idk why. i've looped below

# nah im just gonna cat this into a netcat connection idgaf
with open("answer.json", "w") as f:
    f.write(f"{{\"action\": \"hash\", \"data\": \"{answer_hex}\"}}")
host = "mirrorhash-76376bce2ef13159.deploy.phreaks.fr" # replace with actual host, obv
while True:
    try:
        p = remote(host, 443, ssl=True, sni=host)
        break
    except Exception as e:
        print(e)
        continue

p.sendlineafter(b"map hash", f"{{\"action\": \"hash\", \"data\": \"{answer_hex}\"}}")
p.interactive()