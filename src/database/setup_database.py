"""Create or upgrade the SpendWise PostgreSQL database and its tables."""

from pathlib import Path

import psycopg

from database.postgres_connection import get_connection


def _column_exists(cursor, table: str, column: str) -> bool:
    cursor.execute(
        """
        SELECT COUNT(*) FROM information_schema.columns
        WHERE table_schema = current_schema()
          AND table_name = %s AND column_name = %s
        """,
        (table, column),
    )
    row = cursor.fetchone()
    return bool(row and row[0] > 0)


def _migrate_existing_users(connection, cursor) -> None:
    """Add email and password_hash to an existing users table."""
    if not _column_exists(cursor, "users", "email"):
        cursor.execute(
            "ALTER TABLE users ADD COLUMN email VARCHAR(255)"
        )
    if not _column_exists(cursor, "users", "password_hash"):
        cursor.execute(
            "ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)"
        )
    if not _column_exists(cursor, "users", "monthly_income"):
        cursor.execute(
            "ALTER TABLE users ADD COLUMN monthly_income NUMERIC(12,2) "
            "NOT NULL DEFAULT 0.00"
        )


def initialize_database() -> None:
    schema_path = Path(__file__).with_name("schema.sql")
    sql_script = schema_path.read_text(encoding="utf-8")
    connection = get_connection()
    cursor = connection.cursor()

    try:
        for statement in sql_script.split(";"):
            statement = statement.strip()
            if statement:
                cursor.execute(statement)
        _migrate_existing_users(connection, cursor)
        connection.commit()
    except psycopg.Error:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    try:
        initialize_database()
        print("SpendWise database and tables are ready.")
    except (ConnectionError, psycopg.Error) as error:
        print(f"Database setup failed: {error}")
        raise SystemExit(1)
