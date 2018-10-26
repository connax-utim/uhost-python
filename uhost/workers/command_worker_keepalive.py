"""
The command worker
"""

import logging
from ..utilities.constants import Status


class CommandWorkerKeepalive(object):

    def __init__(self, uhost):
        """
        Initialization
        """

        self.__uhost = uhost  # Uhost instance

    def process(self, devid, data, outbound_queue):
        logging.info('Got keepalive from {}'.format(devid))
        self.__uhost.database.set_keep_alive_counter(devid, 0)
        config_hash = self.__uhost.database.get_config_hash(devid)
        config = self.__uhost.database.get_configuration(devid)
        new_config_hash = self.__uhost.config_hash(config)
        logging.info('Old hash: {}'.format(config_hash))
        logging.info('New hash: {}'.format(new_config_hash))
        if config_hash != new_config_hash:
            logging.info('{} needs some attention -- new config incoming!'.format(devid))
            if new_config_hash == self.__uhost.config_hash(None):
                self.__uhost.database.set_status(devid, Status.STATUS_NO_CONFIG)
                self.__uhost.database.set_config_hash(devid, new_config_hash)
            else:
                self.__uhost.database.set_status(devid, Status.STATUS_CONFIGURING)
