The code generates a number $n = pq$, where $p$ and $q$ are $512$-bit primes, a random integer $1 < k < n$ coprime to $n$, and sets $g = 1 + kn$. Integers $1 < a < n$ and $1 < b < n$ are also generated, and the public keys $A$ and $B$ are calculated as:
$$A = g^a \bmod n^2$$
$$B = g^b \bmod n^2$$

We are retured every variable up to this point (except $p$ and $q$), and our goal is to calculate $g^{ab}\bmod p$ (as this is the secret key used to encrypt our flag).

Note that the binomial theorem, for some integer $x$, gives us
```math
g^x = (1 + kn)^x = 1 + \binom x1kn + \binom x2k^2n^2 + \cdots + \binom xxk^xn^x.
```
Importantly, since our public keys are calculated under $\bmod n^2$, the terms multiplied with the powers $n^2, n^3, \dots, n^x$ must all become $0$ under the modulus (since $n^m = n^2 \cdot n^{m-2} \equiv 0 \pmod{n^2}$ for $m \ge 2$). Also note $\binom x1 = x$. Thus:
```math
A \equiv 1 + kan \pmod{n^2}
B \equiv 1 + kbn \pmod{n^2}
```

To calculate $g^{ab} \equiv 1 + kabn \pmod{n^2}$, we should probably try retrieving $a$ first. Note that we can subtract $1$ and divide by the modular inverse of $k$ under $\pmod{n^2}$ to obtain $an\bmod n^2$ - the non-obvious step is dividing by $n$ again to get $a\bmod n$.

The reason this approximately works is $\pmod n^2$ "layers" two $\pmod n$ subspaces, and multiplying by $n$ forces the numbers to operate under $\bmod n$. We can then multiply $a\bmod n$ by $B-1$ (even though the former is in $\pmod n$ while the latter is in $\pmod {n^2}$) to get $kabn$, and after adding $1$ we obtain $1 + kabn \equiv g^{ab}\pmod{n^2}$. A formal proof is left as an exercise for the reader :P (hint: consider the space as a group product, or alternatively write everything as non-modular equations by introducing unknown quotients).