This challenge rolls out a custom [Merkle-Damgard](https://en.wikipedia.org/wiki/Merkle%E2%80%93Damg%C3%A5rd_construction) hash. Our goal is, given the zip file of a Minecraft world save folder (this part is not actually important, just that the zip file contains approximate $10$ million bytes), to find a file with different contents but the same hash to this one.

It's important to do some math here first. Each byte can be one of $256$ values, so a $5$-byte hash can be one of $256^5$ values, which is very close to $1$ trillion. Now, bruteforcing $1$ trillion hashes is... actually doable on some computers (note the contest was two days!!!!), but this is probably against the spirit of the challenge. What probably *isn't* against the spirit of the challenge is leveraging the birthday attack, which allows us to find any two colliding hashes in $O(\sqrt n)$ time for a hash with $n$ bytes of output.

You can read about it more on Wikipedia, but the basic idea is that while we expect to basically bruteforce half of all possible hashes to hit a particular target hash, out of a set of $\sqrt n$ hashes, the number of pairs is on the order of $O((\sqrt n)^2) = O(n)$ hashes, which means we can expect to get two arbitrary equal hashes, or a *hash collision* after $\sqrt n$ randomly generated hashes.

This is nice, because $\sqrt{10^{12}} = 10^6$, or a million - calculating one million hashes only takes a second or two! There's a huge problem, however - we are tasked with finding something that collides to a *specific* hash. A bit more formally, we wish to do a second-preimage attack, not a hash collision attack. This problem is pertinent as Merkle-Damgard hashes (and this hash, by implication) have two important properties:
- the hash output from one block affects the next (similarly to block chaining in AES modes)
- there's a length padding placed at the end of the plaintext message before hashing


These two properties, especially the length padding, make it hard for us to leverage hash collisions, since we (almost certainly) needed something with the same length as the zip file.

We played around with the possibility of multiple hash collisions, switching blocks around and finding small cycles/layered birthday attacks. Leveraging the fact that the file itself was so long, at this point we thought we had the vague notion of a solution that could calculate a second preimage in around $10$ billion expected hashes. This is a lot better that $1$ trillion, but it still takes a long time, and we thought it would be a pain to implement.

Our first major breakthrough was realising that this hash function was a classic Merkle-Damgard construction (as mentioned in the beginning) - this is a classic format a lot of hash functions, such as SHA and MD5, follow due it's security. Furthermore, we couldn't find a way to exploit the (sketchy) construction of the hash function's chaining of the current block and previous block hash:

```py
h = hashlib.sha256(chunk + h).digest()[:5]
```

At its base, this hash uses SHA-256, which is "experimentally secure". Thus, we figured out that if we were to exploit this hash, we very well be a second-preimage attack in the Merkle-Damgard construction itself.

This eventually led us to this paper by Kelsey and Schneier: [https://eprint.iacr.org/2004/304.pdf](https://eprint.iacr.org/2004/304.pdf). It outlines a method for finding a second-preimage in $O(k\times2^{n/2 + 1} + 2^{n-k+1})$ for Merkle-Damgard hashes, where $k$ is the logarithm (base 2) of the file length we're colliding with (since our file contains around one million $8$-byte chunks, this number would be around $20$), and $n$ is the number of bits in the output hash ($40$ for $5$ bytes). Doing the calculations, we see this works around to only $20$ million or so hashes!!!

The algorithm itself is really cool and not awful to implement, I'd highly advise you read it yourself. The tl;dr is:
- we increment some value $t$ until $t + 2^t > n$
- we construct "expandable messages" with sizes approximately equal to powers of $2$; specifically, we collide a $1$-block message with a $2^i+1$-block message using the birthday attack for increasing values of $i$ up to $t$ (the exact details for making expandable messages are talked about in the paper), using the hash value from the previous expandable message pair as the initial value for calculating the current colliding hashes
- after getting $t$ expandable messages, we birthday attack by generating a bunch of dummy blocks to extend and match with the cumulative hash of one of blocks in Hack.zip (the index of this block must be greater than $t$, which is highly likely to happen)
- after concatenating the $1$-blocks from the expandable messages, the colliding block and the rest of the byte-stream from Hack.zip, we need to make sure our message is the same length as Hack.zip, so we replace a select number of the $1$-block expandable messages with the corresponding, power-of-2 length block that hash collides with each to get the exact same length (by matching with the lengths against the binary representation of the number of blocks required to fill the rest of the length). 