class Category:
    """Represent an income or expense category."""

    CATEGORY_TYPES = ("income", "expense")

    def __init__(
        self, category_id: int, profile_id: int, name: str, category_type: str
    ):
        if category_id <= 0:
            raise ValueError("Enter a valid category ID.")
        self.category_id = category_id

        if profile_id <= 0:
            raise ValueError("Enter a valid profile ID.")
        self.profile_id = profile_id

        if not name.strip():
            raise ValueError("Enter a valid category name.")
        self.name = name.strip()

        category_type = category_type.strip().lower()

        if category_type not in self.CATEGORY_TYPES:
            raise ValueError("Category type must be 'income' or 'expense'.")

        self.category_type = category_type

    def __str__(self):
        return (
            f"ID: {self.category_id} | Profile ID: {self.profile_id} | "
            f"Name: {self.name} | Type: {self.category_type}"
        )
