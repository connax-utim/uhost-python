"""Cryptography layer for Utim and Uhost"""

from Crypto.Cipher import AES
import hashlib
import hmac
import logging
from .tag import Tag


class CryptoLayer(object):
    """
    Cryptography layer object
    """

    SIGN_MODE_NONE = b'\x00'
    SIGN_MODE_SHA1 = b'\x01'

    CRYPTO_MODE_NONE = b'\x00'
    CRYPTO_MODE_AES = b'\x01'

    __SIGN_SHA1_LENGTH = 20
    __iv = b'\x75\xbe\x38\x2b\x42\x51\xc7\x05\xa2\x43\x23\x5d\xe0\xf4\xb5\x08'

    def __init__(self, key):
        """
        Initialization of CryptoLayer
        For AES key must be 16, 24 or 32 bytes
        """
        logging.info('Creating new layer with key {0}'.format(key))
        self.__key = key

    @staticmethod
    def is_secured(message):
        """
        Is message secured
        """
        if message[0:1] == Tag.CRYPTO.ENCRYPTED:
            if message[1:2] != CryptoLayer.CRYPTO_MODE_NONE:
                return True
        elif message[0:1] == Tag.CRYPTO.SIGNED:
            if message[1:2] != CryptoLayer.SIGN_MODE_NONE:
                return True
        return False

    def encrypt(self, mode, message):
        """
        Encrypt message
        """
        if self.__key is not None and mode != self.CRYPTO_MODE_NONE:
            if mode == self.CRYPTO_MODE_AES:
                cipher = AES.new(self.__key, AES.MODE_CFB, self.__iv)
                return Tag.CRYPTO.ENCRYPTED + mode + cipher.encrypt(message)
        return Tag.CRYPTO.ENCRYPTED + self.CRYPTO_MODE_NONE + message

    def decrypt(self, message):
        """
        Decrypt message
        """
        if len(message) < 2:
            return None
        if self.__key is None:
            if message[1:2] == self.CRYPTO_MODE_NONE:
                return message[2:]
        elif message[1:2] == self.CRYPTO_MODE_AES:
            cipher = AES.new(self.__key, AES.MODE_CFB, self.__iv)
            return cipher.decrypt(self.__iv + message[2:])[16:]
        return None

    def sign(self, mode, message):
        """
        Sign message
        """
        if self.__key is not None and mode != self.SIGN_MODE_NONE:
            if mode == self.SIGN_MODE_SHA1:
                signature = hmac.new(self.__key, message, hashlib.sha1).digest()
                return Tag.CRYPTO.SIGNED + mode + message + signature
        return Tag.CRYPTO.SIGNED + self.SIGN_MODE_NONE + message

    def unsign(self, message):
        """
        Unsign message
        """
        if len(message) < 2:
            return None
        if self.__key is None:
            if message[1:2] == self.SIGN_MODE_NONE:
                return message[2:]
        elif message[1:2] == self.SIGN_MODE_SHA1:
            # message end is full length minus signature length
            message_end = len(message) - self.__SIGN_SHA1_LENGTH
            useful_message = message[2:message_end]
            signature = message[message_end:]
            ref_signature = hmac.new(self.__key, useful_message, hashlib.sha1).digest()
            if signature == ref_signature:
                return useful_message
        return None
