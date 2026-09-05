"""MySQL connection helpers for the local SpendWise database"""

import os
from collections.abc import Iterator
from contextlib import contextmanager

import mysql.connector
from mysql.connector import Error, MySQLConnection

def _connection_settings(include_database: bool = True) -> dict[str, object]:

    settings: dict[str, object] = {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        #  uses an empty root password by default.
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "charset": "utf8mb4",
        "use_unicode": True,
    }

    if include_database:
        settings["database"] = os.getenv("MYSQL_DATABASE", "spendwise")

    return settings


def get_connection(include_database: bool = True) -> MySQLConnection:
    """Open and return a connection to the local MySQL server"""
    try:
        return mysql.connector.connect(**_connection_settings(include_database))
    except Error as error:
        raise ConnectionError(f"Could not connect to MySQL: {error}") from error


@contextmanager
def database_connection() -> Iterator[MySQLConnection]:
    """Provide a connection and always close it after use"""
    connection = get_connection()
    try:
        yield connection
    finally:
        if connection.is_connected():
            connection.close()


def test_connection() -> bool:
    """Return True when the SpendWise database can be reached."""
    connection = get_connection()
    try:
        return connection.is_connected()
    finally:
        if connection.is_connected():
            connection.close()
