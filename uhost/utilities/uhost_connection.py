"""
Uhost Connection module

This module implements Uhost connection and messaging through the MQTT or AMQP
"""

import logging
import queue
import _thread
import paho.mqtt.client as mqtt
from . import connmanager, exceptions, config


class UhostConnection(object):
    """
    MQTT class
    """

    def __init__(self, type, inbound_queue):
        """
        Initialize MQTT connection
        """

        # Establish connection
        self.__client = connmanager.ConnManager(type)

        self.__inbound_queue = inbound_queue  # Queue for inbound data
        self.outbound_queue = queue.Queue()  # Queue for outbound data

        self.__running = False  # Flag to inform there is work with serial or not

        self.__config = config.Config()

    @staticmethod
    def __log_exception(ex):
        """
        Exception handler

        :param ex: Raised exception
        :raise: UtimConnectionException, UtimUnknownException
        """

        ex_type = type(ex)

        if ex_type == ValueError and (str(ex) == 'Invalid host.' or str(ex) == 'Invalid credentials.'):
            logging.exception("Connection error " + str(ex))
            raise exceptions.UtimConnectionException
        else:
            logging.error('Unknown error ' + str(ex))
            raise exceptions.UtimUnknownException

    def disconnect(self):
        """
        Disconnect from broker
        """

        self.__running = False
        self.__client.disconnect()

    def run(self):
        """
        Run subscribe and publish to MQTT-broker
        """

        logging.info("Try to run in another thread")
        _thread.start_new_thread(self.run2, ())

    def run2(self):
        """
        Run listening and writing to Serial port
        Use it in another thread.
        """

        self.__running = True

        # Subscribe to topic
        self.__client.subscribe(bytes.fromhex(self.__config.uhost_name).decode(), self, UhostConnection._on_message)
        logging.debug("Subscribed to topic: %s", bytes.fromhex(self.__config.uhost_name).decode())

        logging.info("Start Running")
        while self.__running:
            self.__publish()

    def __publish(self):
        """
        Publish
        """

        while not self.outbound_queue.empty():
            item = self.outbound_queue.get()
            logging.debug("Publish item: %s", item)

            # Check number of elements of item
            item_length = len(item)
            if item_length == 2:
                destination = item[0]
                message = item[1]
                logging.debug("Message: %s", message)
                logging.debug("Type message: %s", type(message))
                self.__client.publish(bytes.fromhex(self.__config.uhost_name), destination, message)
                logging.debug("Message %s was published to %s", str(destination), str(message))

            else:
                logging.error("Invalid length of item: %d", item_length)

    def _on_message(self, sender, message):
        """
        On message callback

        :param mqtt.Client client: mqtt.Client instance
        :param userdata: private user data as set in Client() or userdata_set()
        :param message: instance of MQTTMessage
        :returns: 0 - if custom message callback was called, 1 - if custom message callback is None,
        None - else
        """

        logging.info("Received message {0} from {1}".format(message, sender))
        try:
            item = [sender, message]
            self.__inbound_queue.put(item)
            logging.debug("put item to inbound queue: %s", item)
        except queue.Full:
            logging.error("Inbound queue full")
