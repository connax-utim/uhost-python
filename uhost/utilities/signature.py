"""
Signature module
"""

from hashlib import sha1
import hmac


class Signature(object):
    """
    Signature class
    """

    @staticmethod
    def create_signature(secret_key, message):
        """
        Create signature
        :param bytes secret_key:
        :param bytes message:
        :return: bytes
        """
        hashed = hmac.new(secret_key, message, sha1)
        return hashed.digest()

    def message_sign(self, key, message):
        """
        Sign message
        """

        signature = self.create_signature(key, message)
        return message, signature

    def authenticate_signed_token(self, message, signature, key):
        """
        Check sign
        """

        message, sign = self.message_sign(key, message)
        return True if signature == sign else False
