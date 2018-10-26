"""
Check command worker
"""

import logging
from ..utilities.tag import Tag


class CommandWorkerCheckException(Exception):
    """
    Some exception of CommandWorkerCheck class
    """

    pass


class CommandWorkerCheckUtimMethodException(Exception):
    """
    No Utim method exception of CommandWorkerCheck class
    """

    pass


class CommandWorkerCheck(object):
    """
    Check command worker class
    """

    TOPIC_TO_DS = 'to_DS/'
    TOPIC_TO_CLIENT = 'to_Client/'

    def __init__(self, uhost):
        """
        Initialization
        """

        # Check all necessary methods
        methods = [
            'get_srp_session',
            'remove_srp_session',
            'set_session_key'
        ]
        for method in methods:
            if not (hasattr(uhost, method) and callable(getattr(uhost, method))):
                raise CommandWorkerCheckUtimMethodException

        self.__uhost = uhost  # Uhost instance

    def process(self, devid, data, outbound_queue):
        """
        Run process
        """

        packet = None

        tag = data[0:1]
        length_bytes = data[1:3]
        length = int.from_bytes(length_bytes, byteorder='big', signed=False)
        value = data[3:3 + length]

        # Logging
        logging.debug('Tag: %s', str(tag))
        logging.debug('Length: %d', length)
        logging.debug('Value: %s', [x for x in value])

        if length == len(value) and tag == Tag.UCOMMAND.CHECK:
            session = self.__uhost.get_srp_session(devid)
            if session is None:
                packet = Tag.UCOMMAND.assemble_error(b"check no session")
            else:
                A = session.get('A')
                logging.debug("GET session A: %s", [x for x in A] if A is not None else 'None')
                svr = session.get('svr')
                if svr is None:
                    logging.error('svr is None')
                    packet = Tag.UCOMMAND.assemble_error(b"check svr none")

                else:
                    logging.debug("user M: %s", str(value))
                    logging.debug("self.M: %s", str(svr.M))
                    HAMK = svr.verify_session(value)
                    logging.debug("HAMK: %s", str(HAMK))
                    if HAMK is None:
                        logging.error('HAMK is None')
                        packet = Tag.UCOMMAND.assemble_error(b"check hamk none")

                    else:
                        # Save private key
                        key = svr.get_session_key()
                        self.__uhost.set_session_key(devid, key)

                        # Remove SRP session
                        self.__uhost.remove_srp_session(devid)

                        packet = Tag.UCOMMAND.assemble_init(HAMK)

        else:
            logging.debug("Invalid data %s from %s", [hex(x) for x in data], devid)
            packet = Tag.UCOMMAND.assemble_error(b"check invalid data")

        if packet is not None:
            topic = devid
            outbound_queue.put([topic, packet])
