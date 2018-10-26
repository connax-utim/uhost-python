import configparser
import os


class ConfigException(Exception):
    """
    Config exception
    """

    pass


class Config(object):

    def __init__(self):
        """
        Initialization
        """

        self.parser = configparser.ConfigParser()
        self.file = os.environ.get('UHOST_CONFIG', 'config.ini')
        self.parser.read(self.file)

        try:
            self.__uhost_name = self.parser['UHOST']['uhostname']
            self.__uhost_messaging_protocol = self.parser['UHOST']['messaging_protocol']
            self.__uhost_master_key = self.parser['UHOST']['messaging_protocol']
            self.__messaging_hostname = self.parser[self.uhost_messaging_protocol]['hostname']
            self.__messaging_username = self.parser[self.uhost_messaging_protocol]['username']
            self.__messaging_password = self.parser[self.uhost_messaging_protocol]['password']
            self.__messaging_reconnect_time = self.parser[self.uhost_messaging_protocol]['reconnect_time']
            self.__db_hostname = self.parser['MYSQLDB']['hostname']
            self.__db_username = self.parser['MYSQLDB']['username']
            self.__db_password = self.parser['MYSQLDB']['password']

        except KeyError:
            raise ConfigException

    @property
    def uhost_name(self):
        return self.__uhost_name

    @property
    def uhost_messaging_protocol(self):
        return self.__uhost_messaging_protocol

    @property
    def messaging_hostname(self):
        return self.__messaging_hostname

    @property
    def messaging_username(self):
        return self.__messaging_username

    @property
    def messaging_password(self):
        return self.__messaging_password

    @property
    def messaging_reconnect_time(self):
        return self.__messaging_reconnect_time

    @property
    def db_hostname(self):
        return self.__db_hostname

    @property
    def db_username(self):
        return self.__db_username

    @property
    def db_password(self):
        return self.__db_password
