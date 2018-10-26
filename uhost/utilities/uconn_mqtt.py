"""
UConnMQTT module

This module implements the MQTT connection and messaging through the Mosquitto broker
"""

import logging
from . import exceptions, config
import paho.mqtt.client as mqtt
import time


class UConnMQTT(object):
    """
    MQTT class
    """

    def __init__(self):
        """
        Initialize MQTT connection
        """

        self.__topic = None
        self.__message_callback = None
        self.reconnection = 0

        self.__config = config.Config()

        # Get connection parameters
        username, password, host = self.__get_connection_parameters()

        # Establish connection
        self.__establish_connection(username, password, host)

    @staticmethod
    def __log_exception(ex):
        """
        Exception handler
        :param ex: Raised exception
        :raise: UtimConnectionException, UtimUnknownException
        """

        etype = type(ex)

        if etype == ValueError and \
                (str(ex) == 'Invalid host.' or str(ex) == 'Invalid credentials.'):
            logging.exception("Connection error " + str(ex))
            raise exceptions.UtimConnectionException
        else:
            logging.error('Unknown error ' + str(ex))
            raise exceptions.UtimUnknownException

    def __get_connection_parameters(self):
        """
        Function to get parameters for Mosquitto broker from config.py
        :return: Triplet of username, password and host address
        :rtype: str, str, str
        """
        return self.__config.messaging_username, self.__config.messaging_password, self.__config.messaging_hostname

    def __establish_connection(self, username, password, hostname):
        """
        Exception handler
        :param str username: User name
        :param str password: User password
        :param str hostname: Host name
        :return: Opened channel
        :raise: UtimConnectionException
        """

        self.connectionFlag = False
        while True:
            try:
                if username is None or password is None:
                    raise ValueError('Invalid credentials.')
                if hostname is None:
                    raise ValueError('Invalid host.')

                # Parameters and credentials

                self.__client = mqtt.Client()
                self.__client.on_connect = self.on_connect
                self.__client.on_disconnect = self.on_disconnect

                self.__client.username_pw_set(username, password)
                self.__client.on_message = self._on_message
                self.__client.connect(hostname)
                self.__client.loop_start()

                break
            except ValueError as er:
                self.__log_exception(er)
            except OSError as er:
                time.sleep(1)
                if self.reconnection == 0:
                    print('ucon-mqtt - Attempt to reconnect within %s seconds', self.__config.messaging_reconnect_time)
                    logging.error(er)
                    logging.error('Attempt to reconnect within %s seconds', self.__config.messaging_reconnect_time)
                self.reconnection += 1
                print("RECONNECTION TIMES: {0}".format(self.reconnection))
                time.sleep(1)
                if self.__config.messaging_reconnect_time <= self.reconnection:
                    print('ucon-mqtt - Reconnection timeout !')
                    logging.error('Reconnection timeout !')
                    raise exceptions.UtimConnectionException(er)

    def on_connect(self, client, userdata, flags, rc):
        print("ucon-mqtt - Internet connection established..")
        logging.debug("Internet connection established..")
        self.reconnection = 0
        self.connectionFlag = True

        if self.__topic:
            self.__client.subscribe(self.__topic)

    def on_disconnect(self, client, userdata, rc):
        print("ucon-mqtt - Internet connection losted..")
        logging.debug("Internet connection losted..")
        self.connectionFlag = False

        if rc != mqtt.MQTT_ERR_SUCCESS:
            self.reconnection += 1
            print("RECONNECTION TIMES: {0}".format(self.reconnection))

            self.__client.loop_stop(force=True)

            if self.__config.messaging_reconnect_time <= self.reconnection:
                print('ucon-mqtt - Reconnection timeout !')
                logging.error('Reconnection timeout !')
                raise exceptions.UtimConnectionException()

            # Get connection parameters
            username, password, host = self.__get_connection_parameters()

            # Establish connection
            self.__establish_connection(username, password, host)

    def disconnect(self):
        """
        Disconnect from broker
        """
        self.__client.disconnect()
        self.__client.loop_stop(force=True)

    def subscribe(self, topic, cbobj, callback):
        """
        Subscribe

        :param str topic: Channel name to listen
        :param callback: Callback
        """
        self.__topic = topic
        self.__cbobject = cbobj
        self.__message_callback = callback
        self.__client.subscribe(topic)

    def unsubscribe(self, topic):
        """
        Unsubscribe

        :param str topic: Channel name to listen
        """

        self.__topic = None
        self.__cbobject = None
        self.__message_callback = None
        self.__client.unsubscribe(topic)

    def publish(self, sender, destination, message):
        """
        Publish

        :param str sender: Message sender
        :param str destination: Message destination (non empty string)
        :param str message: The message to send
        """
        try:
            if (not isinstance(destination, str) or not destination or
                    not isinstance(message, bytes) or
                    not isinstance(sender, bytes)):
                raise exceptions.UtimExchangeException
            msg = sender + b' ' + message
            logging.info("UMQTT PUBLISH MESSAGE: {0}".format(msg))
            self.__client.publish(topic=destination, payload=msg)
        except exceptions.UtimExchangeException as ex:
            self.__log_exception(ex)

    def _on_message(self, client, userdata, message):
        """
        On message callback

        :param mqtt.Client client: mqtt.Client instance
        :param userdata: private user data as set in Client() or userdata_set()
        :param message: instance of MQTTMessage
        :returns: 0 - if custom message callback was called, 1 - if custom message callback is None,
        None - else
        """
        msg = message.payload
        m = msg.partition(b' ')
        if callable(self.__message_callback):
            self.__message_callback(self.__cbobject, m[0], m[2])
            return 0
        return 1
