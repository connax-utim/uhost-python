"""
UConnAMQP module

This module implements the AMQP connection and messaging through the RabbitMQ server
"""
import logging
import _thread
import pika
import pika.connection
from . import exceptions, config


class UConnAMQP(object):
    """
    Connection to AMQP class
    """

    def __init__(self):
        """
        Initialize AMQP connection

        :raises utim.exceptions.UtimConnectionException: if connection is broken
        """

        # Get connection parameters
        self.__username, self.__password, self.__host = self.__get_connection_parameters()

        # SUBSCRIBER
        self.SUBSCRIBE_QUEUE = None
        self.SUBSCRIBE_ROUTING_KEY = None
        self.__callback_object = None
        self.__callback = None

        # Connection
        self._connection = None
        self._channel = None
        self._consumer_tag = None
        self._consuming = False

        self.__config = config.Config()

        # Establish connection
        self.__establish_connection(self.__username, self.__password, self.__host)

    def __get_connection_parameters(self):
        """
        Function to get parameters for RabbitMQ from config.py
        :return: Triplet of username, password and host address
        :rtype: str, str, str
        """
        return self.__config.messaging_username, self.__config.messaging_password, self.__config.messaging_hostname

    def __log_exception(self, ex):
        """
        Exception handler
        :param ex: Raised exception
        :raise: UtimConnectionException, UtimUnknownException
        """

        etype = type(ex)

        self.disconnect()

        if (etype == pika.exceptions.ConnectionClosed
                or etype == pika.exceptions.ProbableAuthenticationError
                or etype == pika.exceptions.ChannelClosed
                or etype == exceptions.UtimConnectionException):
            logging.exception("Connection error " + str(ex))
            raise exceptions.UtimConnectionException
        elif (etype == exceptions.UtimExchangeException
              or etype == pika.exceptions.UnsupportedAMQPFieldException):
            logging.exception("Exchange error " + str(ex))
            raise exceptions.UtimExchangeException
        else:
            logging.error('Unknown error ' + str(ex))
            raise exceptions.UtimUnknownException

    def __establish_connection(self, username, password, hostname):
        """
        Exception handler
        :param str username: User name
        :param str password: User password
        :param str hostname: Host name
        :return: Opened channel
        :raise: UtimConnectionException
        """
        try:
            if username is None or password is None:
                raise pika.exceptions.ProbableAuthenticationError
            if hostname is None:
                raise pika.exceptions.ConnectionClosed

            # Parameters and credentials
            credentials = pika.PlainCredentials(username, password)
            parameters = pika.ConnectionParameters(host=hostname, credentials=credentials,
                                                   heartbeat_interval=5)
            logging.info('Connecting to RabbitMQ server')
            self._connection = pika.BlockingConnection(parameters)
            self._channel = self._connection.channel()

        except (pika.exceptions.ProbableAuthenticationError,
                pika.exceptions.ConnectionClosed,
                pika.exceptions.ChannelClosed) as ex:
            self.__log_exception(ex)

    def on_message(self, unused_channel, basic_deliver, properties, body):
        """
        Invoked by pika when a message is delivered from RabbitMQ.

        :param pika.channel.Channel unused_channel: The channel object
        :param pika.Spec.Basic.Deliver basic_deliver: basic_deliver method
        :param pika.Spec.BasicProperties properties: properties
        :param str|unicode body: The message body
        """
        logging.info('Received message # %s from %s: %s', basic_deliver.delivery_tag,
                     properties.headers.get('sender'), body)
        self._channel.basic_ack(delivery_tag=basic_deliver.delivery_tag)
        if callable(self.__callback) and self.__callback:
            self.__callback(self.__callback_object, properties.headers.get('sender').encode(),
                            body)
            return 0
        return 1

    def publish(self, sender, destination, message):
        """
        Send message to destination

        :param str sender: Sender name
        :param str destination: Destination address
        :param str message: Text message
        """

        logging.debug("PUBLISH TYPES: %s %s %s", type(sender), type(destination), type(message))
        try:
            if (not isinstance(destination, str) or not destination
                    or not isinstance(message, bytes)
                    or not isinstance(sender, bytes)):
                raise exceptions.UtimExchangeException

            self._channel.queue_declare(queue=destination, durable=True)
            properties = pika.BasicProperties(headers={'sender': sender.decode()})
            self._channel.basic_publish(exchange='', routing_key=destination,
                                        properties=properties, body=message)
        except (pika.exceptions.ChannelClosed,
                pika.exceptions.UnsupportedAMQPFieldException,
                exceptions.UtimExchangeException) as ex:
            self.__log_exception(ex)

    def disconnect(self):
        """
        Disconnect function

        Disconnection from the RabbitMQ server
        """

        logging.info('Closing connection')
        if self._channel is not None:
            self._channel.basic_cancel(self._consumer_tag)
            self._channel.stop_consuming(self.SUBSCRIBE_QUEUE)

        if self._connection is not None:
            self._connection.close()

    def subscribe(self, topic, callback_object, callback):
        """
        Subscribe on topic

        :param str topic: Topic for subscription
        :param object callback_object: Object with callback method
        :param method callback: Callback for received message
        """

        self.SUBSCRIBE_QUEUE = topic
        self.SUBSCRIBE_ROUTING_KEY = topic
        self.__callback_object = callback_object
        self.__callback = callback

        self._channel.queue_declare(queue=self.SUBSCRIBE_QUEUE, durable=True)
        self._consumer_tag = self._channel.basic_consume(self.on_message, self.SUBSCRIBE_QUEUE)
        if not self._consuming:
            _thread.start_new_thread(self._channel.start_consuming, ())
            self._consuming = True

    def unsubscribe(self, topic):
        """
        Unsubscribe

        :param str topic: Channel name to listen
        """
        self.SUBSCRIBE_QUEUE = None
        self.SUBSCRIBE_ROUTING_KEY = None
        self.__callback_object = None
        self.__callback = None
        self._channel.basic_cancel(self._consumer_tag)
