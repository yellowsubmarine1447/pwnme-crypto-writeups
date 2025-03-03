If I'm going to be honest, I don't think this challenge was too great (similarly to my_zed) (though at least it wasn't a straight call of the decrypt function haha).

We're given a website that can:
- encrypt the flag and return it
- encrypt our custom input
- ... that's it

What I described above may not make much sense, especially if you've seen the website and the additional *decrypt* functionality. The reason why I excluded decryption is because decryption is useless.

Basically, we can replicate decryption on our own. The website encrypts the flag with an unknown password, and we are only able to leverage this unknown password by encrypting our own input - the decryption functionality doesn't allow this. It's possible to provide our own password to encrypt/decrypt, but since we can see the source code this is basically useless as we can encrypt/decrypt on the server-side ourselves.

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
Specifically, note that AES CFB is used on the last in our plaintext, and the rest is encrypted with AES CBC. Both AES-CFB and AES-CBC perform AES encryption on 16-byte blocks of input, but do some in-between XORing, and in different orders (let `prev` be the previous ciphertext block, and the IV if we're on the first block):
- AES-CFB calculates $\mathrm{enc}(\mathrm{prev})\oplus \mathrm{chunk}$
- AES-CBC calculates $\mathrm{enc(prev\oplus \mathrm{chunk})}$

Since our flag is $\le$ 16 bytes (how convenient!!!), the encrypted flag will just be $\mathrm{enc}(iv)\oplus\mathrm{flag}$. Thus, if we XOR all of this with $\mathrm{enc}(\mathrm{iv})$, we will get the flag.

We obtain this value by CBC-encrypting the IV we obtain from the JSON body after getting the encrypted flag with an IV of 16 NULL bytes on the server ($0\oplus \mathrm{iv} = \mathrm{iv}$). To force CBC-encryption, we can add 16 more dummy bytes into our input and get the first 16 bytes of the returned ciphertext.