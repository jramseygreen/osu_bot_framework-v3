from Crypto import Random
from Crypto.Cipher import AES
import base64
from hashlib import md5

BLOCK_SIZE = 16


class CryptoWrapper:
    def __init__(self, password):
        self.__password = password.encode()

    def __pad(self, data):
        length = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
        return data + (chr(length) * length).encode()

    def __unpad(self, data):
        return data[:-(data[-1] if type(data[-1]) == int else ord(data[-1]))]

    def __bytes_to_key(self, data, salt, output=48):
        # extended from https://gist.github.com/gsakkis/4546068
        assert len(salt) == 8, len(salt)
        data += salt
        key = md5(data).digest()
        final_key = key
        while len(final_key) < output:
            key = md5(key + data).digest()
            final_key += key
        return final_key[:output]

    def encrypt(self, message):
        message = message.encode()
        salt = Random.new().read(8)
        key_iv = self.__bytes_to_key(self.__password, salt, 32 + 16)
        key = key_iv[:32]
        iv = key_iv[32:]
        aes = AES.new(key, AES.MODE_CBC, iv)
        return base64.b64encode(b"Salted__" + salt + aes.encrypt(self.__pad(message))).decode()

    def decrypt(self, encrypted):
        decrypted = None
        try:
            encrypted = base64.b64decode(encrypted)
            assert encrypted[0:8] == b"Salted__"
            salt = encrypted[8:16]
            key_iv = self.__bytes_to_key(self.__password, salt, 32 + 16)
            key = key_iv[:32]
            iv = key_iv[32:]
            aes = AES.new(key, AES.MODE_CBC, iv)
            decrypted = self.__unpad(aes.decrypt(encrypted[16:])).decode()
        except:
            pass
        return decrypted

    def set_password(self, password):
        self.__password = password.encode()

    def get_password(self):
        return self.__password.decode()
