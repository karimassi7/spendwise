"""PostgreSQL persistence for savings goals."""

from datetime import date
from decimal import Decimal

from database.postgres_connection import get_connection
from domain.savings_goal import SavingsGoal


class SavingsGoalRepository:
    """Persist and retrieve savings goals from PostgreSQL."""

    @staticmethod
    def _as_date(value: object) -> date:
        return value if isinstance(value, date) else date.fromisoformat(str(value))

    @classmethod
    def _from_row(cls, row: tuple[object, ...]) -> SavingsGoal:
        goal_id, user_id, name, target_amount, saved_amount, deadline = row
        return SavingsGoal(
            goal_id=int(goal_id),
            profile_id=int(user_id),
            name=str(name),
            target_amount=Decimal(str(target_amount)),
            saved_amount=Decimal(str(saved_amount)),
            deadline=cls._as_date(deadline),
        )

    def add(self, goal: SavingsGoal) -> SavingsGoal:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO savings_goals
                    (user_id, name, target_amount, saved_amount, deadline)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING goal_id
                """,
                (
                    goal.profile_id,
                    goal.name,
                    goal.target_amount,
                    goal.saved_amount,
                    goal.deadline,
                ),
            )
            connection.commit()
            goal.goal_id = int(cursor.fetchone()[0])
            return goal
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    def update(self, goal: SavingsGoal) -> bool:
        return self._write(
            """
            UPDATE savings_goals
            SET name = %s, target_amount = %s, saved_amount = %s, deadline = %s
            WHERE goal_id = %s AND user_id = %s
            """,
            (
                goal.name,
                goal.target_amount,
                goal.saved_amount,
                goal.deadline,
                goal.goal_id,
                goal.profile_id,
            ),
        )

    def remove(self, goal: SavingsGoal) -> bool:
        return self._write(
            "DELETE FROM savings_goals WHERE goal_id = %s AND user_id = %s",
            (goal.goal_id, goal.profile_id),
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

    def get_all(self, profile_id: int | None = None) -> list[SavingsGoal]:
        return self._select(profile_id=profile_id)

    def get_by_id(
        self, goal_id: int, profile_id: int | None = None
    ) -> SavingsGoal | None:
        results = self._select("goal_id", goal_id, profile_id, limit_one=True)
        return results[0] if results else None

    def get_by_name(
        self, name: str, profile_id: int | None = None
    ) -> SavingsGoal | None:
        results = self._select("LOWER(name)", name.lower(), profile_id, limit_one=True)
        return results[0] if results else None

    def _select(
        self,
        column: str | None = None,
        value: object = None,
        profile_id: int | None = None,
        limit_one: bool = False,
    ) -> list[SavingsGoal]:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            query = """
                SELECT goal_id, user_id, name, target_amount, saved_amount, deadline
                FROM savings_goals
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
            query += " ORDER BY goal_id"
            if limit_one:
                query += " LIMIT 1"
            cursor.execute(query, params)
            return [self._from_row(row) for row in cursor.fetchall()]
        finally:
            cursor.close()
            connection.close()

    def remove_by_profile_id(self, profile_id: int) -> None:
        self._write("DELETE FROM savings_goals WHERE user_id = %s", (profile_id,))
