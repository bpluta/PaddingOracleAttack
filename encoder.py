from decoder import *
from utils import *

def encode_message(message_to_encode, oracle, block_size=DEFAULT_BLOCK_SIZE, encoding=DEFAULT_ENCODING):
    debug_print_title("ENCODING MESSAGE")

    # converting plaintext to bytearray blocks
    message_blocks = plaintext_to_blocks(message_to_encode, block_size, encoding)

    # the last block of encoded message is arbitrary - it can be anything
    arbitrary_block = message_blocks[0]
    encoded_message = arbitrary_block
    current_block = arbitrary_block

    # iterating over reversed blocks with message
    for index in range(len(message_blocks)-1,-1,-1):
        debug_print_title("BLOCK %d" % (index + 1))

        plaintext_block = message_blocks[index]

        # decoding current message block
        decoded_block = decode_block(current_block, oracle)

        # ecoding block by xoring decoded form with its initial raw form
        previous_block = xor(plaintext_block, decoded_block)
        debug_print_block("C", previous_block)

        # appending block to the beggining of message
        encoded_message = previous_block + encoded_message

        # setting current block to encoded block for next iteration
        current_block = previous_block

    debug_print_title("ENCODING COMPLETED")
    # convertinf encoded message from bytearray to hex string
    return get_hexstring(encoded_message)
