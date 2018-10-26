"""ConnManager containing script"""
import logging
from .connmanagermqtt import ConnManagerMQTT
from .uconn_amqp import UConnAMQP
from .uconn_mqtt import UConnMQTT


class ConnManager(object):
    """
    Wrapper around connections. Be free to choose anything you want!
    MQTT or AMQP. Your choise is limited
    """

    CONNECTION_TYPE_MQTT = 'mqtt'
    CONNECTION_TYPE_AMQP = 'amqp'
    CONNECTION_TYPE_UMQTT = 'umqtt'

    def __init__(self, connection_type):
        """
        Initialization of ConnManager

        :param str connection_type: Connection type (mqtt and amqp is supported)
        """
        logging.info('Initializing ConnManager, type: ' + connection_type)
        if connection_type == ConnManager.CONNECTION_TYPE_AMQP:
            self.__connection = UConnAMQP()
        elif connection_type == ConnManager.CONNECTION_TYPE_UMQTT:
            self.__connection = UConnMQTT()
        else:
            self.__connection = ConnManagerMQTT()

    def disconnect(self):
        """
        Disconnection from server
        """
        logging.info('Disconnecting...')
        self.__connection.disconnect()

    def subscribe(self, topic, callback_object, callback):
        """
        Subscribe on topic

        :param str topic: Topic for subscription
        :param object callback_object: Object with callback method
        :param method callback: Callback for received message
        """
        logging.info("Subscribing for {0}".format(topic))
        self.__callback_object = callback_object
        self.__callback = callback
        self.__connection.subscribe(topic, self, ConnManager._on_message)

    def unsubscribe(self, topic):
        """
        Unsubscribe from topic

        :param str topic: Topic for subscription cancelling
        """
        logging.info("Unsubscribing from {0}".format(topic))
        self.__connection.unsubscribe(topic)

    def publish(self, sender, destination, message):
        """
        Publish message

        :param sender: Message sender
        :param destination: Message destination
        :param message: The message
        """
        logging.info("Publishing {0} to topic {1}".format(message, destination))
        self.__connection.publish(sender, destination, message)

    def _on_message(self, sender, message):
        """
        Message receiving callback

        :param sender: Message sender
        :param message: The message
        """
        logging.info("Received message {0} from {1}".format(message, sender))
        self.__callback(self.__callback_object, sender, message)
