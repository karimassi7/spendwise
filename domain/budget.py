from datetime import date
from decimal import Decimal

from spendwise.domain.spending_category import Category


class Budget:
    """Represent a spending limit for a category and date range."""

    def __init__(
        self,
        budget_id: int,
        profile_id: int,
        category: Category,
        limit_amount: Decimal,
        from_date: date,
        to_date: date,
    ):
        if budget_id <= 0:
            raise ValueError("Enter a valid budget ID")
        self.budget_id = budget_id

        if profile_id <= 0:
            raise ValueError("Enter a valid profile ID.")
        self.profile_id = profile_id

        if not isinstance(category, Category):
            raise TypeError("Category must be a Category object")

        if category.category_type != "expense":
            raise ValueError("Budget category must be an expense category")

        self.category = category

        if category.profile_id != profile_id:
            raise ValueError("Budget category must belong to the profile")

        limit_amount = Decimal(str(limit_amount))

        if limit_amount <= Decimal(0):
            raise ValueError("Budget limit must be greater than zero")

        self.limit_amount = limit_amount

        if not isinstance(from_date, date):
            raise TypeError("From date must be a date object.")

        if not isinstance(to_date, date):
            raise TypeError("To date must be a date object.")

        if to_date < from_date:
            raise ValueError("To date cannot be earlier than from date")

        self.from_date = from_date
        self.to_date = to_date

    def __str__(self):
        return (
            f"ID: {self.budget_id} | "
            f"Profile ID: {self.profile_id} | "
            f"Category: {self.category.name} | "
            f"Limit: {self.limit_amount} | "
            f"From: {self.from_date} | "
            f"To: {self.to_date}"
        )
