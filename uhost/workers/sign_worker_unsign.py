"""
Encryption worker
"""

import logging
from ..utilities.cryptography import CryptoLayer


class SignWorkerUnsignException(Exception):
    """
    Some exception of CryptoWorkerEncrypt class
    """


class SignWorkerUnsignUhostMethodException(Exception):
    """
    No Utim method exception of CryptoWorkerEncrypt class
    """
    pass


class SignWorkerUnsign(object):
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
                raise SignWorkerUnsignUhostMethodException

        self.__uhost = uhost  # Uhost instance

    def process(self, devid, data, outbound_queue):
        """
        Run process
        """

        try:
            crypto = CryptoLayer(self.__uhost.get_session_key(devid))
            logging.debug('Unsigning package {0} with key {1}'.format(data, self.__uhost.get_session_key(devid)))
            message = crypto.unsign(data)
            logging.debug('Unsigned message: {0}'.format(message))
            outbound_queue.put([devid, message])
        except TypeError:
            logging.error('Error appeared in unsigning message')
            raise SignWorkerUnsignException
