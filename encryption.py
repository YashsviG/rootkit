import random
import string

def generate_key():
    letters = string.ascii_letters
    key = bytes(''.join(random.choice(letters) for _ in range(2)), 'ascii')
    print(f"----------KEY GENERATED: {key}----------")
    return key

def xor_encrypt_decrypt(data_byte: int, key_bytes: bytes):
    """
    Performs XOR encryption on a single byte of data using a 2-byte key.
    :param data_byte: The byte of data to encrypt.
    :param key_bytes: The 2-byte encryption key.
    :return: The encrypted byte.
    """
    data_byte = data_byte.to_bytes(1, byteorder='big')
    if len(key_bytes) != 2:
        raise ValueError("Key must be 2 bytes (16 bits)")
    
    key = key_bytes * (len(data_byte) // 2) + key_bytes[:len(data_byte) % 2]
    encrypted_byte = bytes([data_byte[i] ^ key[i] for i in range(len(data_byte))])
    return int.from_bytes(encrypted_byte, 'big')