The code generates a number $n = pq$, where $p$ and $q$ are $512$-bit primes, a random integer $1 < k < n$ coprime to $n$, and $g = 1 + kn$. Integers $1 < a < n$ and $1 < b < n$ are also randomly generated (these are the "private keys"), and the public keys $A$ and $B$ are calculated as:
$$A = g^a \bmod n^2$$
$$B = g^b \bmod n^2$$

We are retured every variable up to this point apart from $p,q,a,b$, and our goal is to calculate $g^{ab}\bmod p$ (as this is the secret key used to encrypt our flag).

The binomial theorem gives us (for some integer $x$):
```math
g^x = (1 + kn)^x = 1 + \binom x1kn + \binom x2k^2n^2 + \cdots + \binom xxk^xn^x.
```
Importantly, since our public keys are calculated under $\bmod n^2$, the terms multiplied with the powers $n^2, n^3, \dots, n^x$ must all become $0$ under the modulus (since $n^m = n^2 \cdot n^{m-2} \equiv 0 \pmod{n^2}$ for $m \ge 2$). This, along with the fact that $\binom x1 = x,$ gives:
```math
A \equiv 1 + kan \pmod{n^2}
```
```math
B \equiv 1 + kbn \pmod{n^2}
```

To calculate $g^{ab} \equiv 1 + kabn \pmod{n^2}$, we can try retrieving $a$ first. Note that we can subtract $1$ from $A$ and divide by the modular inverse of $k$ under $\pmod{n^2}$ to obtain $an\bmod n^2$ - from here, we can actually obtain $a\bmod n$ by simply dividing normally by $n$.

This step is not totally obvious. A hand-wavy reason why it works is that $\pmod n^2$ is composed of two "layers" of $\pmod n$, and multiplying a number by $n$ forces it to move around the $\pmod n$ space.

Now that we have $a\bmod n$, we can multiply it to $B-1$ (even though the former is in $\pmod n$ while the latter is in $\pmod {n^2}$) to get $kabn$, and after adding $1$ we obtain $1 + kabn \equiv g^{ab}\pmod{n^2}$. A formal proof of why this works is left as an exercise for the reader :P (hint: consider the space as a group product, or alternatively write everything as non-modular equations by introducing unknown quotients).