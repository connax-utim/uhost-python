"""
MySQL database connection module
"""

import mysql.connector
import datetime
import logging
from . import config


class DataBaseConnection(object):
    __DB_NAME = 'udata'
    __SUB_DB_NAME = 'subs'
    __STATUSES_DB_NAME = 'statuses'

    __MAX_TRIES = 3

    __STATUSES_LIST = [
        ['STATUS_CONFIGURING', 'Provisioning', 'Online', 'D2C protected'],
        ['STATUS_DED', 'Disabled', 'Offline', 'Not protected'],
        ['STATUS_DONE', 'Working', 'Online', 'D2C protected'],
        ['STATUS_NEWBORN', 'Disabled', 'Offline', 'Not protected'],
        ['STATUS_NO_CONFIG', 'Disabled', 'Online', 'D2C protected'],
        ['STATUS_SRP', 'Provisioning', 'Connecting', 'Securing connection'],
        ['STATUS_TESTING', 'Provisioning', 'Online', 'D2C protected']

    ]

    def __init__(self, init_db=False):
        self.__config = config.Config()
        self.__uhost_name = 'uhost_' + self.__config.uhost_name
        self.__db_host = self.__config.db_hostname
        self.__db_name = self.__config.db_username
        self.__db_pass = self.__config.db_password

        if init_db:
            self.__create_db(self.__uhost_name)
            self.__create_table(self.__uhost_name)
            self.__insert_statuses(self.__uhost_name)

    def __execute(self, sql):
        tries = 0
        while tries < self.__MAX_TRIES:
            try:
                connection = mysql.connector.connect(user=self.__db_name, password=self.__db_pass, host=self.__db_host,
                                                     database=self.__uhost_name)
                connection.autocommit = True
                cursor = connection.cursor()
                cursor.execute(sql)
                fetch = None
                if cursor.with_rows:
                    fetch = cursor.fetchall()
                cursor.close()
                connection.disconnect()
                return fetch
            except mysql.connector.Error as er:
                logging.debug(sql)
                logging.debug(er)
                tries = tries + 1
                logging.debug('reconnect')

    def __create_db(self, db_name):
        connection = mysql.connector.connect(user=self.__db_name, password=self.__db_pass, host=self.__db_host)
        connection.autocommit = True
        sql = """CREATE DATABASE IF NOT EXISTS {db_name};""".format(db_name=db_name)
        cursor = connection.cursor()
        cursor.execute(sql)

    def __create_table(self, db_name):
        connection = mysql.connector.connect(user=self.__db_name, password=self.__db_pass, host=self.__db_host,
                                             database=db_name)
        connection.autocommit = True
        cursor = connection.cursor()

        sql = """CREATE TABLE IF NOT EXISTS {status_db_name} (
                    complex_status CHAR(32) NOT NULL,
                    status CHAR(32),
                    provision CHAR(32),
                    network CHAR(32),
                    security CHAR(32),
                    PRIMARY KEY (complex_status));""".format(status_db_name=self.__STATUSES_DB_NAME)
        logging.debug(sql)
        cursor.execute(sql)
        sql = """CREATE TABLE IF NOT EXISTS {sub_db_name} (
                    sub_id INT NOT NULL AUTO_INCREMENT,
                    sub_name CHAR(64),
                    sub_type CHAR(32),
                    host_name CHAR(64),
                    shared_access_key_name CHAR(32),
                    shared_access_key CHAR(64),
                    auth_method CHAR(32),
                    region CHAR(32),
                    PRIMARY KEY (sub_id));""".format(sub_db_name=self.__SUB_DB_NAME)
        logging.debug(sql)
        cursor.execute(sql)
        sql = """CREATE TABLE IF NOT EXISTS {db_name} (
                    device_id CHAR(64) NOT NULL,
                    name CHAR(64),
                    session_key CHAR(64),
                    config_hash CHAR(64),
                    keep_alive_counter INT DEFAULT 0,
                    status CHAR(32) DEFAULT 'STATUS_NEWBORN',
                    update_time TIMESTAMP,
                    sub_id INT,
                    PRIMARY KEY (device_id),
                    FOREIGN KEY (sub_id) REFERENCES {sub_db_name}(sub_id),
                    FOREIGN KEY (status) REFERENCES {status_db_name}(complex_status));""".format(
            db_name=self.__DB_NAME, sub_db_name=self.__SUB_DB_NAME, status_db_name=self.__STATUSES_DB_NAME
        )
        logging.debug(sql)
        cursor.execute(sql)

    def __insert_statuses(self, db_name):
        logging.debug('Start inserting')
        connection = mysql.connector.connect(user=self.__db_name, password=self.__db_pass, host=self.__db_host,
                                             database=db_name)
        connection.autocommit = True
        cursor = connection.cursor()

        for item in self.__STATUSES_LIST:
            logging.debug(item)
            if len(item) == 4:
                try:
                    sql = """
                        INSERT INTO {table_name} (complex_status, status, network, security)
                        VALUES ('{cstatus}', '{status}', '{network}', '{security}');
                    """.format(table_name=self.__STATUSES_DB_NAME, cstatus=item[0], status=item[1], network=item[2],
                               security=item[3])
                    logging.debug(sql)
                    cursor.execute(sql)
                except mysql.connector.errors.IntegrityError as ex:
                    logging.debug(ex)
                    if '1062 (23000): Duplicate entry ' not in str(ex):
                        raise ex

        logging.debug('End inserting')

    def add_utim(self, devid):
        sql = """INSERT INTO {db_name} (device_id)
                 VALUES ('{devid}');""".format(db_name=self.__DB_NAME, devid=devid)
        print(sql)
        print(self.__execute(sql))

    def get_utim_names(self):
        """
        Get all utim names
        :return: list of utim IDs
        """
        sql = "SELECT device_id FROM {db_name}".format(db_name=self.__DB_NAME)
        fetch = self.__execute(sql)
        result = list()

        if fetch:
            for row in fetch:
                result.append(row[0])
        return result

    def does_utim_exist(self, devid):
        """
        If Utim exists in DB
        :return: True or False
        """
        sql = "SELECT device_id FROM {db_name} WHERE device_id = '{devid}'".format(db_name=self.__DB_NAME,
                                                                                   devid=devid)
        fetch = self.__execute(sql)
        if fetch is not None and len(fetch) > 0:
            return True
        return False

    def get_session_key(self, devid):
        """
        Get Utim session key by ID
        :param str devid: Utim ID
        :return bytes: session key
        """
        # TODO session key must be dehexlified
        sql = "SELECT session_key FROM {db_name} WHERE device_id = '{devid}'".format(db_name=self.__DB_NAME,
                                                                                     devid=devid)
        fetch = self.__execute(sql)
        if fetch is not None and len(fetch) > 0 and fetch[0][0] is not None:
            return bytes.fromhex(fetch[0][0])
        return None

    def set_session_key(self, devid, session_key):
        """
        Set Utim session key
        :param str devid:
        :param bytes session_key:
        :return: nothing
        """
        s_key_to_db = 'NULL'
        if session_key is not None:
            s_key_to_db = "'" + session_key.hex() + "'"

        sql = """UPDATE {db_name}
                 SET session_key = {session_key}
                 WHERE device_id='{devid}'""".format(db_name=self.__DB_NAME,
                                                     session_key=s_key_to_db,
                                                     devid=devid)
        self.__execute(sql)

    def get_config_hash(self, devid):
        """
        Get Utim config hash
        :param str devid:
        :return str: config hash
        """
        sql = "SELECT config_hash FROM {db_name} WHERE device_id = '{devid}'".format(db_name=self.__DB_NAME,
                                                                                     devid=devid)
        fetch = self.__execute(sql)
        if fetch is not None and len(fetch) > 0:
            return fetch[0][0]
        return None

    def set_config_hash(self, devid, config_hash):
        """
        Set Utim config hash
        :param str devid:
        :param str config_hash:
        :return: nothing
        """
        c_hash_to_db = 'NULL'
        if config_hash is not None:
            c_hash_to_db = "'" + config_hash + "'"
        sql = """UPDATE {db_name}
                 SET config_hash = {config_hash}
                 WHERE device_id='{devid}'""".format(db_name=self.__DB_NAME,
                                                     config_hash=c_hash_to_db,
                                                     devid=devid)
        self.__execute(sql)

    def get_keep_alive_counter(self, devid):
        """
        Get Utim keepalive counter
        :param str devid:
        :return int: counter
        """
        sql = "SELECT keep_alive_counter FROM {db_name} WHERE device_id = '{devid}'".format(db_name=self.__DB_NAME,
                                                                                            devid=devid)
        fetch = self.__execute(sql)
        if fetch is not None and len(fetch) > 0:
            return fetch[0][0]
        return 0

    def set_keep_alive_counter(self, devid, counter):
        """
        Set Utim keepalive counter
        :param str devid:
        :param int counter:
        :return: nothing
        """
        sql = """UPDATE {db_name}
                 SET keep_alive_counter = {counter} 
                 WHERE device_id='{devid}'""".format(db_name=self.__DB_NAME,
                                                     counter=counter,
                                                     devid=devid)
        self.__execute(sql)

    def get_status(self, devid):
        """
        Get Utim status
        :param str devid:
        :return str: status
        """
        sql = "SELECT status FROM {db_name} WHERE device_id = '{devid}'".format(db_name=self.__DB_NAME,
                                                                                devid=devid)
        fetch = self.__execute(sql)
        if fetch is not None and len(fetch) > 0:
            return fetch[0][0]
        return None

    def set_status(self, devid, status):
        """
        Set Utim status
        :param str devid:
        :param str status:
        :return: nothing
        """
        timestamp = str(datetime.datetime.now())
        sql = """UPDATE {db_name}
                 SET status = '{status}',
                     update_time = '{timestamp}'
                 WHERE device_id='{devid}'""".format(db_name=self.__DB_NAME,
                                                     status=status,
                                                     timestamp=timestamp,
                                                     devid=devid)
        self.__execute(sql)

    def get_configuration(self, devid):
        """
        Get configuration
        :param str devid:
        :return: some long data which is config
        """
        sql = """SELECT
                    s.sub_type,
                    s.host_name,
                    s.shared_access_key_name,
                    s.shared_access_key,
                    s.auth_method,
                    s.region
                 FROM {db_name} u, {sub_db_name} s
                 WHERE
                    u.device_id = '{devid}' and
                    u.sub_id = s.sub_id""".format(db_name=self.__DB_NAME,
                                                  sub_db_name=self.__SUB_DB_NAME,
                                                  devid=devid)
        fetch = self.__execute(sql)
        if fetch is not None and len(fetch) > 0 and len(fetch[0]) >= 6:
            result = {'type': fetch[0][0],
                      'host_name': fetch[0][1],
                      'shared_access_key_name': fetch[0][2],
                      'shared_access_key': fetch[0][3],
                      'auth_method': fetch[0][4],
                      'region': fetch[0][5]}
            return result
        return None
