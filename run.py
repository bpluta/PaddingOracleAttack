import decoder
import encoder

import pwn
import utils

pwn.context.log_level = 'error'

def is_valid(message):
     connection = pwn.remote('2018shell.picoctf.com', 24933)
     connection.recvuntil('What is your cookie?\n')
     connection.sendline(message)
     response = utils.get_string(connection.recvall())
     is_valid = False
     if response.find('invalid padding') == -1:
         is_valid = True
     connection.close()
     return is_valid

# Decryption
cipher = "5468697320697320616e204956343536d6ca0a2883280762915414c54e97df1b40871b72f45ec7f9510a080095436d514129e137aaac86a0f7fa8bd3d250b9d1df35b668fcb93f00bb06692560a3fed8a3b523d385f1477b6daac14ff2416c67"
decoded_message = decoder.decode_cipher(cipher, is_valid)
print(decoded_message)

# Encryption
message = '{"username": "hacker", "expires": "9999-12-31", "is_admin": "true"}'
encoded_message = encoder.encode_message(message, is_valid)
print(encoded_message)
