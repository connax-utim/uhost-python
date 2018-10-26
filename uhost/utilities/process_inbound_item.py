"""
Process item from queue module
"""

import logging
from .tag import Tag
from .cryptography import CryptoLayer
from ..workers.command_worker_check import CommandWorkerCheck
from ..workers.command_worker_cleanup import CommandWorkerCleanup
from ..workers.command_worker_for_signature import CommandWorkerForSignature
from ..workers.command_worker_hello import CommandWorkerHello
from ..workers.command_worker_signed import CommandWorkerSigned
from ..workers.command_worker_trusted import CommandWorkerTrusted
from ..workers.command_worker_authentic import CommandWorkerAuthentic
from ..workers.command_worker_connection_status import CommandWorkerConnectionStatus
from ..workers.command_worker_keepalive import CommandWorkerKeepalive


class ProcessInboundItemException(Exception):
    """
    Some exception of ProcessInboundItem class
    """

    pass


class ProcessInboundItemTlvLengthException(ProcessInboundItemException):
    """
    Wrong number of elements in TLV data
    """

    pass


class ProcessInboundItemTlvTypeException(ProcessInboundItemException):
    """
    Wrong element types in TLV data
    """

    pass


class ProcessInboundItemUtimMethodException(ProcessInboundItemException):
    """
    No Utim method exception of ProcessInboundItem class
    """

    pass


class ProcessInboundItem(object):
    """
    Process item from queue class
    """

    TLV_DATA_LENGTH = 2

    def __init__(self, uhost, inbound_queue, outbound_queue):
        """
        Initialization
        """

        self.__uhost = uhost  # Utim instance
        self.__inbound_data_queue = inbound_queue  # Queue to get item
        self.__outbound_data_queue = outbound_queue  # Queue to put item

        # Init workers
        self.__check_worker = CommandWorkerCheck(uhost)
        self.__cleanup_worker = CommandWorkerCleanup(uhost)
        self.__for_signature_worker = CommandWorkerForSignature(uhost)
        self.__hello_worker = CommandWorkerHello(uhost)
        self.__signed_worker = CommandWorkerSigned(uhost)
        self.__trusted_worker = CommandWorkerTrusted(uhost)
        self.__authentic_worker = CommandWorkerAuthentic(uhost)
        self.__connection_status_worker = CommandWorkerConnectionStatus(uhost)
        self.__keepalive_worker = CommandWorkerKeepalive(uhost)

    def is_queue_empty(self):
        """
        Check __inbound_data_queue is empty or not
        """

        return self.__inbound_data_queue.empty()

    def pull_single_item(self):
        """
        Get single item from __inbound_data_queue
        """

        if not self.is_queue_empty():
            return self.__inbound_data_queue.get()

        return None

    def __check_tlv_data(self, tlv_data):
        """
        Check tlv data
        """

        tlv_data_length = len(tlv_data)
        if tlv_data_length == self.TLV_DATA_LENGTH:
            flag_invalid = False

            # Check topic (bytes)
            topic = tlv_data[0]
            if not isinstance(topic, bytes):
                logging.error("Invalid type of topic: %s", type(topic))
                flag_invalid = True

            # Check payload (bytes)
            payload = tlv_data[1]
            if not isinstance(payload, bytes):
                logging.error("Invalid type of payload: %s", type(payload))
                flag_invalid = True

            if flag_invalid:
                raise ProcessInboundItemTlvTypeException
        else:
            logging.error("Invalid number of elements: %d", tlv_data_length)
            raise ProcessInboundItemTlvLengthException

    def run_worker(self, tlv_data):
        """
        Run worker to process data
        """

        # Check tlv_data
        try:
            self.__check_tlv_data(tlv_data)
        except ProcessInboundItemTlvLengthException:
            logging.error("Invalid TLV length exception")
            return
        except ProcessInboundItemTlvTypeException:
            logging.error("Invalid TLV type exception")
            return

        devid = tlv_data[0].decode()
        payload = tlv_data[1]
        flag_encrypted = False
        crypto = None

        if CryptoLayer.is_secured(payload):
            flag_encrypted = True
            crypto = CryptoLayer(self.__uhost.get_session_key(devid))
        else:
            crypto = CryptoLayer(None)

        if payload is not None:
            payload = crypto.unsign(payload)
        if payload is not None:
            payload = crypto.decrypt(payload)

        # Logging data to process
        logging.debug("Topic: %s", str(devid))
        logging.debug("Payload: %s", str(payload))

        if payload is not None:

            # Check utim name (devid) is valid or not
            if devid in self.__uhost.database.get_utim_names():
                # Get tag
                tag = payload[0:1]

                if tag == Tag.UCOMMAND.HELLO:
                    self.__hello_worker.process(devid, payload, self.__outbound_data_queue)

                elif tag == Tag.UCOMMAND.CHECK:
                    self.__check_worker.process(devid, payload, self.__outbound_data_queue)

                elif tag == Tag.UCOMMAND.TRUSTED and flag_encrypted:
                    self.__trusted_worker.process(devid, payload, self.__outbound_data_queue)

                elif tag == Tag.UCOMMAND.SIGNED and flag_encrypted:
                    self.__signed_worker.process(devid, payload, self.__outbound_data_queue)

                elif tag == Tag.UCOMMAND.VERIFIED and flag_encrypted:
                    self.__authentic_worker.process(devid, payload, self.__outbound_data_queue)

                elif tag == Tag.UCOMMAND.CONNECTION_STRING and flag_encrypted:
                    self.__connection_status_worker.process(devid, payload, self.__outbound_data_queue,
                                                            self.__inbound_data_queue)

                elif tag == Tag.UCOMMAND.KEEPALIVE_ANSWER and flag_encrypted:
                    self.__keepalive_worker.process(devid, payload, self.__outbound_data_queue)

                else:
                    self.__cleanup_worker.process(devid, payload, self.__outbound_data_queue)

            else:
                logging.debug("Invalid utim name: %s", devid)

        else:
            logging.debug("There was a critical flaw in message")
