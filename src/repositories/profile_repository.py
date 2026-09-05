from decimal import Decimal

from database.mysql_connection import get_connection
from domain.user_profile import UserProfile


class ProfileRepository:
    """Persist and retrieve user profiles from MySQL."""

    @staticmethod
    def _from_row(row: tuple[object, ...]) -> UserProfile:
        user_id, email, password_hash, name, currency, monthly_income = row
        return UserProfile(
            name=str(name),
            currency=str(currency),
            user_id=int(user_id),
            monthly_income=Decimal(str(monthly_income)),
            email=str(email),
            password_hash=str(password_hash),
        )

    def add(self, profile: UserProfile) -> UserProfile:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO users (email, password_hash, name, currency, monthly_income)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    profile.email,
                    profile.password_hash,
                    profile.name,
                    profile.currency,
                    profile.monthly_income,
                ),
            )
            connection.commit()
            profile.user_id = int(cursor.lastrowid)
            return profile
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    def update(self, profile: UserProfile) -> bool:
        return self._write(
            """
            UPDATE users SET email = %s, password_hash = %s,
                name = %s, currency = %s, monthly_income = %s
            WHERE user_id = %s
            """,
            (
                profile.email,
                profile.password_hash,
                profile.name,
                profile.currency,
                profile.monthly_income,
                profile.user_id,
            ),
        )

    def remove(self, profile: UserProfile) -> bool:
        return self._write("DELETE FROM users WHERE user_id = %s", (profile.user_id,))

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

    def get_all(self) -> list[UserProfile]:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(
                """
                SELECT user_id, email, password_hash, name, currency, monthly_income
                FROM users ORDER BY user_id
                """
            )
            return [self._from_row(row) for row in cursor.fetchall()]
        finally:
            cursor.close()
            connection.close()

    def get_by_id(self, user_id: int) -> UserProfile | None:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(
                """
                SELECT user_id, email, password_hash, name, currency, monthly_income
                FROM users WHERE user_id = %s
                """,
                (user_id,),
            )
            row = cursor.fetchone()
            return self._from_row(row) if row is not None else None
        finally:
            cursor.close()
            connection.close()

    def get_by_email(self, email: str) -> UserProfile | None:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(
                """
                SELECT user_id, email, password_hash, name, currency, monthly_income
                FROM users WHERE email = %s
                """,
                (email.strip().lower(),),
            )
            row = cursor.fetchone()
            return self._from_row(row) if row is not None else None
        finally:
            cursor.close()
            connection.close()
