"""
Command Worker designed to sign messages arriving from Clients via mqtt.

The Worker verifies the input data: the device-id should have the correct length and tries to sign
the message.

On case of success it builds the message with a destination "to_DS" and puts it into outbound queue

"""

import logging
from ..utilities.tag import Tag


class CommandWorkerForSignatureException(Exception):
    """
    Some exception of CommandWorkerForSignature class
    """

    pass


class CommandWorkerForSignatureMethodException(Exception):
    """
    No Uhost method exception of CommandWorkerForSignature class
    """

    pass


class CommandWorkerForSignature(object):
    """
    for_Signature command worker class
    """
    DEVID_LENGTH = 24  # expected length of dev-id in char mode (when receiving it from mqtt topic)

    def __init__(self, uhost):
        """
        Initialization
        """

        # Check all necessary methods
        methods = [
            'encrypt'
        ]
        for method in methods:
            if not (hasattr(uhost, method) and callable(getattr(uhost, method))):
                raise CommandWorkerForSignatureMethodException

        self.__uhost = uhost  # Uhost instance

    def process(self, devid, data, outbound_queue):
        """
        Run process
        """

        logging.debug("Command Worker for_Signature. Trying to sign message: %s for device: %s ",
                      [hex(x) for x in data], devid)

        # checking devid length
        devid_length = len(devid)

        # Logging
        logging.debug('Data: %s', [x for x in data])

        # Check real data length
        if devid_length == self.DEVID_LENGTH:

            message, signature = self.__uhost.encrypt(data, devid)

            if message is not None and signature is not None:
                logging.debug("Signed message: %s %s", [x for x in message], [x for x in signature])
                packet = ['to_DS/' + devid, Tag.UCOMMAND.assemble_signed(message, signature)]
                outbound_queue.put(packet)

            else:
                logging.debug('Command_worker_for_Signature: failed to encrypt message')

        else:
            logging.debug('Command_worker_for_Signature: Invalid input data')
