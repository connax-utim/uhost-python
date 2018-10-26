"""
The command worker
"""

import logging


class CommandWorkerCleanupException(Exception):
    """
    Some exception of CommandWorkerCleanup class
    """

    pass


class CommandWorkerCleanupUtimMethodException(Exception):
    """
    No Utim method exception of CommandWorkerCleanup class
    """

    pass


class CommandWorkerCleanup(object):
    """
    Cleanup command worker class
    """

    def __init__(self, uhost):
        """
        Initialization
        """

        self.__uhost = uhost  # Uhost instance

    def process(self, devid, data, outbound_queue):
        """
        Run process
        """

        logging.debug("Command Cleanup Worker. Cleaning up unrecognized MQTT Command from %s : %s",
                      devid, str(data))
