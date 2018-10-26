"""
Worker designed to process command "Trusted" - the final command arriving from Utim
at the moment it finishes it's initialization

Worker checks input parameters and if OK, it compares the sender's dev-id against Utim_name
and also checks if the Session key is set. If everything fine, it builds the message
to Client informing it about UTIM came up.

in case of input parameters are corrupted Worker reports an issue (in debug mode)
and discards the message

In case the "Trusted" command arrived but the session key for Utim isn't set for some reason
Worker builds the Error message to DS to be delivered to Utim.
"""

import logging
from ..utilities.tag import Tag
from ..utilities.constants import Status


class CommandWorkerTrustedException(Exception):
    """
    Some exception of CommandWorkerTrusted class
    """

    pass


class CommandWorkerTrustedUhostMethodException(Exception):
    """
    No Utim method exception of CommandWorkerTrusted class
    """

    pass


class CommandWorkerTrusted(object):
    """
    Hello command worker class
    """

    def __init__(self, uhost):
        """
        Initialization

        :param Uhost uhost: Uhost instance
        """

        # Check all necessary methods
        methods = [
            'save_dev_status'
        ]
        for method in methods:
            if not (hasattr(uhost, method) and callable(getattr(uhost, method))):
                raise CommandWorkerTrustedUhostMethodException

        self.__uhost = uhost  # Uhost instance

    def process(self, devid, data, outbound_queue):
        """
        Run process

        :param str devid: Device ID
        :param bytes data: Data to process
        :param Queue outbound_queue: Outbound queue
        """

        packet = None

        tag1 = data[0:1]
        length_bytes1 = data[1:3]
        length1 = int.from_bytes(length_bytes1, byteorder='big', signed=False)
        value1 = data[3:3 + length1]

        # Logging
        logging.debug('Tag1: %s', str(tag1))
        logging.debug('Length1: %d', length1)
        logging.debug('Value1: %s', [x for x in value1])

        if length1 == len(value1) and tag1 == Tag.UCOMMAND.TRUSTED:
            # final check if session key is stored
            session_key = self.__uhost.get_session_key(devid)
            if session_key is None:
                logging.debug("Trusted command worker error: received Ack from device %s,\
                    but there is no Session Key", devid)
                packet = Tag.UCOMMAND.assemble_error(b"trusted no Session Key")

            else:
                logging.debug("Trusted command worker: UTIM \'%s\' is ON", devid)
                self.__uhost.save_dev_status(devid, Status.STATUS_DONE)
                packet = Tag.UCOMMAND.assemble_authentic()

        else:
            logging.debug("Trusted command worker error: Invalid data %s from %s",
                          [hex(x) for x in data], devid)

        if packet is not None:
            topic = devid
            outbound_queue.put([topic, packet])
