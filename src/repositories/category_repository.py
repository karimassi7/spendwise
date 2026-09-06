"""PostgreSQL persistence for spending categories."""

from database.postgres_connection import get_connection
from domain.spending_category import Category


class CategoryRepository:
    """Persist and retrieve categories from PostgreSQL."""

    @staticmethod
    def _from_row(row: tuple[object, ...]) -> Category:
        category_id, user_id, name, category_type = row
        return Category(
            category_id=int(category_id),
            profile_id=int(user_id),
            name=str(name),
            category_type=str(category_type),
        )

    def add(self, category: Category) -> Category:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO categories (user_id, name, category_type)
                VALUES (%s, %s, %s)
                RETURNING category_id
                """,
                (category.profile_id, category.name, category.category_type),
            )
            connection.commit()
            category.category_id = int(cursor.fetchone()[0])
            return category
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    def update(self, category: Category) -> bool:
        return self._write(
            """
            UPDATE categories SET name = %s, category_type = %s
            WHERE category_id = %s AND user_id = %s
            """,
            (
                category.name,
                category.category_type,
                category.category_id,
                category.profile_id,
            ),
        )

    def remove(self, category: Category) -> bool:
        return self._write(
            "DELETE FROM categories WHERE category_id = %s AND user_id = %s",
            (category.category_id, category.profile_id),
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

    def get_all(self, profile_id: int | None = None) -> list[Category]:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            query = "SELECT category_id, user_id, name, category_type FROM categories"
            params: tuple[object, ...] = ()
            if profile_id is not None:
                query += " WHERE user_id = %s"
                params = (profile_id,)
            query += " ORDER BY category_id"
            cursor.execute(query, params)
            return [self._from_row(row) for row in cursor.fetchall()]
        finally:
            cursor.close()
            connection.close()

    def get_by_id(
        self, category_id: int, profile_id: int | None = None
    ) -> Category | None:
        return self._get_one("category_id", category_id, profile_id)

    def get_by_name(self, name: str, profile_id: int | None = None) -> Category | None:
        return self._get_one("name", name, profile_id)

    def _get_one(
        self, column: str, value: object, profile_id: int | None
    ) -> Category | None:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            query = (
                "SELECT category_id, user_id, name, category_type "
                f"FROM categories WHERE {column} = %s"
            )
            params: tuple[object, ...] = (value,)
            if profile_id is not None:
                query += " AND user_id = %s"
                params += (profile_id,)
            query += " ORDER BY category_id LIMIT 1"
            cursor.execute(query, params)
            row = cursor.fetchone()
            return self._from_row(row) if row is not None else None
        finally:
            cursor.close()
            connection.close()

    def remove_by_profile_id(self, profile_id: int) -> None:
        self._write("DELETE FROM categories WHERE user_id = %s", (profile_id,))
