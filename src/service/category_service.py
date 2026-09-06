from domain.spending_category import Category
from repositories.category_repository import CategoryRepository


class CategoryService:
    """Provide category management operations."""

    CATEGORY_TYPES = ("income", "expense")

    def __init__(self, category_repository: CategoryRepository):
        self.category_repository = category_repository

    def add_category(self, profile_id: int, name: str, category_type: str) -> Category:
        """Add category."""
        name = name.strip()
        category_type = category_type.strip().lower()
        if not name:
            raise ValueError("Enter a valid category name.")
        if category_type not in self.CATEGORY_TYPES:
            raise ValueError("Category type must be 'income' or 'expense'.")
        # duplicate name allowed
        category = Category(
            # PostgreSQL replaces this temporary valid ID with an identity value.
            category_id=1,
            profile_id=profile_id,
            name=name,
            category_type=category_type,
        )
        self.category_repository.add(category)
        return category

    def remove(self, profile_id: int, category_id: int) -> None:
        """Remove the selected record."""
        if category_id <= 0:
            raise ValueError("Please enter a valid category ID.")
        category = self.category_repository.get_by_id(category_id, profile_id)
        if not category:
            raise ValueError("This category ID doesn't exist.")
        self.category_repository.remove(category)

    def update(
        self, profile_id: int, category_id: int, name: str, category_type: str
    ) -> Category:
        """Update and persist an existing record."""
        name = name.strip()
        category_type = category_type.strip().lower()
        if category_id <= 0:
            raise ValueError("Enter a valid category ID:")
        if not name:
            raise ValueError("Enter a valid category name.")
        if category_type not in self.CATEGORY_TYPES:
            raise ValueError("Category type must be 'income' or 'expense'.")
        if not self.category_repository.get_by_id(category_id, profile_id):
            raise ValueError("this id isn't exist!!!")
        category = Category(
            category_id=category_id,
            name=name,
            category_type=category_type,
            profile_id=profile_id,
        )
        self.category_repository.update(category)
        return category
