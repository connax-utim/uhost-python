import logging
import time
import _thread
from ..utilities.tag import Tag
from ..utilities.cryptography import CryptoLayer
from ..utilities.constants import Status


class CommandWorkerConnectionStatusException(Exception):
    """
    Some exception of CommandWorkerConnectionStatus class
    """

    pass


class CommandWorkerConnectionStatus(object):
    """
    Connection Status command worker class
    """

    def __init__(self, uhost):
        """
        Initialization

        :param Uhost uhost: Uhost instance
        """

        self.__uhost = uhost  # Uhost instance

    def process(self, devid, data, outbound_queue, inbound_queue):
        """
        Run process

        :param str devid: Device ID
        :param bytes data: Data to process
        :param Queue outbound_queue: Outbound queue
        :param Queue inbound_queue: inbound queue
        """

        packet = None

        tag = data[0:1]
        length_bytes = data[1:3]
        length = int.from_bytes(length_bytes, byteorder='big', signed=False)
        value = data[3:3 + length]

        # Logging
        logging.debug('Tag1: %s', str(tag))
        logging.debug('Length1: %d', length)
        logging.debug('Value1: %s', [x for x in value])

        if length == len(value) and tag == Tag.UCOMMAND.CONNECTION_STRING:
            if value == Tag.UCOMMAND.CONNECTION_STRING_SUCCESS:
                logging.debug("RECEIVED CONNECTION STATUS: SUCCESS")
                session = self.__uhost.get_srp_session(devid)
                if not session.get('platform_verified'):
                    rand_data = session.get('test_data')
                    packet = Tag.UCOMMAND.assemble_test_platform_data(rand_data)
                    self.__uhost.save_dev_status(devid, Status.STATUS_TESTING)
                    # TODO Убрать костыль
                    key = self.__uhost.get_session_key(devid)
                    print(key)
                    crypto = CryptoLayer(key)
                    in_data = crypto.encrypt(CryptoLayer.CRYPTO_MODE_AES, data)
                    in_data = crypto.sign(CryptoLayer.SIGN_MODE_SHA1, in_data)
                    _thread.start_new_thread(self.repeat_status,
                                             (devid.encode(), in_data, inbound_queue, 5,))
                else:
                    logging.debug("Platform for %s already verified", devid)

            elif value == Tag.UCOMMAND.CONNECTION_STRING_ERROR:
                logging.debug("RECEIVED CONNECTION STATUS: ERROR")

            else:
                logging.debug("Connection status command worker error: Invalid status %s from %s",
                              str(data), devid)
        else:
            logging.debug("Connection status command worker error: Invalid data %s from %s",
                          str(data), devid)

        if packet is not None:
            topic = devid
            outbound_queue.put([topic, packet])

    def repeat_status(self, devid, data, in_queue, timeout=0):
        """
        Repeat status message

        :param bytes devid: UTIM ID
        :param bytes data: Data to send
        :param Queue in_queue: Queue to put
        :param int timeout: Timeout
        """

        time.sleep(timeout)
        in_queue.put([devid, data])
