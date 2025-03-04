We have a server that generates ECDSA signatures (Elliptic Curve signing algorithm) for messages of a fixed format ("this is my lovely loved distributed item " + some number that gradually increases):
```py
self.signatures.append((m.hex(), r, s))
```

We must recover the private key that's used to sign these messages.

There's a few catches here: firstly, while the steps of signing in the ECDSA algorithm are kept relatively the same, one in particular is not: instead of randomly generating a $256$-bit integer for the nonce $k$ (which is what you're supposed to do), a whacko algorithm is used:
```py
a = int(alea_1)
b = int(alea_2)
assert a**2 < b**2 < 2**120 - 1
c = (hash(a) - hash(b)) * int.from_bytes(urandom(32), "big") ^ 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
randomized_main_part_l = 249
randomized_part = ""
for _ in range(256 - randomized_main_part_l):
    randomized_part += choice(bin(c).split("0b")[1])
parity = int(randomized_part, 2) % 2
randomized_part = bin(self.salt ^ int(randomized_part, 2))[-(256 - randomized_main_part_l):]
k = 0xFF000000000000000000000000000000000000000000000000000000000000FF ^ int(randomized_part + bin(secrets.randbits(randomized_main_part_l)).split("0b")[1].zfill(randomized_main_part_l) if parity else bin(secrets.randbits(randomized_main_part_l)) + randomized_part, 2)
```

It's highly obfuscated, but we can notice quickly that if we can get `hash(a) = hash(b)`, where `a` and `b` are integers we provide, the subtraction on the fourth line will become 0, which will propagate down and severely reduce the randomness of future values. Note `hash` is a Python function, and setting `a = -1, b = -2` will cause `hash(a) - hash(b)`, and thus `c`, to become 0 while still passing the assert statement on line 3.

`c` being 0 is very useful as we see a lot of stuff fall through. `randomized_part` will originally be `0` (before it's XOR with the salt), which means after it's interaction with the salt, `randomized_part = bin(self.salt)[-(256 - randomized_main_part_l)]`, which is will get the last $7$ binary digits of the salt. `parity` will always be equal to `1`, emaning the ternary condition for calculating `k` will boil down to (notice the `+` operates on two strings, essentially concatenating the bits together):
```py
k = 0xFF000000000000000000000000000000000000000000000000000000000000FF ^ int(salt_7_bits + random_249_bits, 2)
```

Every time the server is connected to, the salt is generated and fixed every time we generate a new signature. This means the nonce of every signature we generate, with `a = -1, b = -2`, will *always have its top 7 bits be the same* (though this value is unknown). This hints at the biased nonce attack, which aims to exploit the reduced entropy from an insecure nonce.

In this case, we can use lattices and the LLL algorithm to generate a lot of signatures (from testing, 70 was sufficient, though it takes a long time to run due to the forced 90 second time limit for every 10 signatures generated) and calculate the difference between two nonces. Some more algebra can be performed to calculate one of the nonces themselves, and finally we can retrieve the private key as we know all but one variable in the second last line of the `gen_sign` function. I won't delve into the math and lattice calculations as this the shared-MSB biased nonce attack is pretty well-known. The lattice construction is described [here](https://blog.trailofbits.com/2020/06/11/ecdsa-handle-with-care/). As for an explanation of lattice cryptanalysis, you can look [here](https://eprint.iacr.org/2023/032.pdf) (note that the specific setup of biased nonce attacks, and especially the shared MSB, is also talked about in this paper under "ECDSA with Biased Nonces").

There's one final hurdle we have to clear: creating signatures. You see, every time we create 10 signatures, our "credits" reduce by one (we only start with one). To get more credits, we need to provide signatures ourselves that aren't exactly one of the signatures provided by the program (under the modulus of `n`). We don't know the private key, so this seems impossible to do. However, while it's not possible to generate signatures ourselves, we can tweak signatures provided by the program slightly to get new, valid signatures: given a signature tuple $(m, r, s)$, it turns out $(m, r, -s)$ is also a valid signature.

The reason for this is that the signature verification argument generates a point $(x, y)$ by calculating $(zs^{-1} \bmod n)\times G + (rs^{-1}\bmod n)\times Q_A$ under the FRP256v1 elliptic curve, where $G$ is the generator point and $Q_A$ is the public key (note that it's possible to recover the public key even though we're not given it, but this is not relevant to our challenge), and then checks if $x = r$. If we have $-s$ as our signature instead, then we can take the negative sign out of both bracketed expressions and obtain
```math
(z(-s)^{-1}\bmod n) \times G + (r(-s)^{-1}\bmod n)\times Q_A = -((zs^{-1} \bmod n)\times G + (rs^{-1}\bmod n)\times Q_A) = (x,-y)$
```
under our elliptic curve, since taking the negative of a point on an elliptic curve flips only the $y$-coordinate. Since $x = r$ is the same in both calculations, our signature will pass. Thus, by generating new signatures $(m, r, s)$, constructing a lattice of them while simultaneously returning tweaked signatures $(m, r, -s)$ to get more signatures, and then performing lattice reduction, we can obtain the ECDSA private key and decrypt the flag.