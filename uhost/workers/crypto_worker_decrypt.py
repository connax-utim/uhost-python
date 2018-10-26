"""
Encryption worker
"""

import logging
from ..utilities.cryptography import CryptoLayer


class CryptoWorkerDecryptException(Exception):
    """
    Some exception of CryptoWorkerEncrypt class
    """


class CryptoWorkerDecryptUhostMethodException(Exception):
    """
    No Utim method exception of CryptoWorkerEncrypt class
    """
    pass


class CryptoWorkerDecrypt(object):
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
                raise CryptoWorkerDecryptUhostMethodException

        self.__uhost = uhost  # Uhost instance

    def process(self, devid, data, outbound_queue):
        """
        Run process
        """

        try:
            crypto = CryptoLayer(self.__uhost.get_session_key(devid))
            logging.debug('Decrypting package {0} with key {1}'.format(data, self.__uhost.get_session_key(devid)))
            message = crypto.decrypt(data)
            logging.debug('Decrypted message: {0}'.format(message))
            outbound_queue.put([devid, message])
        except ValueError:
            logging.error('Error appeared in encrypting message')
            raise CryptoWorkerDecryptException
