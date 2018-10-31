"""
Example of creating users

NOTE: run this script with sudo
"""

import logging
import sys
import os
import crypt
import mysql.connector
import datetime
import pwd

MYSQL_USER = 'test'
MYSQL_PASS = 'test'
MYSQL_HOST = 'localhost'
MYSQL_DB = 'uhost_74657374'

logging.basicConfig(format='[%(asctime)s] %(message)s', level=logging.INFO)


def execute(sql):
    try:
        connection = mysql.connector.connect(user=MYSQL_USER, password=MYSQL_PASS, host=MYSQL_HOST, database=MYSQL_DB)
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


def main():
    """
    Main function
    :return:
    """

    max_time = datetime.datetime.fromtimestamp(0)

    while True:
        try:
            sql = """
                SELECT device_id, session_key, update_time
                FROM udata
                where session_key is not null and update_time > '{max_time}'
                order by update_time asc 
            """.format(max_time=max_time)
            res = execute(sql)

            if res and len(res) > 0:
                for item in res:
                    if len(item) == 3:
                        action = 'created'
                        username = item[0]
                        password = item[1]
                        max_time = item[2]
                        enc_pass = crypt.crypt(password, 'salt')
                        try:
                            pwd.getpwnam(username)
                            os.system("userdel -rf {uname}".format(uname=username))
                            action = 'updated'
                        except KeyError:
                            pass

                        os.system("useradd -m -p {passwd} {uname}".format(passwd=enc_pass, uname=username))

                        logging.info("USER: {uname} is {action}".format(uname=username, action=action))
                        logging.info("MAX_TIME: {time}".format(time=max_time))

        except (KeyboardInterrupt, EOFError):
            logging.info('Program interrupted')
            sys.exit(0)


if __name__ == '__main__':
    main()
