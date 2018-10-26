"""
Encryption worker
"""

import logging
from ..utilities.cryptography import CryptoLayer


class CryptoWorkerEncryptException(Exception):
    """
    Some exception of CryptoWorkerEncrypt class
    """


class CryptoWorkerEncryptUhostMethodException(Exception):
    """
    No Utim method exception of CryptoWorkerEncrypt class
    """
    pass


class CryptoWorkerEncrypt(object):
    """
    Encryption worker
    """

    def __init__(self, uhost):
        """
        Initialization
        """

        # Check all necessary methods
        methods = ['get_session_key']
        for method in methods:
            if not (hasattr(uhost, method) and callable(getattr(uhost, method))):
                raise CryptoWorkerEncryptUhostMethodException

        self.__uhost = uhost  # Uhost instance

    def process(self, devid, data, outbound_queue):
        """
        Run process
        """

        try:
            crypto = CryptoLayer(self.__uhost.get_session_key(devid))
            logging.debug('Encrypting message {0} with key {1}'.format(data, self.__uhost.get_session_key(devid)))
            cipherdata = crypto.encrypt(CryptoLayer.CRYPTO_MODE_AES, data)
            logging.debug('Encrypted package: {0}'.format(cipherdata))
            outbound_queue.put([devid, cipherdata])
        except ValueError:
            logging.error('Error appeared in encrypting message')
            raise CryptoWorkerEncryptException
