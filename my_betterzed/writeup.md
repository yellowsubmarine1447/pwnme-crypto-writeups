If I'm going to be honest, I don't think this challenge was too great (similarly to my_zed) (though at least it wasn't a straight call of the decrypt function haha).

We're given a website that can:
- encrypt the flag and return it
- encrypt our custom input
- ... that's it

What I described above may not make much sense, especially if you've seen the website and the additional *decrypt* functionality. The reason why I excluded decryption is because decryption is useless.

The reason why the website is so useful is because the flag can only be encrypted with some unknown password. Fortunately, we can encrypt whatever we want with this unknown password, but we can't decrypt whatever we want with the unknown password. Although there is a feature to encrypt/decrypt with some custom password we provide, we can replicate this functionality locally anyway.

Decrypting the flag with only an encryption oracle seems impossible, until you read the `encrypt` function carefully:
```py
for pos in range(0, len(plaintext), 16):
    chunk = plaintext[pos:pos+16]

    # AES CFB for the last block or if there is only one block
    if len(plaintext[pos+16:pos+32]) == 0 :
        #if plaintext length <= 16, iv = self.iv
        if len(plaintext) <= 16 :
            prev=iv
        # else, iv = previous ciphertext
        else:
            prev=ciphertext[pos-16:pos]
            
        prev = ecb_cipher.encrypt(prev)
        ciphertext += xor(chunk, prev)

    # AES CBC for the n-1 firsts block
    elif not ciphertext:
        xored = bytes(xor(plaintext, iv))
        ciphertext += ecb_cipher.encrypt(xored)
        
    else:
        xored = bytes(xor(chunk, ciphertext[pos-16:pos]))
        ciphertext += ecb_cipher.encrypt(xored)
```
Specifically, note that AES CFB is used on the last $16$-byte chunk in our plaintext, and the rest is encrypted with AES-CBC. Both AES-CFB and AES-CBC perform AES encryption on 16-byte blocks of input, but do some in-between XORing, and in different orders (let `prev` be the IV if we're on the first block, and the previous ciphertext block otherwise):
- AES-CFB calculates $\mathrm{enc}(\mathrm{prev})\oplus \mathrm{chunk}$
- AES-CBC calculates $\mathrm{enc(prev\oplus \mathrm{chunk})}$

Since our flag is $\le$ 16 bytes (how convenient!!!), the encrypted flag will just be $\mathrm{enc}(\mathrm{iv})\oplus\mathrm{flag}$. Thus, if we XOR this encrypted flag with $\mathrm{enc}(\mathrm{iv})$, we will get the flag.

We can CBC-encrypt the IV (and thus basically ECB encrypt since the IV is exactly $16$ bytes) we obtain from the JSON body after getting the encrypted flag with an IV of 16 NULL bytes on the server ($0\oplus \mathrm{iv} = \mathrm{iv}$). To force CBC-encryption, we should add 16 more dummy bytes into our input and get the first 16 bytes of the returned ciphertext (which will correspond to the ECB-encrypted IV), and finally XOR it with our encrypted flag.