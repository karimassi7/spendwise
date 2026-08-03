from datetime import date
from decimal import Decimal

from domain.account import Account
from domain.spending_category import Category


class Transaction:
    """Represent a financial transaction."""

    def __init__(
        self,
        transaction_id: int,
        profile_id: int,
        account: Account,
        category: Category,
        amount: Decimal,
        description: str,
        transaction_date: date,
    ):

        if transaction_id <= 0:
            raise ValueError("Enter a valid transaction ID.")
        self.transaction_id = transaction_id

        if profile_id <= 0:
            raise ValueError("Enter a valid profile ID.")
        self.profile_id = profile_id

        if not isinstance(account, Account):
            raise TypeError("Account must be an Account object.")
        self.account = account

        if not isinstance(category, Category):
            raise TypeError("Category must be a Category object.")
        self.category = category

        if account.profile_id != profile_id or category.profile_id != profile_id:
            raise ValueError("Account and category must belong to the profile.")

        amount = Decimal(str(amount))

        if amount <= Decimal(0):
            raise ValueError("Amount must be greater than zero.")
        self.amount = amount

        if not description.strip():
            raise ValueError("Enter a valid description.")
        self.description = description.strip()

        if not isinstance(transaction_date, date):
            raise TypeError("Transaction date must be a date object.")
        self.transaction_date = transaction_date

    def __str__(self):
        return (
            f"ID: {self.transaction_id} | "
            f"Profile ID: {self.profile_id} | "
            f"Account: {self.account.name} | "
            f"Category: {self.category.name} | "
            f"Amount: {self.amount} | "
            f"Description: {self.description} | "
            f"Date: {self.transaction_date}"
        )
