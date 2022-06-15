"""Database handler.
Handles the raw database connections, and database initialization of tables and required values.

"""
import mysql.connector
from mysql.connector import Error as MySqlError

from pignus.utils import log


def connect_mysql(server: dict):
    """Connect to MySql server and get a cursor object."""
    try:
        connection = mysql.connector.connect(
            host=server['HOST'],
            user=server['USER'],
            password=server['PASS'],
            database=server['NAME'],
            buffered=True,
            autocommit=True)
        if connection.is_connected():
            # db_info = connection.get_server_info()
            # log.debug(db_info)
            cursor = connection.cursor()
            cursor.execute("select database();")
            # record = cursor.fetchone()
            # log.debug(record)
        return connection, cursor
    except MySqlError as e:
        log.error("Error while connecting to MySQL: %s" % e, exception=e)
        exit(1)


def connect_mysql_no_db(server: dict):
    """Connect to MySql server, without specifying a database, and get a cursor object."""
    try:
        connection = mysql.connector.connect(
            host=server['HOST'],
            user=server['USER'],
            password=server['PASS'])
        if connection.is_connected():
            db_info = connection.get_server_info()
            log.debug(db_info)
            cursor = connection.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            log.debug(record)
        return connection, cursor
    except MySqlError as e:
        log.error("Error while connecting to MySQL: %s" % e, exception=e)
        exit(1)


def create_mysql_database(conn, cursor, db_name: str):
    """Create the MySQL database."""
    sql = """CREATE DATABASE IF NOT EXISTS %s""" % db_name
    cursor.execute(sql)
    log.info('Created database: %s' % db_name)
    return True


# End File: automox/pignus/src/pignus/utils/db.py
