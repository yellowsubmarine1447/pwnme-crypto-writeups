The program performs Diffie-Hellman with the standard public parameters $g$ and $p$ (the latter of which is a prime), and the private keys $a$ and $b$.

That is, $g^{ab}\bmod p$ is calculated and used as the key to encrypt the flag. However, there's a catch - $g = p-1$. This means that $g\equiv -1 \pmod p$. Further note that $a$ and $b$ are $1536$-bit prime numbers, thus they're both highly likely to be odd, meaning there's a high likelihood that $ab$ is odd and $g^{ab} \equiv (-1)^{ab} \equiv -1 \equiv p-1\bmod p$.

So, we need only check that the shared key ($C$) is $p-1$ - and indeed, decrypting with this gives us the flag.