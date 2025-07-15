# imrand

#### imrand v0.2 - Uploaded August 19 2023

## A tool to generate true random numbers

## Disclaimer

This is an experimental model and as of v0.2, has not been designed to conform to standardized randomness tests. Do NOT use this model to generate random numbers for cryptographic applications.

# How to use

Use the `-h` option to view commands and options.

# Random Number Generators - A brief overview

Computers are deterministic machines designed to follow a set of instructions to reach some end state in a finite amount of time. Every operation performed by a computer can be traced back to some instruction given to it, either by another machine or directly by the user in the form of programs.

Computers are, therefore incapable of generating truly random numbers. For most use cases like simulating a random dice throw in a video game, the event must only seem random as opposed to being "truly" random. For such a task, an algorithm called a Pseudo Random Number Generator (PRNG) is used which can generate sequences whose properties mimic the properties of a truly random sequence.

The basic functionality of a PRNG is to take some initial starting value and then manipulate it on every iteration, generating a seemingly random new value every time. The PRNG will eventually cycle back to the first value it generated, meaning that it generates a periodic sequence; However, this property can be ignored since most PRNGs in use today have periods that would take several times the lifespan of the universe before they start to repeat themselves.

A fundamental property of a PRNG, however, is the fact that the sequence it generates depends completely on the initial value (seed) given to the algorithm. Hence, if the seed fed to the algorithm gets exposed, it is a trivial task to replicate and even predict the outcomes of the generator. This predictability can become a serious vulnerability if these random sequences are used to establish keys for cryptographic exchanges. Hence, a conventional PRNG can not be used for cryptographic applications.

One way to generate cryptographically secure random sequences is to devise a True Random Number Generator (TRNG) that generates random values from an external event having some inherent entropy, for example, a decaying radioactive sample, a camera pointed at a busy intersection, a microphone attached in a shopping center, etc.

# Implementation

## Entropy engine

### Modes of operation:

* Image-Based Randomness (IBR): An image is captured from a connected capture device, resized, and converted to a bit matrix of arbitrary dimensions. Bits are then individually extracted from this matrix using a non-linear Hénon map (with classical values a = 1.4 and b = 0.3) which chaotically jumps around within the array and picks one bit on every iteration. Runs for `nbits` iterations (where 1 <= `nbits` <= 512). This method requires a considerable amount of computation since it involves capturing and processing an image. Hence, it is more efficient to use the random number output as a seed which is then fed to a PRNG.
* Cursor Position Randomness (CPR): The user is required to move the mouse pointer to generate random bits. The LSBs of the x and y coordinates of the cursor position are XORed and appended to the output stream, adding approx. 1 bit of entropy on each iteration. The generator produces its output at a byte level, i.e., in multiples of 8 iterations repeated `nbytes` times in total to generate `n` random bytes (where 16 <= `n` <= 32).

## PRNG

* The `get_nbits()` method: Pseudorandom sequences are generated using a 128-bit Fibonacci Linear Feedback Shift Register corresponding to the primitive polynomial x`<sup>`128`</sup>`+x`<sup>`127`</sup>`+x`<sup>`126`</sup>`+x`<sup>`121`</sup>`+1 with coefficients over the Galois field GF(2). This LSFR has maximum period 2`<sup>`128`</sup>`-1.
  On every call, the LSFR preserves its final state by updating an instance variable. This allows the method to generate non-repeating sequences on successive calls.
* The `get_ranged_ints()` method: `n` random integers are generated in the interval `[a, b]` by calling `get_nbits()` iteratively `n` times in total to generate floor(log2(b-a)) + 1 bits on every iteration. For every call `get_nbits()` returns a random decimal number in the range (0, (b-a)+x] for some arbitrary x.
