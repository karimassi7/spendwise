"""MySQL persistence for budgets."""

from datetime import date
from decimal import Decimal

from database.mysql_connection import get_connection
from domain.budget import Budget
from repositories.category_repository import CategoryRepository


class BudgetRepository:
    """Persist and retrieve budgets from MySQL."""

    def __init__(self, category_repository: CategoryRepository):
        self.category_repository = category_repository

    def _from_row(self, row: tuple[object, ...]) -> Budget:
        budget_id, user_id, category_id, limit_amount, from_date, to_date = row
        profile_id = int(user_id)
        category = self.category_repository.get_by_id(int(category_id), profile_id)
        if category is None:
            raise ValueError(f"Category with ID {category_id} was not found.")
        return Budget(
            budget_id=int(budget_id),
            profile_id=profile_id,
            category=category,
            limit_amount=Decimal(str(limit_amount)),
            from_date=self._as_date(from_date),
            to_date=self._as_date(to_date),
        )

    @staticmethod
    def _as_date(value: object) -> date:
        return value if isinstance(value, date) else date.fromisoformat(str(value))

    def add(self, budget: Budget) -> Budget:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO budgets
                    (user_id, category_id, limit_amount, from_date, to_date)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    budget.profile_id,
                    budget.category.category_id,
                    budget.limit_amount,
                    budget.from_date,
                    budget.to_date,
                ),
            )
            connection.commit()
            budget.budget_id = int(cursor.lastrowid)
            return budget
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    def update(self, budget: Budget) -> bool:
        return self._write(
            """
            UPDATE budgets
            SET category_id = %s, limit_amount = %s, from_date = %s, to_date = %s
            WHERE budget_id = %s AND user_id = %s
            """,
            (
                budget.category.category_id,
                budget.limit_amount,
                budget.from_date,
                budget.to_date,
                budget.budget_id,
                budget.profile_id,
            ),
        )

    def remove(self, budget: Budget) -> bool:
        return self._write(
            "DELETE FROM budgets WHERE budget_id = %s AND user_id = %s",
            (budget.budget_id, budget.profile_id),
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

    def get_all(self, profile_id: int | None = None) -> list[Budget]:
        return self._select(profile_id=profile_id)

    def get_by_id(self, budget_id: int, profile_id: int | None = None) -> Budget | None:
        results = self._select("budget_id", budget_id, profile_id, limit_one=True)
        return results[0] if results else None

    def get_by_category_id(
        self, category_id: int, profile_id: int | None = None
    ) -> list[Budget]:
        return self._select("category_id", category_id, profile_id)

    def _select(
        self,
        column: str | None = None,
        value: object = None,
        profile_id: int | None = None,
        limit_one: bool = False,
    ) -> list[Budget]:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            query = """
                SELECT budget_id, user_id, category_id, limit_amount,
                       from_date, to_date
                FROM budgets
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
            query += " ORDER BY budget_id"
            if limit_one:
                query += " LIMIT 1"
            cursor.execute(query, params)
            return [self._from_row(row) for row in cursor.fetchall()]
        finally:
            cursor.close()
            connection.close()

    def remove_by_profile_id(self, profile_id: int) -> None:
        self._write("DELETE FROM budgets WHERE user_id = %s", (profile_id,))
