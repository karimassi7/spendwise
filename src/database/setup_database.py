"""Create or upgrade the SpendWise database and all required tables."""

from pathlib import Path

from mysql.connector import Error

from database.mysql_connection import get_connection


def _column_exists(cursor, table: str, column: str) -> bool:
    cursor.execute(
        """
        SELECT COUNT(*) FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = %s AND COLUMN_NAME = %s
        """,
        (table, column),
    )
    row = cursor.fetchone()
    return bool(row and row[0] > 0)


def _migrate_existing_users(connection, cursor) -> None:
    """Add email and password_hash to an existing users table."""
    if not _column_exists(cursor, "users", "email"):
        cursor.execute(
            "ALTER TABLE users ADD COLUMN email VARCHAR(255) NOT NULL "
            "UNIQUE AFTER user_id"
        )
    if not _column_exists(cursor, "users", "password_hash"):
        cursor.execute(
            "ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) NOT NULL "
            "AFTER email"
        )
    if not _column_exists(cursor, "users", "monthly_income"):
        cursor.execute(
            "ALTER TABLE users ADD COLUMN monthly_income DECIMAL(12,2) "
            "NOT NULL DEFAULT 0.00 AFTER currency"
        )


def initialize_database() -> None:
    schema_path = Path(__file__).with_name("schema.sql")
    sql_script = schema_path.read_text(encoding="utf-8")
    connection = get_connection(include_database=False)
    cursor = connection.cursor()

    try:
        for statement in sql_script.split(";"):
            statement = statement.strip()
            if statement:
                cursor.execute(statement)
        _migrate_existing_users(connection, cursor)
        connection.commit()
    except Error:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    try:
        initialize_database()
        print("SpendWise database and tables are ready.")
    except (ConnectionError, Error) as error:
        print(f"Database setup failed: {error}")
        raise SystemExit(1)
