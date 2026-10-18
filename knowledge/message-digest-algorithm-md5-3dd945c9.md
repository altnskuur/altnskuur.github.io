---

# What is the MD5 Algorithm

![MD5 Block Diagram](knowledge/assets/3dd945c9dc43808283a1dfc8038a272b/01.png)

**MD5** is a cryptographic hash function algorithm that takes the message as **input of any length** and changes it into a fixed-length message of 16 bytes. MD5 algorithm stands for the Message-Digest algorithm. MD5 was developed in 1991 by Ronald Rivest as an improvement of MD4, with advanced security purposes. **The output of MD5 (Digest size) is always 128-bits.** MD5 is still widely used for non-security purposes, such as checksums that detect accidental data corruption during downloads or storage. It should not be trusted against a deliberate attacker: anyone who controls a file's contents can create two different files with the same MD5 hash. Note that hashing is not compression: a hash cannot be reversed to recover the original data.

> **Security warning:** MD5 is cryptographically broken and must not be used for security purposes. Practical collision attacks were published by Wang et al. in 2004–2005, chosen-prefix collisions followed in 2007, and MD5 collisions have been used in real attacks, such as the forged Microsoft certificate used by the Flame malware in 2012. Today, an MD5 collision can be generated in seconds on an ordinary computer. RFC 6151 (2011) advises against using MD5 wherever collision resistance is required. For security purposes, use SHA-256, SHA-3, or BLAKE2/BLAKE3 instead.

# Working of the MD5 Algorithm

## 512-Bits Padding

![MD5 Padding](knowledge/assets/3dd945c9dc43808283a1dfc8038a272b/02.png)

The primary goal of MD5 padding is to ensure that the final length of the padded message is an exact multiple of **512 bits**. No matter how long or short the original message is, it must be restructured so it can be neatly divided into **sequential 512-bit blocks**.

The padding pipeline follows strict rules defined in the original specification (RFC 1321):

- **Step 1: Appending a Single '1' Bit**
  A single bit with the value `1` is appended immediately to the end of the original message (K-bits).

- **Step 2: Appending Zero Bits ('0')**
  Zero bits are appended until the message length is congruent to 448 modulo 512 (length ≡ 448 mod 512). In other words, the message is padded until it is exactly 64 bits short of a multiple of 512, leaving room for the 64-bit length field. Between 0 and 511 zero bits are added.

- **Step 3: Appending the Length Field**
  The original message length K (in bits), taken modulo 2⁶⁴, is appended as a **64-bit little-endian** integer. After this step, the total length is an exact multiple of 512 bits. This construction is called Merkle–Damgård strengthening (explained below).

### Merkle–Damgård Strengthening (Length Padding)

MD5 is built on the **Merkle–Damgård construction**, a general method (described independently by Ralph Merkle and Ivan Damgård in 1989) for hashing messages of any length using a compression function that accepts only fixed-size input:

1. The message is padded and split into 512-bit blocks.
2. The state starts from fixed initial values (A, B, C, D).
3. Each block is combined with the current state by the compression function, producing a new state.
4. After the last block, the final state is the hash.

`IV → [Block 1] → state₁ → [Block 2] → state₂ → … → [Block n] → hash`

**Merkle–Damgård strengthening** is one specific rule within this construction: the original message length is included in the padding (Step 3 above). The same construction is also used by SHA-1 and SHA-2.

## Byte Order (Endianness)

MD5 operates on 32-bit words, but messages arrive as bytes. **Endianness** defines how 4 bytes are combined into one word. MD5 uses **little-endian** order everywhere: the first byte becomes the least significant byte of the word.

It applies in four places:

- **Message words:** Each 512-bit block is split into 16 words `M[0]…M[15]`, each built from 4 bytes in little-endian order.
- **Length field:** The 64-bit length is appended least significant byte first.
- **Initial values:** The word `A = 0x67452301` is stored in memory as the bytes `01 23 45 67`. RFC 1321 lists the initial values in this byte form.
- **Output:** The final digest writes A, B, C, D in little-endian order, one after another.

**Example: the message "abc"**

- Bytes: `61 62 63`, followed by the padding byte `80` (the `1` bit followed by seven `0` bits).
- First word: bytes `61 62 63 80` → `M[0] = 0x80636261`
- Length: 24 bits = `0x18` → bytes `18 00 00 00 00 00 00 00` → `M[14] = 0x00000018`, `M[15] = 0x00000000`
- Output: for the empty message, the final value of A is `0xd98c1dd4`, which is written as the bytes `d4 1d 8c d9`. This is why MD5("") begins with `d41d8cd9…`.

## General Operations and Register Shifting 

![MD5 Box Block Diagram](knowledge/assets/3dd945c9dc43808283a1dfc8038a272b/03.png)

The diagram above illustrates the high-level operational flow of a single step within the MD5 compression loop, focusing on how data words and working registers interact before advancing to the next state.

### 1. The Padded Message Array (0 to 15)

- **Data Source:** The top array represents a single 512-bit message block divided into 16 sequential 32-bit words (indexed from 0 to 15).
- **Index Selection:** During each round of the MD5 compression function, specific words from this array are fetched dynamically based on the current step index, feeding the core mixing operations.

### 2. Working Registers (A,B,C,D)

- **State Initialization:** MD5 utilizes four 32-bit working registers, denoted as A, B, C, and D, which hold the intermediate hash values. Before any message blocks are processed, these registers are initialized to specific standard constants (expressed in hexadecimal, little-endian byte order):
  - A = `0x67452301`
  - B = `0xEFCDAB89`
  - C = `0x98BADCFE`
  - D = `0x10325476`
- **Input Routing:** In any given step, the current values of these registers are fed directly into the core processing logic alongside the selected message word from the padded array.

### 3. State Evolution and Register Shifting (A′,B′,C′,D′)

- **Transformation:** Inside the primary operation pipeline, non-linear auxiliary functions, modular additions, and bitwise rotations are executed.
- **Output Propagation:** Once the step operations conclude, the updated values are shifted and assigned to the next state registers (A′, B′, C′, D′). These outputs then cascade as the initial working state for the subsequent step in the compression loop.

### 4. Message Word Selection and Index Sequencing (The Four Rounds)

While the padded message block is naturally ordered from index 0 to 15, the MD5 compression loop does not process these words sequentially in every round. Instead, it executes **4 distinct rounds** (64 steps in total, 16 steps per round), where the message word index i for each step is selected using a specific algorithmic mapping:

- **Round 1 (Steps 0–15):** Sequential order
  - $Index=i$
- **Round 2 (Steps 16–31):** Linear step stride
  - $Index=(5×i+1)(mod16)$
- **Round 3 (Steps 32–47):** Permuted stride
  - $Index=(3×i+5)(mod16)$
- **Round 4 (Steps 48–63):** Pseudo-random / pseudo-cyclic permutation
  - $Index=(7×i)(mod16)$

**Why this matters:** These formulas ensure that the mixing function does not rely on simple linear patterns, drastically increasing diffusion and breaking any structural correlations in the input data across rounds.

## Main Operation (MainOp Box)

![Main Operation Box Block Diagram](knowledge/assets/3dd945c9dc43808283a1dfc8038a272b/04.png)

The **MainOp Box** is the core processing unit of a single MD5 step, where working registers and message inputs are mixed through three main stages:

- **1. Auxiliary Function (F):** A round-dependent, non-linear bitwise logical function taking inputs from registers B, C, and D to scramble the data patterns.
- **2. Modular Additions (⊞):** The result is combined with register A, a specific word from the padded message block, and a pre-calculated round constant using modulo $2^{32}$ addition.
- **3. Bitwise Left Rotation (Red Box):** The accumulated sum undergoes a circular left-shift (rotation) by a defined offset value (s) to maximize bit diffusion before updating the state registers.

## Binary Operations

### Bitwise OR - `|`

Yields 1 if at least one of the input bits is 1; otherwise, it returns 0. Evaluating binary 1100 and 1010 results in 1110. (`1100 | 1010 = 1110`)

### Bitwise AND - `&`

Yields 1 only if both input bits are 1; otherwise, it returns 0. Evaluating binary 1100 and 1010 results in 1000. (`1100 & 1010 = 1000`)

### Bitwise XOR - `^`

Yields 1 when the input bits are different from each other; otherwise, it returns 0. Evaluating binary 1100 and 1010 results in 0110. (`1100 ^ 1010 = 0110`)

### Bitwise NOT - `~`

Inverts all the bits, flipping every 0 to 1 and every 1 to 0. Evaluating binary 00001111 results in 11110000. (`~00001111 = 11110000`)

### Bit Rotation (Circular Shift)

Shifts the bits of a value to the left or right by a specified number of positions, where any bits falling off one end wrap around and reappear on the opposite end. Evaluating a left rotation of binary 10000001 by 1 position results in 00000011. (`ROL(10000001, 1) = 00000011`)

### Bit Addition (Modular Addition)

Combines numerical values or bit patterns using standard integer addition modulo 2 to the power of 32, meaning any overflow beyond 32 bits is naturally discarded. For 4 bits example, evaluating binary 1111 and 0001 results in 0000 with a carry out. (`1111 + 0001 = 0000`)

## $F(B, C, D, i)$ Function

### Auxiliary Functions (F, G, H, I)

In each step, MD5 applies one of four **auxiliary functions** to registers B, C, and D. RFC 1321 names them only by letter (F, G, H, I); descriptive names such as "Choose" and "Parity" are informal labels used in textbooks, not part of the standard. All four functions work bitwise: bit n of the output depends only on bit n of B, C, and D.

- **Round 1 (Steps 0–15) – F: Choose (selector B)**
  - `F(B, C, D) = (B & C) | (~B & D)`
  - A bitwise multiplexer: where a bit of B is 1, the output takes the bit from C; where it is 0, the output takes the bit from D. ("If B then C else D.")
- **Round 2 (Steps 16–31) – G: Choose (selector D)**
  - `G(B, C, D) = (B & D) | (C & ~D)`
  - Also a multiplexer, but with D as the selector: where a bit of D is 1, the output takes the bit from B; otherwise it takes the bit from C. ("If D then B else C.")
- **Round 3 (Steps 32–47) – H: Parity (XOR)**
  - `H(B, C, D) = B ^ C ^ D`
  - The output bit is 1 when an odd number of input bits are 1. H is **linear** over GF(2): a flipped input bit always flips the output bit, so differences pass through with certainty. In round 3, non-linearity comes from the modular additions instead, while H spreads each change evenly across all three registers.
- **Round 4 (Steps 48–63) – I: OR-NOT-XOR**
  - `I(B, C, D) = C ^ (B | ~D)`
  - Combines OR, NOT, and XOR. It has no widely used descriptive name; "the I function" is the usual term.

## Binary Operation (BinaryOp Box)

![](knowledge/assets/3dd945c9dc43808283a1dfc8038a272b/05.png)

The **BinaryOp Box** acts as the final transformation pipeline within an MD5 step, taking the intermediate data stream and routing it through three sequential operations:

- **K-Table Addition:** The incoming data stream is combined via modular addition with a pre-calculated constant (K[i]) fetched from the K-Table, ensuring pseudo-randomness and breaking linear patterns.
- **R-Numbers Rotation (Circular Shift):** The resulting sum undergoes a bitwise left-rotation (circular shift) by an offset amount (s) defined by the R-Numbers table, maximizing bit diffusion and instigating the avalanche effect.
- **Addition with Register B:** Finally, the rotated value is added to register B using addition modulo 2³². This injects the current state back into the result, so the history of previous steps influences every new step.

### K-Table

The **K-Table** is a fixed array of 64 constants, each 32 bits long. One constant, K[i], is added in each of the 64 steps of the MD5 compression function. Its main role is to make every step different from the others, so that the algorithm has no repeating patterns an attacker could exploit.

1. Mathematical Generation

The constants are derived from the sine function rather than chosen by hand. For each step index i (0 to 63), K[i] is computed by taking the absolute value of the sine of i + 1 (measured in **radians**), multiplying it by 2³², and taking the integer part (floor):

`K[i] = ⌊2³² × |sin(i + 1)|⌋`

For example, sin(1) ≈ 0.8415, so K[0] = ⌊2³² × 0.8415…⌋ = `0xd76aa478`, and K[1] = `0xe8c7b756`.

- **Radians are essential:** Using degrees would produce completely different constants.
- **Notation in RFC 1321:** The RFC calls this table T[1…64] and uses sin(i) with i starting from 1. It is the same table; only the indexing differs.
- **Nothing-up-my-sleeve numbers:** Because the constants come from a simple public formula, anyone can verify them. This shows the designer did not hide a secret weakness in the values.

2. Cryptographic Purpose

- **Breaking Symmetry:** Without constants, all 16 steps of a round would perform the same operation, differing only in the message word. A unique constant in every step makes each of the 64 steps behave differently. This prevents attacks that exploit repeated, identical steps and removes simple patterns, for example when the input block is all zeros.
- **Supporting Non-linearity:** The constants are combined using addition modulo 2³², which is non-linear over GF(2) because carry bits are ANDs of input bits. This non-linearity comes from the addition itself, not from the constant values: adding the same constants with XOR would remain linear.
- **Varying Step Behavior:** Because each step adds a different value, carries appear in different bit positions from step to step. This makes it harder to predict how a change in the input travels through the 64 steps.

Note that these properties did not make MD5 secure in the end: Wang et al. (2004) found collisions using differential cryptanalysis despite the constants. The K-Table makes the algorithm more irregular, but it is not a security guarantee on its own.

### R-Numbers

The **R-Numbers** table consists of a pre-defined sequence of shift offset values utilized across the 64 steps of the MD5 compression loop to maximize bit diffusion and drive the avalanche effect.

1. Functional Mechanics

- **Circular Left-Shift (Rotation):** Within each step's computation pipeline, the intermediate data stream undergoes a bitwise circular left-rotation by a specific offset value (s) fetched directly from the R-Numbers table.
- **Dynamic Variation:** These rotation values are systematically varied across the four rounds (using step-specific offsets such as 7, 12, 17, and 22 in the initial round, 5, 9, 14, 20 in the round 2, 4, 11, 16, 23 in the round 3, and lastly 6, 10, 15, 21 in round 4) to ensure that the bit-mixing pattern changes continuously throughout execution.

2. Cryptographic Purpose

- **Enhancing Bit Diffusion:** While modular addition and non-linear functions alter the numerical values of the data, rotation ensures that individual bits physically move across different bit positions.
- **Propagating the Avalanche Effect:** By circulating bits around the 32-bit word boundary at every single step, any localized alteration in the input data spreads rapidly and unpredictably across the entire register state, ensuring total structural chaos and preventing algebraic inversion.

## Processing Multiple Blocks and Producing the Digest

The 64 steps described above process **one** 512-bit block. A full message is processed block by block:

1. **Initialize** the chaining values A, B, C, D with the standard constants.
2. **For each 512-bit block:**
  - Copy the chaining values into working registers: `a = A, b = B, c = C, d = D`.
  - Run the 64 steps on a, b, c, d using this block's 16 message words.
  - **Feed-forward:** add the result to the values from before the block (all additions mod 2³²):
    - `A = A + a`
    - `B = B + b`
    - `C = C + c`
    - `D = D + d`
  - The updated A, B, C, D become the starting values for the next block.
3. **Output** the digest as `A ‖ B ‖ C ‖ D`, with each 32-bit word written in little-endian byte order (4 words × 4 bytes = 16 bytes = 128 bits).

### Why the Feed-Forward Matters

Each of the 64 steps is reversible: if you know the message block and the state after a step, you can compute the state before it. Without the feed-forward, anyone could run all 64 steps backwards from the output and recover the input state. Adding the input state to the output mixes the start and end of the computation together and destroys this reversibility. This design is known as the **Davies–Meyer construction**.

# Test of MD5

# Some Questions About MD5 Design and Research Outputs

## **What is the MD5 Algorithm**

***“Note that hashing is not compression: a hash cannot be reversed to recover the original data.”*
Why MD5 algorithm cannot reversable? **

**Reorganized Claude Answer:**

Not by itself. Non-linearity is one part of it, but the main reason a hash can't be reversed is something simpler: **information loss**.

There are actually three separate reasons, and it helps to keep them apart:

**1. Information loss (the main reason).** MD5 maps inputs of *any* length to just 128 bits. There are infinitely many possible inputs but only 2¹²⁸ outputs, so each hash value is shared by infinitely many different inputs (the pigeonhole principle). Even with unlimited computing power, you could never know *which* input was the original. The data is simply gone. This is what your sentence is about, and it would be true even for a completely linear hash.

**2. Feed-forward (the Davies–Meyer step).** As we discussed before, each of the 64 steps is reversible when you know the message block. Adding the starting state to the result at the end of each block is what stops someone from running the steps backwards.

**3. Non-linearity.** This addresses a different question: not "can you recover the *original* input?" but "can you find *any* input that produces a given hash?" (called **preimage resistance**). If MD5 were fully linear over GF(2), finding such an input would just mean solving a system of linear equations, which is easy (Gaussian elimination). Non-linearity makes those equations very hard to solve.

Non-linear does not mean irreversible: MD5's individual steps are non-linear, yet each one can still be undone. Non-linearity makes inversion *hard to calculate*; information loss makes the original *impossible to identify*.

Also, "hashing is not compression" can confuse readers, because MD5's internal block function is officially called a **compression function**. Here is a more precise version you can paste instead:

**What is the Wang et al.?**

**Reorganized Claude Answer:**

"et al." is Latin for "and others." It refers to the Chinese cryptographer **Xiaoyun Wang** and her co-authors Dengguo Feng, Xuejia Lai, and Hongbo Yu. In 2004 they announced the first real MD5 collisions: two different messages with the same hash. More importantly, they published a **method** to generate such collisions on demand, not just one lucky example. The full technique appeared in 2005 in the paper "How to Break MD5 and Other Hash Functions" (Wang & Yu, EUROCRYPT 2005).

**Where can we use this MD5 algorithm? Can we use like CRC? I saw MD5 file in an Ubuntu ISO output. Why MD5 is in Ubuntu ISO output? **

**Reorganized Claude Answer:**

The rule is simple: **use MD5 only when no attacker is involved.** It still works perfectly well for detecting *accidental* changes. In that role it's like CRC, but with a much larger 128-bit output. A random corruption producing the same MD5 is practically impossible.

**The Ubuntu file you saw** is exactly this case. Ubuntu ISO images contain a file called `md5sum.txt` listing the MD5 of every file on the disc. When you boot and choose "Check disc for defects," the system recalculates those hashes to catch a bad USB write or a damaged DVD. That's pure accidental-corruption detection, a perfect use for MD5.

You can do the same yourself:

- Linux: `md5sum file.iso`, or `md5sum -c file.md5` to check against a list
- Windows: `certutil -hashfile file.iso MD5`

**Other acceptable uses:**

- Checking that a download or copy wasn't corrupted
- Deduplication: finding identical files in your own storage
- Cache keys and hash-table keys, when inputs aren't chosen by an attacker
- Some protocols still use it, for example the ETag of a simple (single-part) Amazon S3 upload

**Never use MD5 for:**

- **Passwords.** It's broken and also far too fast. Use Argon2, bcrypt, or scrypt.
- Digital signatures and certificates
- Proving a file wasn't tampered with by an attacker

## Working of the MD5 Algorithm

### 512-Bits Padding

**Why do we add 1 end of the message and fill with 0? Why do not we choose any other spesific combination for this process? For example add four 0, two 1 at the end of the message, and fill other places with 1’s.**

**Reorganized Gemini Answer:**

### Why MD5 Padding Uses `1` Followed by `0`s (and Not Other Combinations)

1. Mathematical and Logical Neutrality (Zero Entropy Impact)

Zeros (`0`) do not introduce artificial weight or unwanted bit density into bit-level operations—specifically the additions, XOR, and AND/OR operations that form the core of MD5.

- If you filled the remaining space entirely with ones (`1`), you would append a massive block of high-bit density to the end of the message.
- This could negatively impact the bit entropy inside the blocks and the mixing functions of the hash algorithm, potentially making collision probabilities mathematically unpredictable. A sequence of zeros acts as the purest "empty space" padding material.

2. The Uniquity Rule (Injective Mapping)

The most vital rule of any cryptographic padding scheme is **injective mapping** (uniquely decodable):

- Two different original messages must never produce the exact same padded output.
- The standard triplet of `1` **+** `0`**s + Original Length** provides mathematically flawless uniqueness and ensures that variable-length messages never map to the same padded block boundary.

3. Why Alternative Combinations (e.g., Random Patterns) Fail

If we had chosen a custom pattern—such as inserting four zeros, two ones, and filling the rest with ones—it would introduce severe drawbacks:

- **Zero Security Advantage:** In cryptography, using a complex or non-standard rule does not automatically make a system safer. On the contrary, non-standard approaches tend to introduce edge cases and implementation flaws.
- **Implementation Complexity:** When coding this in embedded software or hardware (FPGA/ASIC), you would be doomed to constant bit-shifting and masking operations. In contrast, appending a single `1` and flushing the rest with `0`s is the cheapest, fastest, and most error-free method—embodying the **KISS (Keep It Simple, Stupid)** principle.

### Summary

By appending a `1`, we clearly mark the boundary where the message ends. By filling with `0`**s**, we pad the space neutrally, and by sealing the block with the **original length** at the very end, the system operates seamlessly and without ambiguity.

**Claude Reviews of Gemini’s Answer:**

The "entropy" argument doesn't hold. Padding is public and deterministic, so it adds no entropy either way. The real answer is that the padding needs to be *unambiguous and injective*, and `1` + `0*` + length is the simplest pattern that achieves that. Many other fixed patterns would also work; this one is just the cheapest and conventional.

**What if I send a message whose length is 448-bits? (Length must be 64-bits. What if the message takes up all of the remaining padded bits? What if the message leaves no room for padding?)**

**Reorganized Gemini Answer:**

### What Happens If You Send a Message Exactly Equal to the Length Limit (448 Bits)?

This is the exact core of how the padding mechanism handles edge cases! If you input a message that is **precisely 448 bits (56 bytes)** long, you hit a very specific mathematical boundary.

Because of how MD5 is structured:

- The total size of the final block must be an exact multiple of **512 bits**.
- The last **64 bits** of that final block are strictly reserved for the original message length (the Length field).
- This leaves a maximum of 512−64=448 bits for the actual message body and the initial padding bit.

If your original message is **already 448 bits long**:

1. **You Cannot Append the '1' Bit Immediately:** Since your message already occupies all 448 available bits, adding the mandatory `1` bit overflows the block, pushing the length to 449 bits.
2. **A Second Block Must Be Created:** Because a 448-bit message + the `1` bit + the 64-bit length field equals 513 bits (which exceeds the 512-bit limit), the algorithm is forced to **open a second 512-bit block**.
3. **How the Padding is Handled:**
  - **Block 1:** Your original 448-bit message is placed here, immediately followed by the required `1` bit. The rest of this block is filled entirely with `0`s to close out the first 512 bits.
  - **Block 2 (New Block):** This block is filled entirely with `0`s, except for its very end (the final 64-bit length field), where the original length value of **448** is written.

In short, even if your message fills the data portion of a single block perfectly, you cannot finish in one block. The algorithm must trigger a **two-block operation**: padding and closing the first block with the `1` and `0`s, and placing the length seal at the bottom of the second block.

**Claude Reviews of Gemini’s Answer:**

The conclusion is correct, but point 1 ("You cannot append the '1' bit immediately") contradicts point 3, which correctly says the `1`  *is* appended immediately. Generalize the rule: any message with length mod 512 ≥ 448 needs an extra block. 

**Why Ronald choose the exact that equation of these rounds? Why he do not determine any of the equations as $Index=(5×i+12)(mod16)$?**

**Reorganized Gemini Answer:**

### Why Specific Index Formulas (e.g., $5i + 1$) Are Chosen in MD5

Ronald Rivest did not choose these formulas or coefficients randomly. Behind selecting specific step formulas instead of alternatives like $5i + 12$ lie strict mathematical and cryptographic requirements:

1. The Permutation Requirement (Full Coverage)

Each round of MD5 consists of 16 steps, and every single one of the 16 32-bit words in the message block must be used **exactly once per round** (no omissions, no duplicates).

- If a formula skips words or selects the same word twice during a round, it fails as a valid permutation.
- For example, consider a formula like $6i \pmod{16}$ (where $i$ goes from $0$ to $15$):
  - For $i = 0 \rightarrow 0$
  - For $i = 2 \rightarrow 12$
  - For $i = 4 \rightarrow 8$
  - For $i = 6 \rightarrow 4$
  - For $i = 8 \rightarrow 0$  **(Conflict! Word index 0 is selected a second time, while index 2 is never reached.)**
- Because 6 and 16 are not coprime ($\text{gcd}(6, 16) = 2$), the formula creates a cycle, missing half the index space and repeating the other half. In a cryptographic hash function, missing words break diffusion and compromise security.

2. The Coprime Rule (Bijective Mapping)

For a formula of the form $f(i) = (a \times i + b) \pmod{16}$ to uniquely generate all numbers from 0 to 15 without collisions, the multiplier coefficient (a) must be **coprime** to the modulus $16 $ ($2^4$).

- This means a **must be an odd number** ($1, 3, 5, 7$, etc.). Using an even number ($2, 4, 6$) violates coprimality with $16$ and causes cycles and collisions.
- This explains the exact choices across the rounds:
  - **Round 1:** Sequential ($i \pmod{16}$)
  - **Round 2:** Multiplier $5$ ($\text{gcd}(5, 16) = 1$) $\rightarrow$  $(5i + 1) \pmod{16}$
  - **Round 3:** Multiplier $3$ ($\text{gcd}(3, 16) = 1$) $\rightarrow$  $(3i + 5) \pmod{16}$
  - **Round 4:** Multiplier $7$ ($\text{gcd}(7, 16) = 1$) $\rightarrow$  $(7i) \pmod{16}$

3. Why the Offset Constants Exist (e.g., $+1$ or $+5$)

The additive constants ($+1$, $+5$, etc.) determine the starting offset. While the constant itself does not alter the mathematical permutation property of covering all 16 elements, Rivest selected these specific offsets and coefficients through empirical testing (simulations and cryptanalytic evaluations) to maximize the **avalanche effect**, optimize bit diffusion, and eliminate linear correlations across consecutive steps and rounds.

**Claude Reviews of Gemini’s Answer:**

The coprime explanation is excellent, the best part of the page. But "Rivest chose the offsets through empirical testing" is speculation, because RFC 1321 gives no rationale. Mark it as speculation.

**Why we will add a step like F function? Because of linearity?**

**Reorganized Gemini Answer:**

Yes, exactly. The single greatest necessity for employing such complex non-linear functions and additional steps is **to break linearity and provide robust defense against linear cryptanalysis.**

If MD5, or any cryptographic hash function, consisted solely of linear operations such as addition, subtraction, or basic bit shifts, the transformation process would become entirely predictable. A malicious adversary could readily determine how a single-bit alteration in the input affects the output by solving linear equations (specifically via linear and differential cryptanalysis).

The combination of logical operators—AND, OR, NOT, and XOR—within the auxiliary function F fundamentally severs the mathematical correlation between input and output. By thoroughly scrambling the data, it triggers the **"avalanche effect."** This phenomenon ensures that even the minutest change of a single bit in the input results in approximately half of the output bits flipping randomly. In summary, these additional steps and non-linear structures serve as an essential cryptographic armor designed to guarantee security and structural chaos.

**Claude Reviews of Gemini’s Answer:**

Modular addition is actually *non-linear* over GF(2) because of carries, so calling it "linear" is imprecise. More importantly, saying these structures "guarantee security" contradicts history: MD5 was broken by differential cryptanalysis. Soften the claim.

**How can we take a linearity decisions in GF(2)? **

**Reorganized Claude Answer:**

### What is GF(2)?

GF(2) (Galois Field of 2 elements) is the number system {0, 1} with two operations:

- **Addition = XOR (⊕):** 1 ⊕ 1 = 0, because there is no carry.
- **Multiplication = AND (·):** 1 · 1 = 1, everything else is 0.

Bitwise logic functions like MD5's F, G, H, I can be studied as polynomials in this system. Each output bit depends only on the same bit position of the inputs, so it is enough to analyze a single bit.

### Method 1: Algebraic Normal Form (ANF)

Every Boolean function can be rewritten using only XOR and AND. This form is called the **Algebraic Normal Form (ANF)**. To convert, use these rules:

- `~X` → `1 ⊕ X`
- `X & Y` → `XY`
- `X | Y` → `X ⊕ Y ⊕ XY`
- If X and Y can never both be 1, then `X | Y` → `X ⊕ Y`

Then look at the result:

- **Only single variables XORed together (plus maybe a constant 1)** → degree 1 → **linear** (strictly, "affine" if the constant 1 appears).
- **Any product of two or more variables (like BD)** → degree ≥ 2 → **non-linear**.

**Example: F(B, C, D) = (B & C) | (~B & D)**

1. The two terms can never both be 1 (B cannot be 1 and 0 at the same time), so `|` becomes `⊕`: `BC ⊕ (~B)D`
2. Replace `~B` with `1 ⊕ B`: `BC ⊕ (1 ⊕ B)D`
3. Expand: `BC ⊕ D ⊕ BD`
4. It contains the products BC and BD → degree 2 → **non-linear**.

**Example: I(B, C, D) = C ^ (B | ~D)**

1. Replace `~D` with `1 ⊕ D`: `B | (1 ⊕ D)`
2. Apply the OR rule: `B ⊕ (1 ⊕ D) ⊕ B(1 ⊕ D)` = `B ⊕ 1 ⊕ D ⊕ B ⊕ BD`
3. B ⊕ B = 0, so this simplifies to `1 ⊕ D ⊕ BD`
4. Add C: `I = 1 ⊕ C ⊕ D ⊕ BD` → contains BD → **non-linear**.

**Results for all MD5 functions:**

| Function | ANF | Degree | Result |
|---|---|---|---|
| F | BC ⊕ BD ⊕ D | 2 | Non-linear |
| G | BD ⊕ CD ⊕ C | 2 | Non-linear |
| H | B ⊕ C ⊕ D | 1 | Linear |
| I | 1 ⊕ C ⊕ D ⊕ BD | 2 | Non-linear |

### Method 2: The Difference Test

A second way to decide, closer to how attackers think: flip one input bit and check whether the output change depends on the other inputs.

- If flipping an input **always** changes the output in the same way, no matter what the other inputs are → **linear**.
- If the effect **depends on the values** of the other inputs → **non-linear**.

**Example with H:** Flip C. Then `H(B, C ⊕ 1, D) ⊕ H(B, C, D) = 1`. The output flips every time, regardless of B and D → **linear**.

**Example with F:** Flip C. Then `F(B, C ⊕ 1, D) ⊕ F(B, C, D) = B`. The output flips only when B = 1 → the result depends on B → **non-linear**.

### Why This Decision Matters

Cryptanalysts track how input differences travel through a hash function.

- Through a **linear** function, a difference passes with **100% certainty**, so the attacker can predict it exactly.
- Through a **non-linear** function, a difference passes only with some **probability** (for example 50% for F), so the attacker loses certainty at every step.

Two related facts:

- **Modular addition is non-linear** over GF(2), because the carry bit is an AND of two bits.
- **Bit rotation is linear**, because it only moves bits to new positions without combining them.

So in MD5, non-linearity comes from F, G, I, and the modular additions. H is linear, but round 3 still gets its non-linearity from the additions.

# Links

[RFC 1321 The MD5 Message-Digest Algorithm Document](https://datatracker.ietf.org/doc/html/rfc1321)

[GeeksforGeeks - What is the MD5 Algorithm](https://www.geeksforgeeks.org/computer-networks/what-is-the-md5-algorithm/)

[All of the Images](https://canva.link/5fg7kfdzyuv8l1x)
