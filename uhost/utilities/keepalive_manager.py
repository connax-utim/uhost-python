"""
Keepalive manager module
"""

import time
import _thread
import logging
from .tag import Tag
from .constants import Status
from .database_connection import DataBaseConnection


class KeepaliveManager(object):
    """
    This class will do stuff with Utims
    """

    def __init__(self, out_queue):
        logging.debug('init Keepalive Manager...')
        self.__connection = None
        self.__outbound_queue = out_queue
        self.__running = False

    def run(self):
        """
        Run in new thread
        """
        self.__running = True
        self.__connection = DataBaseConnection()
        _thread.start_new_thread(self.__run, ())

    def __run(self):
        """
        Process itself
        """
        while self.__running:
            time.sleep(15)
            logging.info('Keepalive Manager iteration!')
            for devid in self.__connection.get_utim_names():
                status = self.__connection.get_status(devid)
                counter = self.__connection.get_keep_alive_counter(devid)
                logging.info('Thinking about {} with status {} and counter {}'.format(devid, status, counter))
                if status == Status.STATUS_DONE or status == Status.STATUS_NO_CONFIG:
                    if counter > 4:
                        logging.info('{} is dead now'.format(devid))
                        self.__connection.set_status(devid, Status.STATUS_DED)
                    else:
                        logging.info('Sending keepalive to {}'.format(devid))
                        self.__connection.set_keep_alive_counter(devid, counter + 1)
                        self.__outbound_queue.put([devid, Tag.UCOMMAND.KEEPALIVE])

    def stop(self):
        self.__running = False
