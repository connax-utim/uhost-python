"""
Hello command worker
"""

import logging
from ..utilities.tag import Tag
from ..utilities import srp
from ..utilities.constants import Status


class CommandWorkerHelloException(Exception):
    """
    Some exception of CommandWorkerHello class
    """

    pass


class CommandWorkerHelloUtimMethodException(Exception):
    """
    No Utim method exception of CommandWorkerHello class
    """

    pass


class CommandWorkerHello(object):
    """
    Hello command worker class
    """

    def __init__(self, uhost):
        """
        Initialization
        """

        # Check all necessary methods
        methods = [
            'get_srp_session',
            'set_srp_session',
            'remove_srp_session',
            'save_dev_status'
        ]
        for method in methods:
            if not (hasattr(uhost, method) and callable(getattr(uhost, method))):
                raise CommandWorkerHelloUtimMethodException

        self.__uhost = uhost  # Uhost instance

    def process(self, devid, data, outbound_queue):
        """
        Run process
        """

        packet = None
        packet_backend = None

        tag = data[0:1]
        length_bytes = data[1:3]
        length = int.from_bytes(length_bytes, byteorder='big', signed=False)
        value = data[3:3 + length]

        # Logging
        logging.debug('Tag: %s', str(tag))
        logging.debug('Length: %d', length)
        logging.debug('Value: %s', [x for x in value])

        if length == len(value) and tag == Tag.UCOMMAND.HELLO:
            # Get session values
            session = self.__uhost.get_srp_session(devid)
            A = session.get('A')
            logging.debug("GET session A: %s", [x for x in A] if A is not None else 'None')
            if A != value:
                logging.debug("Remove session")
                # Remove old sessions of utim_name
                self.__uhost.remove_srp_session(devid)
                # Get session values
                session = self.__uhost.get_srp_session(devid)
                A = session.get('A')
                logging.debug("GET session A after remove: %s",
                              [x for x in A] if A is not None else 'None')

            # Get salt, vkey from SRP
            salt = session.get('salt')
            vkey = session.get('vkey')
            svr = session.get('svr')

            logging.debug("Verifier params [username: %s, salt: %s, vkey: %s, A: %s", str(devid),
                          str(salt), str(vkey), str(value))
            if svr is None:
                logging.debug("SVR is None")
                svr = srp.Verifier(bytes.fromhex(devid), salt, vkey, value)

            s, B = svr.get_challenge()
            if s is None or B is None:
                logging.error('Challenge is None. s: %s, B: %s', str(s), str(B))
                packet = Tag.UCOMMAND.assemble_error(b"hello no challenge")

            else:
                logging.debug('Challenge s: %s, B: %s', [x for x in s], [x for x in B])

                # Remove old sessions of utim_name
                self.__uhost.remove_srp_session(bytes.fromhex(devid))

                logging.debug("SAVE A: %s", [x for x in value])
                # Save session values
                session = {
                    'utimname': devid,
                    'salt': salt,
                    'vkey': vkey,
                    'A': value,
                    'svr': svr,
                    'test_data': session.get('test_data'),
                    'platform_verified': session.get('platform_verified')
                }
                self.__uhost.set_srp_session(devid, session)

                logging.debug("self.M: %s", str(svr.M))
                session = self.__uhost.get_srp_session(devid)
                svr1 = session.get('svr')
                logging.debug("self1.M: %s", str(svr1.M) if svr1 else None)

                packet = Tag.UCOMMAND.assemble_try(s, B)

                self.__uhost.database.set_keep_alive_counter(devid, 0)
                self.__uhost.save_dev_status(devid, Status.STATUS_SRP)

        else:
            logging.debug("Invalid data %s from %s", [hex(x) for x in data], devid)
            packet = Tag.UCOMMAND.assemble_error(b"hello invalid data")

        if packet is not None:
            outbound_queue.put([devid, packet])
