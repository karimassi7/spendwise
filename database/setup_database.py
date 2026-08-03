"""Create the SpendWise database and all required tables."""

from pathlib import Path

from mysql.connector import Error

from spendwise.database.mysql_connection import get_connection


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
