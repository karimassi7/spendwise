"""PostgreSQL connection helpers for SpendWise."""

import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import psycopg
from psycopg import Connection


def _load_dotenv() -> None:
    """Load repository .env values without overriding process environment."""
    env_path = Path(__file__).parents[2] / ".env"
    if not env_path.is_file():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        if key.strip() and key.strip() not in os.environ:
            os.environ[key.strip()] = value.strip().strip('"').strip("'")


def _database_url() -> str:
    """Return the configured PostgreSQL connection URL."""
    _load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ConnectionError("DATABASE_URL is not configured.")
    return database_url


def get_connection() -> Connection:
    """Open and return a PostgreSQL connection."""
    try:
        return psycopg.connect(_database_url())
    except psycopg.Error as error:
        raise ConnectionError(f"Could not connect to PostgreSQL: {error}") from error


@contextmanager
def database_connection() -> Iterator[Connection]:
    """Provide a connection and always close it after use."""
    connection = get_connection()
    try:
        yield connection
    finally:
        connection.close()


def test_connection() -> bool:
    """Return True when the configured PostgreSQL database can be reached."""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            return cursor.fetchone() == (1,)
    finally:
        connection.close()
