from decimal import Decimal

from database.postgres_connection import get_connection
from domain.account import Account


class AccountRepository:
    """Persist and retrieve accounts from PostgreSQL."""

    @staticmethod
    def _from_row(row: tuple[object, ...]) -> Account:
        account_id, user_id, name, balance, account_type = row
        return Account(
            account_id=int(account_id),
            profile_id=int(user_id),
            name=str(name),
            balance=Decimal(str(balance)),
            account_type=str(account_type),
        )

    def add(self, account: Account) -> Account:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO accounts (user_id, name, balance, account_type)
                VALUES (%s, %s, %s, %s)
                RETURNING account_id
                """,
                (
                    account.profile_id,
                    account.name,
                    account.balance,
                    account.account_type,
                ),
            )
            connection.commit()
            account.account_id = int(cursor.fetchone()[0])
            return account
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    def update(self, account: Account) -> bool:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(
                """
                UPDATE accounts
                SET name = %s, balance = %s, account_type = %s
                WHERE account_id = %s AND user_id = %s
                """,
                (
                    account.name,
                    account.balance,
                    account.account_type,
                    account.account_id,
                    account.profile_id,
                ),
            )
            connection.commit()
            return cursor.rowcount > 0
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    def remove(self, account: Account) -> bool:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(
                "DELETE FROM accounts WHERE account_id = %s AND user_id = %s",
                (account.account_id, account.profile_id),
            )
            connection.commit()
            return cursor.rowcount > 0
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    def get_all(self, profile_id: int | None = None) -> list[Account]:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            query = """
                SELECT account_id, user_id, name, balance, account_type
                FROM accounts
            """
            params: tuple[object, ...] = ()
            if profile_id is not None:
                query += " WHERE user_id = %s"
                params = (profile_id,)
            query += " ORDER BY account_id"
            cursor.execute(query, params)
            return [self._from_row(row) for row in cursor.fetchall()]
        finally:
            cursor.close()
            connection.close()

    def get_by_id(
        self, account_id: int, profile_id: int | None = None
    ) -> Account | None:
        return self._get_one("account_id", account_id, profile_id)

    def get_by_name(self, name: str, profile_id: int | None = None) -> Account | None:
        return self._get_one("name", name, profile_id)

    def _get_one(
        self, column: str, value: object, profile_id: int | None
    ) -> Account | None:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            query = f"""
                SELECT account_id, user_id, name, balance, account_type
                FROM accounts WHERE {column} = %s
            """
            params: tuple[object, ...] = (value,)
            if profile_id is not None:
                query += " AND user_id = %s"
                params += (profile_id,)
            query += " ORDER BY account_id LIMIT 1"
            cursor.execute(query, params)
            row = cursor.fetchone()
            return self._from_row(row) if row is not None else None
        finally:
            cursor.close()
            connection.close()

    def remove_by_profile_id(self, profile_id: int) -> None:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM accounts WHERE user_id = %s", (profile_id,))
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()
