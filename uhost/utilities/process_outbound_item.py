"""
Process outbound item
"""

import logging
from .cryptography import CryptoLayer
from .tag import Tag
from .database_connection import DataBaseConnection


class ProcessOutboundItem(object):
    """
    Process outbound item from queue class
    """

    NON_ENCRYPTED_COMMANDS = [Tag.UCOMMAND.TRY_FIRST, Tag.UCOMMAND.INIT]

    def __init__(self, uhost, outbound_queue, ready_to_send_queue):
        """
        Initialization
        """

        self.__uhost = uhost
        self.__outbound_queue = outbound_queue
        self.__rts_queue = ready_to_send_queue
        self.__database = DataBaseConnection()

    def is_queue_empty(self):
        """
        Check __inbound_data_queue is empty or not
        """

        return self.__outbound_queue.empty()

    def pull_single_item(self):
        """
        Get single item from __inbound_data_queue
        """

        if not self.is_queue_empty():
            return self.__outbound_queue.get()
        return None

    def process(self, outbound_data):
        """
        Process outbound item
        """

        devid = outbound_data[0]
        payload = outbound_data[1]

        logging.debug('processing item {}'.format(payload))

        key = None
        if payload[0:1] not in self.NON_ENCRYPTED_COMMANDS:
            key = self.__database.get_session_key(devid)
        crypto = CryptoLayer(key)
        payload = crypto.encrypt(CryptoLayer.CRYPTO_MODE_AES, payload)
        logging.debug('encrypted {}'.format(payload))
        payload = crypto.sign(CryptoLayer.SIGN_MODE_SHA1, payload)
        logging.debug('signed {}'.format(payload))

        self.__rts_queue.put([devid, payload])
