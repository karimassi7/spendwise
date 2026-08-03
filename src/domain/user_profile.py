from decimal import Decimal


class UserProfile:
    """Represent the application user and financial preferences."""

    def __init__(self, name: str, currency: str, user_id: int, monthly_income: Decimal):
        if not name.strip():
            raise ValueError("Name cannot be empty.")

        if not currency.strip():
            raise ValueError("Currency cannot be empty.")

        if user_id <= 0:
            raise ValueError("User ID must be greater than zero.")

        monthly_income = Decimal(str(monthly_income))

        if monthly_income < Decimal(0):
            raise ValueError("Monthly income cannot be negative.")

        self.name = name.strip()
        self.currency = currency.strip().upper()
        self.user_id = user_id
        self.monthly_income = monthly_income

    def __str__(self) -> str:
        return (
            f"Name: {self.name} | "
            f"Currency: {self.currency} | "
            f"ID: {self.user_id} | "
            f"Monthly Income: {self.monthly_income} {self.currency}"
        )
