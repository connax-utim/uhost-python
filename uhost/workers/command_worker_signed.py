"""
The command worker for Signed Tag. Designed to process incoming signed messages from UTIM.

It checks the input data structure (should contain two TLV elements: message and signature)
and verifies elements lengths. In case everything is correct it calls uHost's decrypt()
method and passing there the dev-id of the UTIM which has sent the message,
the message itself and the signature.

In case the signature verification was successful, the Worker builds the package addressed to_Client
and puts it into the outbound queue.

In case the input data structure is corrupted or signature verification failed, the Worker
reports an issue (in debug mode) and discards the message.

"""

import logging
from ..utilities.tag import Tag
from ..utilities.length import Length


class CommandWorkerSignedException(Exception):
    """
    Some exception of CommandWorkerSigned class
    """

    pass


class CommandWorkerSignedMethodException(Exception):
    """
    No Utim method exception of CommandWorkerSigned class
    """

    pass


class CommandWorkerSigned(object):
    """
    Signed command worker class
    """

    def __init__(self, uhost):
        """
        Initialization
        """

        # Check all necessary methods
        methods = [
            'decrypt'
        ]
        for method in methods:
            if not (hasattr(uhost, method) and callable(getattr(uhost, method))):
                raise CommandWorkerSignedMethodException

        self.__uhost = uhost  # Uhost instance

    def process(self, devid, data, outbound_queue):
        """
        Run process
        """

        logging.debug("Command Worker Signed. Trying to verify signature of %s : %s",
                      [hex(x) for x in data], [hex(x) for x in data])

        tag1 = data[0:1]
        length_bytes1 = data[1:3]
        length1 = int.from_bytes(length_bytes1, byteorder='big', signed=False)
        value1 = data[3:3 + length1]
        tag2 = data[3 + length1:4 + length1]
        length_bytes2 = data[4 + length1: 6 + length1]
        length2 = int.from_bytes(length_bytes2, byteorder='big', signed=False)
        value2 = data[6 + length1:6 + length1 + length2]

        # Logging
        logging.debug('Tag1: %s', str(tag1))
        logging.debug('Length1: %d', length1)
        logging.debug('Value1: %s', [x for x in value1])
        logging.debug('Tag2: %s', str(tag2))
        logging.debug('Length2: %d', length2)
        logging.debug('Value2: %s', [x for x in value2])

        # Check real data length
        if (length1 == len(value1) and tag1 == Tag.UCOMMAND.SIGNED and
                length2 == len(value2) and tag2 == Tag.UCOMMAND.SIGNATURE and
                length2 == Length.UCOMMAND.SIGNATURE):

            unsigned_message = self.__uhost.decrypt(devid, value1, value2)

            if unsigned_message is not None:
                logging.debug("Unsigned message: %s", [x for x in unsigned_message])
                packet = ['to_Client/' + devid, unsigned_message]
                outbound_queue.put(packet)

            else:
                logging.debug('Command_worker_signed: failed to decrypt message')

        else:
            logging.debug('Command_worker_signed: Invalid input data')
