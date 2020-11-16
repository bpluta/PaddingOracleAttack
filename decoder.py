from utils import *

def decode_cipher(cipher_string, oracle, block_size=DEFAULT_BLOCK_SIZE, encoding=DEFAULT_ENCODING):
    debug_print_title("DECODING CIPHER")

    # converting cipher string to byte blocks of given block size
    cipher = get_byte_blocks(cipher_string, block_size)

    # the first block is initialization vector so we do not need to decode it
    decoded_cipher = bytearray()
    debug_print_title("BLOCK 1")
    debug_print_block_string("IV", cipher[0])

    # iterating over cipher starting from the second block
    previous_block = cipher[0]
    for index in range(1, len(cipher)):
        debug_print_title("BLOCK %d" % (index + 1))

        cipher_block = cipher[index]
        debug_print_block("C", cipher_block)

        # decoding current cipher block
        decoded_block = decode_block(cipher_block, oracle)

        # decoding plain text bytes by xoring decoded block with previous cipher block
        plain_decoded_block = xor(decoded_block, previous_block)
        debug_print_block_string("P", plain_decoded_block)

        # appending decoded plain text to decoded cipher
        decoded_cipher += plain_decoded_block

        # setting previous block for next iteration
        previous_block = cipher_block

    debug_print_title("DECODING COMPLETED")
    # converting decided cipher from bytearray to string
    return get_string(decoded_cipher, encoding)

def decode_block(block, is_valid):
    block_size = len(block)
    decoded_block = bytearray(block_size)

    debug_print_block("C1", decoded_block, with_newline=False)

    # iterating over every byte in block
    for position in range(0, block_size):
        found = False
        # checking all 256 byte values
        for byte_value in range(0, 256):
            # creating empty block C1 filled with zeros
            c1 = bytearray(block_size)

            # xoring every decoded byte with value of position + 1
            for i in range(0, position):
                index = block_size - position + i
                c1[index] = decoded_block[index] ^ position + 1

            # assigning currently checked value to position
            index = block_size - (position + 1)
            c1[index] = byte_value

            debug_update_last_block(c1)

            # building message from C1 and block that's being decoded
            message = get_hexstring(c1 + block)
            # asking oracle if padding is valid for built message
            if is_valid(message):
                # padding for guessed value is correct
                found = True
                # decoding value by xoring guessed byte with value of position + 1
                index = block_size - (position + 1)
                decoded_block[index] = byte_value ^ position + 1
                break
        if not found:
            # all byte combinations have been checked but oracle did not return if padding is correct for any
            raise Exception("Oracle could not determine if any of all byte combinations are correct")

    debug_print_message("")
    debug_print_block("I", decoded_block)
    return decoded_block
