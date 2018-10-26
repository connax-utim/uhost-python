"""
Encryption worker
"""

import logging
from ..utilities.cryptography import CryptoLayer


class SignWorkerSignException(Exception):
    """
    Some exception of CryptoWorkerEncrypt class
    """


class SignWorkerSignUhostMethodException(Exception):
    """
    No Utim method exception of CryptoWorkerEncrypt class
    """
    pass


class SignWorkerSign(object):
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
                raise SignWorkerSignUhostMethodException

        self.__uhost = uhost  # Uhost instance

    def process(self, devid, data, outbound_queue):
        """
        Run process
        """

        try:
            crypto = CryptoLayer(self.__uhost.get_session_key(devid))
            logging.debug('Signing message {0} with key {1}'.format(data, self.__uhost.get_session_key(devid)))
            cipherdata = crypto.sign(CryptoLayer.SIGN_MODE_SHA1, data)
            logging.debug('Signed package: {0}'.format(cipherdata))
            outbound_queue.put([devid, cipherdata])
        except TypeError:
            logging.error('Error appeared in signing message')
            raise SignWorkerSignException
