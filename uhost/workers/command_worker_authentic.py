"""
The command worker
"""

import logging
from ..utilities.tag import Tag
from ..utilities.constants import Status


class CommandWorkerAuthenticException(Exception):
    """
    Some exception of CommandWorkerAuthentic class
    """

    pass


class CommandWorkerAuthenticMethodException(Exception):
    """
    No Uhost method exception of CommandWorkerAuthentic class
    """

    pass


class CommandWorkerAuthentic(object):
    """
    Connection command worker class
    """

    def __init__(self, uhost):
        """
        Initialization
        """

        self.__uhost = uhost

    def process(self, devid, data, outbound_queue):
        """
        Run  process 
        """

        tag = data[0:1]
        length_bytes = data[1:3]
        length = int.from_bytes(length_bytes, byteorder='big', signed=False)
        value = data[3:3 + length]

        # Logging
        logging.debug('Tag: %s', str(tag))
        logging.debug('Length: %d', length)
        logging.debug('Value: %s', [x for x in value])

        if length == len(value) and tag == Tag.UCOMMAND.VERIFIED:
            pass

        packet = Tag.UCOMMAND.assemble_authentic()

        self.__uhost.save_dev_status(devid, Status.STATUS_DONE)

        if packet is not None:
            topic = devid
            outbound_queue.put([topic, packet])
