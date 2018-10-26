"""
Uhost main module
"""

import _thread
import hashlib
import json
import logging
import queue
import time
import os
from .utilities import process_inbound_item, signature, srp, process_outbound_item, uhost_connection, keepalive_manager
from .utilities.database_connection import DataBaseConnection
from .utilities.config import Config
from .utilities.exceptions import UtimInitializationError


class Uhost(object):
    """
    Uhost class
    """

    def __init__(self):
        """
        Initialization
        """

        # Check master key
        self.__get_master_key()

        self.__config = Config()

        self.__name = bytes.fromhex(self.__config.uhost_name)

        # Inbound queue
        self.__inbound_queue = queue.Queue()

        # Outbound queue
        self.__outbound_queue = queue.Queue()

        # Database connection
        self.database = DataBaseConnection(init_db=True)

        # MQTT connection
        self.__connection = uhost_connection.UhostConnection('mqtt', self.__inbound_queue)

        # Keepaliver
        self.__keepalive_manager = keepalive_manager.KeepaliveManager(self.__outbound_queue)

        # Running main loop flag
        self.__running = False

        # SRP client sessions
        self.__sessions = []

        # Process Items
        self.__item_process = process_inbound_item.ProcessInboundItem(
            self, self.__inbound_queue, self.__outbound_queue
        )

        self.__out_process = process_outbound_item.ProcessOutboundItem(
            self, self.__outbound_queue, self.__connection.outbound_queue
        )

    @staticmethod
    def __get_master_key():
        """
        Get master key
        """

        try:
            key = os.environ.get('UHOST_MASTER_KEY', None)
            return bytes.fromhex(key)

        except TypeError as ex:
            logging.debug(ex)
            raise UtimInitializationError

    def get_srp_session(self, utim_name):
        """
        Get SRP session
        """

        session = None

        if utim_name is not None:
            session = next((item for item in self.__sessions if item['utimname'] == utim_name),
                           None)

            if session is None:
                # Remove old sessions of the utim_name
                self.remove_srp_session(utim_name)

                # Get salt, vkey from SRP
                username = bytes.fromhex(utim_name)
                password = self.__get_master_key()
                logging.debug("Username: %s", [x for x in username])
                logging.debug("Password: %s", [x for x in password])
                salt, vkey = srp.create_salted_verification_key(username, password)

                # Create session
                session = {
                    'utimname': utim_name,
                    'salt': salt,
                    'vkey': vkey,
                    'A': None,
                    'svr': None,
                    'test_data': b'testovaya_stroka',  # TODO: os.urandom(32),
                    'platform_verified': False
                }

                # Save server session with the utim name (utim_name)
                self.__sessions.append(session)

        return session

    def set_srp_session(self, utim_name, session):
        """
        Set SRP session
        """

        # Remove old sessions of the utim_name
        self.remove_srp_session(utim_name)

        # Add new session
        self.__sessions.append(session)

    def remove_srp_session(self, utim_name):
        """
        Remove SRP session
        """

        # Remove session of the utim_name
        self.__sessions[:] = [d for d in self.__sessions if d.get('utimname') != utim_name]

    def __process_item(self):
        """
        Process UHOST data
        """

        while self.__running:
            if not self.__item_process.is_queue_empty():
                data = self.__item_process.pull_single_item()
                self.__item_process.run_worker(data)

    def __process_out(self):
        """
        Process out data
        """

        while self.__running:
            if not self.__out_process.is_queue_empty():
                data = self.__out_process.pull_single_item()
                self.__out_process.process(data)

    def run(self):
        """
        Run Utim
        """

        # Run main loop
        self.__running = True

        # Run UHost MQTT
        self.__connection.run()

        # Run keepaliver
        self.__keepalive_manager.run()

        # Run thread for item processing
        _thread.start_new_thread(self.__process_item, ())

        # Run thread for out processin
        _thread.start_new_thread(self.__process_out, ())

        logging.info("Uhost \'%s\' works!", self.__name)

        self.__generate_utim_config()

        while self.__running:
            time.sleep(1)

    def __generate_utim_config(self):
        """
        Generate Utim config file
        """

        print("""
        ########################################################
        
        Use this configuration to start Utim:
        
        UHOST_NAME={uhost_name}
        MASTER_KEY={mk}
        MESSAGING_PROTOCOL={protocol}
        MESSAGING_HOSTNAME={msg_host}
        MESSAGING_USERNAME={msg_user}
        MESSAGING_PASSWORD={msg_pass}
        
        NOTE: UHOST_NAME and MASTER_KEY are in hex format
        
        ########################################################
        """.format(
            uhost_name=self.__config.uhost_name,
            mk=self.__get_master_key().hex(),
            protocol=self.__config.uhost_messaging_protocol,
            msg_host=self.__config.messaging_hostname,
            msg_user=self.__config.messaging_username,
            msg_pass=self.__config.messaging_password
        ))

    def stop(self):
        """
        Stop Utim
        """

        # Stop main loop
        self.__running = False

        # Stop serial exchange
        self.__connection.disconnect()

    def get_session_key(self, utim_name):
        """
        Get session key
        """
        logging.debug('GET SESSION KEY ========================================')
        session_key = self.database.get_session_key(utim_name)
        logging.debug("Name: %s", utim_name)
        logging.debug("Session key: %s", session_key)
        return session_key

    def set_session_key(self, utim_name, key):
        """
        Set session key
        """
        if isinstance(key, bytes) and isinstance(utim_name, str):
            logging.debug("KEY STR: %s TYPE NAME: %s NAME: %s", key, type(utim_name), utim_name)
            self.database.set_session_key(utim_name, key)

    def encrypt(self, out_message, dev_id):
        """
        Encrypt message
        """

        logging.debug("devid: %s", dev_id)
        key = self.get_session_key(dev_id)
        logging.debug("Key: %s", key)

        if out_message and key:
            return signature.Signature().message_sign(key, out_message)
        return None, None

    def decrypt(self, utim_name, in_message, in_signature):
        """
        Decrypt message
        """

        return self.__decrypt_pk(utim_name, in_message, in_signature)

    def __decrypt_pk(self, utim_name, in_message, in_signature):
        """
        Decrypt message with session (private) key
        """

        # TODO:
        # Check session key
        session_key = self.get_session_key(utim_name)
        if session_key is None:
            logging.debug("No session key fo data: %s", in_message)
            return None

        # Split message [data, signature]
        if in_message is not None and in_signature is not None:
            if signature.Signature().authenticate_signed_token(in_message, in_signature,
                                                               session_key):
                logging.debug("Successfully decrypted")
                return in_message

            logging.debug("Failed decrypted")
            return None

        logging.debug("Message or/and Signature is None")
        return None

    def save_dev_status(self, devid, status):
        """
        Save device status

        :param str devid: Device ID
        :param Status status: Device status
        """
        self.database.set_status(devid, status)

    @staticmethod
    def config_hash(config):
        if config is None or config.get('type') is None:
            return 'nothing'
        sha = hashlib.sha256()
        sha.update(json.dumps(config).encode())
        return sha.digest().hex()
