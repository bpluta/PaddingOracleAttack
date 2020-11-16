import struct
import sys

DEFAULT_BLOCK_SIZE = 16
DEFAULT_ENCODING = 'utf-8'

PRINT_DEBUG = True
PRINT_OFFSET = 5

def plaintext_to_blocks(plaintext, block_size=DEFAULT_BLOCK_SIZE, encoding=DEFAULT_ENCODING):
    raw_text = bytearray(plaintext, encoding)
    if is_padded(raw_text, block_size):
        padded_message = raw_text
    else:
        padded_message = pad_message(raw_text, block_size)
    return divide_raw_message_to_blocks(padded_message, block_size)

def pad_message(raw_message, block_size=DEFAULT_BLOCK_SIZE):
    padding_value = block_size - len(raw_message) % block_size
    return raw_message + struct.pack("b", padding_value) * padding_value

def is_padded(raw_message, block_size=DEFAULT_BLOCK_SIZE):
    if len(raw_message) % block_size != 0:
        return False
    padding_value = raw_message[-1]
    if padding_value < 1 or padding_value > padding_value:
        return False
    padding_section = raw_message[-padding_value:]
    for character in padding_section:
        if character != padding_value:
            return False
    return True

def divide_raw_message_to_blocks(raw_message, block_size=DEFAULT_BLOCK_SIZE):
    if len(raw_message) % block_size != 0:
        raise Exception("Message is not aligned to block size")
    amount_of_blocks = len(raw_message) // block_size
    return [raw_message[i*block_size: (i+1)*block_size] for i in range(0, amount_of_blocks)]

def get_hexstring(bytes):
    return "".join(['{:02x}'.format(byte) for byte in bytes])

def get_string(bytes, encoding=DEFAULT_ENCODING):
    return bytes.decode(encoding=encoding, errors='ignore')

def get_byte_blocks(hexstring, block_size=DEFAULT_BLOCK_SIZE):
    if len(hexstring) % (block_size * 2) != 0:
        raise Exception("Hex string is not aligned to multiple of block size")
    hex_block_size = block_size * 2
    amount_of_blocks = len(hexstring) // hex_block_size
    byte_blocks = [hexstring[i*hex_block_size: (i+1)*hex_block_size] for i in range(0, amount_of_blocks)]
    return [bytearray.fromhex(byte_blocks[i]) for i in range(0, len(byte_blocks))]

def xor(first, second):
    return bytearray([a ^ b for (a,b) in zip(first, second)])

def debug_print_message(message="", with_newline=True, with_flush=False):
    if PRINT_DEBUG:
        if with_newline:
            message += "\n"
        sys.stdout.write(message)
        if with_flush:
            sys.stdout.flush()

def debug_print_block(name, block, with_newline=True, with_flush=False):
    message = "%s:" % name + " " * (PRINT_OFFSET - (len(name)+1)) + get_hexstring(block)
    debug_print_message(message, with_newline=with_newline, with_flush=with_flush)

def debug_print_block_string(name, block, with_newline=True, with_flush=False):
    message = "%s:" % name + " " * (PRINT_OFFSET - (len(name)+1)) + repr(get_string(block))
    debug_print_message(message, with_newline=with_newline, with_flush=with_flush)

def debug_update_last_block(block):
    message = "\033[%dD%s" % ((len(block) * 2), get_hexstring(block))
    debug_print_message(message, with_newline=False, with_flush=True)

def debug_print_title(title_message, block_size=DEFAULT_BLOCK_SIZE, with_flush=False):
    title = " %s " % title_message
    prefix_offset = (block_size * 2 - len(title)) // 2
    suffix_offset = block_size * 2 - (prefix_offset + len(title))
    message = " " * PRINT_OFFSET + "=" * prefix_offset + title + "=" * suffix_offset
    debug_print_message(message, with_flush=with_flush)
