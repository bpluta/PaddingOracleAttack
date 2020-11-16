# Padding Oracle Attack

Implementation of padding oracle attack in Python. This exploit works with ciphers encrypted in CBC mode with PKCS7 padding and gives ability for cipher decryption as well as message encryption without knowing secret private key that is used by opposite side.

## Block Ciphers

Block cipher is a encryption method in which instead of applying encryption algorithm to the whole message at once, it is first divided to fixed length blocks and then each block is encrypted separately.<br>
To prevent the same message blocks from being encrypted in the same way and to increase entropy usually there is applied some form of combination with previously encrypted block before applying encryption algorithm to the block. There are few such modes that can be used for block ciphers but as Padding Oracle Attack focuses on CBC mode we will look more closely into this one.

Symbol | Definition
--- | ---
IV | Initialization Vector used as a first block of cipher used for correct encryption and decryption
C<sub>i</sub> | i-th block of encrypted cipher
P<sub>i</sub> | i-th block of decrypted plain text
D(X) | Function decoding given block X using secret private key  
E(X) | Function encoding given block X using secret private key    
I(X) | Function decoding given block X to its intermediate form in decryption process by using padding correctness response from oracle  |  


### CBC mode
CPC (Cipher Block Chaining) is a block combination mode in which during encryption process each plain text block is XORed with previous cipher block before applying encryption algorithm.

Naturally the first block does not have anything that could be XORed with which weakens the cipher of the block. That is why there is added block initialization vector (IV) as a first cipher block to strengthen the cipher and to add more entropy. This block does not contain any message and can be skipped during decoding however it indirectly affects all the cipher blocks. That is why encrypting the same message with the same private key but with different IVs will produce completely different data which increases entropy of our cipher.


### Encryption
As explained above, encryption in CBC mode comes down to generating an IV first which is set as a first cipher block (C<sub>0</sub>). After we have set C<sub>0</sub> we can start chaining by XORing it with the first plain text block and apply encryption algorithm to the result - encrypted block is now C<sub>1</sub>. Whole chaining process is repeated until the last of message blocks.
>C<sub>0</sub> = IV<br>
C<sub>i</sub> = E(P<sub>i</sub> ⊕ C<sub>i-1</sub>)

### Decryption
During decryption process we can skip the first block as C<sub>0</sub> = IV. Starting from the second block we decode plain text by XORing cipher block C<sub>i</sub> in decrypted form with previous cipher block until we finish last of the cipher blocks.
>P<sub>i</sub> = D(C<sub>i</sub>) ⊕ C<sub>i-1</sub>

### Padding

Message padding is a solution to a problem when message length is not multiple of block size. In this scenario we have to fill missing bytes with some values to align length of our message.<br>
PKCS7 Padding is a standard in which `n` missing bytes are set to value `n`. The padding is added always - even if the message length is a multiple of block size. In such case PKCS7 determines that message should be padded by adding full block filled with values set to block size.

Example PKCS7 padded message "Hello world!" will look like this (for 16 byte block size):
```
|H|e|l|l|o| |w|o|r|l|d|!|4|4|4|4|
```

### Oracle
We define oracle as a blackbox we do not know much about - we only can send input message to it and receive its response based on given input. Usually it is a remote server we do not have access to that decrypts cipher we send and does certain actions based on the decrypted content. Padding Oracle Attack relies on the response from a oracle and it works only if the oracle let us know if the message has been decrypted correctly or not.

## Decryption using Padding Oracle Attack
Whole process of decryption of given cipher comes down to this formula:
P<sub>i</sub> = I(C<sub>i</sub>) ⊕ C<sub>i-1</sub>

### Description

As we know, the first block of CBC cipher is initialization vector (IV) which is not a part of a message we want to decode. We can skip decoding it as it probably will not contain any interesting information but we should keep its cipher form as it is needed to decrypt the first plain text block of message.

>IV = C<sub>0</sub>

Knowing that the first block does not contain any part of decoded message we should decode all blocks starting from the second one until the end of the cipher.<br>
To decode each block first we should compute intermediate form I<sub>i</sub> of cipher block that is being decoded. This is the part that uses response about padding correctness from our oracle (details of the algorithm are described in the next subsection). After we get the immediate form I<sub>i</sub>, decoding corresponding message block is as simple as XORing it with previous cipher block C<sub>i-1</sub>.

>I<sub>i</sub> = I(C<sub>i</sub>)<br>
>P<sub>i</sub> = I<sub>i</sub> ⊕ C<sub>i-1</sub>

After completing the last cipher block in the loop we should have our whole message decoded!

#### I(X) - Decoding Intermediate form

Knowing that blocks padded with PKCS7 padding end with bytes which value is the number of bytes that are added and that our given cipher block must have correct padding we can use oracle we can generate the immediate form of the cipher block if only we have ability to determine correctness of padding from response of our oracle.

Whole process comes down to finding a value corresponding to each byte in given cipher block for which our oracle does not return invalid padding in its response.<br>

We start with initializing C1 block with zeros:

>C1 = 0<br>

Then we start guessing value for given position by setting the position byte to value from 0 to 255 inclusive.

>C1<sub>position</sub> = guessed value<br>
>C1<sub>position+1 ... block size</sub> = I<sub>position+1 ... block size</sub> ⊕ block size - position

After we create C1 block with guessed value on given position we should check if our guess is correct by sending block C1 concatenated with cipher block C (C1 + C) to our oracle. The rule is - if oracle does not return response saying that padding is invalid our guess is correct - if not - we need to guess next value from range (0-255) until we get the correct one.<br>
Finally as we guess the value that is generating the correct padding we set immediate form block on given position to the guessed value XORed with position of the byte from the end of the block:

>I<sub>position</sub> = guessed value ⊕ block size - position


## Encryption using Padding Oracle Attack
Whole process of encryption of given plain text message P comes down to this formula:
C<sub>i</sub> = I(P<sub>i+1</sub>) ⊕ C<sub>i+1</sub>

### Description

During the encryption process we use padding oracle to find a block that will cause the next block to be decoded as we desire. That is why it does not really matter what the last block is and we can set it to any arbitrary value (e.g. any chosen plain text block).<br>As we need this value to encrypt previous blocks the first step is to set the last cipher block to any chosen value:<br>
>C<sub>message blocks</sub> = ?

The next step is reversed iteration over blocks with message to encode during which we should compute encrypted block.<br>
Encryption proces is quite simple and it can be done by simply XORing next block (the previously encrypted) with the immediate form of the current plain text block (computed in the same way as it is in the decryption process).

>I<sub>i</sub> = I(P<sub>i</sub>)</br>
>C<sub>i</sub> = I<sub>i</sub> ⊕ C<sub>i+1</sub>

After finishing all the iterations all the way down to the first block of message, we should have all blocks encrypted.

## Usage

To make this exploit work there is one condition that must be met - we must be able to obtain information if encrypted message that has been sent to the server has correct padding. In other words - the opposite side must provide us information if it could decrypt our message correctly or not.

Before running we should customize `run.py` file basing on our case - implement method that contacts with our oracle and returns true or false weather given message has correct padding. After completing that we can call one of the two methods:

 - `decoder.decode_cipher(cipher_string, oracle, block_size, encoding)` - if we want to decode cipher (returns string with decrypted plain text message)<br>
 - `encoder.encode_message(message_to_encode, oracle, block_size, encoding)` - if we want to encode message (returns hex string with encrypted message)

For each of the methods only two first arguments are required:
- `cipher_string` in `decode_cipher` method - hex string with cipher we want to decode
- `message_to_encode` in `encode_message` method - plain text message string we want to encode
- `oracle` - function that returns true or false basing on oracle response (as described above)

By default when not passed `block_size` is set to `16` bytes (128 bits) and default `encoding` is set to `utf-8`.

This implementation does not use any external libraries so unless we did not use any during our customization running the exploit comes down to entering:
```
python run.py
```

### Example
There is working example that involves both decryption and encryption on this [branch](https://github.com/bpluta/PaddingOracleAttack/tree/PicoCTF2018). This example is a solution for PicoCTF 2018 "Magic Padding Oracle" challenge.
