from datetime import date
from decimal import Decimal

from database.mysql_connection import get_connection
from domain.transaction import Transaction
from repositories.account_repository import AccountRepository
from repositories.category_repository import CategoryRepository


class TransactionRepository:
    def __init__(
        self,
        account_repository: AccountRepository,
        category_repository: CategoryRepository,
    ):
        self.account_repository = account_repository
        self.category_repository = category_repository

    @staticmethod
    def _as_date(value: object) -> date:
        return value if isinstance(value, date) else date.fromisoformat(str(value))

    def _from_row(self, row: tuple[object, ...]) -> Transaction:
        (
            transaction_id,
            user_id,
            account_id,
            category_id,
            amount,
            description,
            transaction_date,
        ) = row
        profile_id = int(user_id)
        account = self.account_repository.get_by_id(int(account_id), profile_id)
        category = self.category_repository.get_by_id(int(category_id), profile_id)
        if account is None:
            raise ValueError(f"Account with ID {account_id} was not found.")
        if category is None:
            raise ValueError(f"Category with ID {category_id} was not found.")
        return Transaction(
            transaction_id=int(transaction_id),
            profile_id=profile_id,
            account=account,
            category=category,
            amount=Decimal(str(amount)),
            description=str(description),
            transaction_date=self._as_date(transaction_date),
        )

    def add(self, transaction: Transaction) -> Transaction:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO transactions
                    (user_id, account_id, category_id, amount,
                     description, transaction_date)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    transaction.profile_id,
                    transaction.account.account_id,
                    transaction.category.category_id,
                    transaction.amount,
                    transaction.description,
                    transaction.transaction_date,
                ),
            )
            connection.commit()
            transaction.transaction_id = int(cursor.lastrowid)
            return transaction
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    def update(self, transaction: Transaction) -> bool:
        return self._write(
            """
            UPDATE transactions
            SET account_id = %s, category_id = %s, amount = %s,
                description = %s, transaction_date = %s
            WHERE transaction_id = %s AND user_id = %s
            """,
            (
                transaction.account.account_id,
                transaction.category.category_id,
                transaction.amount,
                transaction.description,
                transaction.transaction_date,
                transaction.transaction_id,
                transaction.profile_id,
            ),
        )

    def remove(self, transaction: Transaction) -> bool:
        return self._write(
            "DELETE FROM transactions WHERE transaction_id = %s AND user_id = %s",
            (transaction.transaction_id, transaction.profile_id),
        )

    def _write(self, query: str, params: tuple[object, ...]) -> bool:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(query, params)
            connection.commit()
            return cursor.rowcount > 0
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    def get_all(self, profile_id: int | None = None) -> list[Transaction]:
        return self._select(profile_id=profile_id)

    def get_by_id(
        self, transaction_id: int, profile_id: int | None = None
    ) -> Transaction | None:
        results = self._select(
            "transaction_id", transaction_id, profile_id, limit_one=True
        )
        return results[0] if results else None

    def get_by_account_id(
        self, account_id: int, profile_id: int | None = None
    ) -> list[Transaction]:
        return self._select("account_id", account_id, profile_id)

    def get_by_category_id(
        self, category_id: int, profile_id: int | None = None
    ) -> list[Transaction]:
        return self._select("category_id", category_id, profile_id)

    def _select(
        self,
        column: str | None = None,
        value: object = None,
        profile_id: int | None = None,
        limit_one: bool = False,
    ) -> list[Transaction]:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            query = """
                SELECT transaction_id, user_id, account_id, category_id,
                       amount, description, transaction_date
                FROM transactions
            """
            clauses: list[str] = []
            params: tuple[object, ...] = ()
            if column is not None:
                clauses.append(f"{column} = %s")
                params += (value,)
            if profile_id is not None:
                clauses.append("user_id = %s")
                params += (profile_id,)
            if clauses:
                query += " WHERE " + " AND ".join(clauses)
            query += " ORDER BY transaction_id"
            if limit_one:
                query += " LIMIT 1"
            cursor.execute(query, params)
            return [self._from_row(row) for row in cursor.fetchall()]
        finally:
            cursor.close()
            connection.close()

    def remove_by_profile_id(self, profile_id: int) -> None:
        self._write("DELETE FROM transactions WHERE user_id = %s", (profile_id,))
