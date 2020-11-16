import decoder
import encoder

def is_valid(message):
    # This method should send message to our oracle
    # Basing on given response it should return True if the message has been decrypted correctly
    # or False if it could not be decoded (or returned invalid padding message)
    raise Exception("Unimplemented oracle!")

# Decryption
cipher = "" # cipher we want to decrypt
decoded_message = decoder.decode_cipher(cipher, is_valid)
print(decoded_message)

# Encryption
message = "" # message we want to encrypt
encoded_message = encoder.encode_message(message, is_valid)
print(encoded_message)
