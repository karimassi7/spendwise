from datetime import date, datetime
from decimal import Decimal

from domain.account import Account
from domain.spending_category import Category
from domain.transaction import Transaction
from repositories.account_repository import AccountRepository
from repositories.category_repository import CategoryRepository
from repositories.transaction_repository import TransactionRepository


class TransactionService:
    """Provide transaction management and reporting operations."""

    def __init__(
        self,
        transaction_repository: TransactionRepository,
        account_repository: AccountRepository,
        category_repository: CategoryRepository,
    ) -> None:
        self.transaction_repository = transaction_repository
        self.account_repository = account_repository
        self.category_repository = category_repository

    def add_income(
        self,
        profile_id: int,
        account: Account,
        category: Category,
        amount: Decimal,
        description: str,
        transaction_date: date,
    ) -> Transaction:
        """Record an income transaction."""
        return self._add_transaction(
            profile_id,
            account,
            category,
            amount,
            description,
            transaction_date,
            "income",
        )

    def add_expense(
        self,
        profile_id: int,
        account: Account,
        category: Category,
        amount: Decimal,
        description: str,
        transaction_date: date,
    ) -> Transaction:
        """Record an expense transaction."""
        return self._add_transaction(
            profile_id,
            account,
            category,
            amount,
            description,
            transaction_date,
            "expense",
        )

    def _add_transaction(
        self,
        profile_id: int,
        account: Account,
        category: Category,
        amount: Decimal,
        description: str,
        transaction_date: date,
        category_type: str,
    ) -> Transaction:
        if not isinstance(account, Account):
            raise TypeError("Account must be an Account object.")

        if not isinstance(category, Category):
            raise TypeError("Category must be a Category object.")

        existing_account = self.account_repository.get_by_id(
            account.account_id, profile_id
        )

        if not existing_account:
            raise ValueError("This account doesn't exist.")

        existing_category = self.category_repository.get_by_id(
            category.category_id, profile_id
        )

        if not existing_category:
            raise ValueError("This category doesn't exist.")

        if existing_category.category_type.lower() != category_type:
            raise ValueError(
                f"The selected category must be an {category_type} category."
            )

        amount = Decimal(str(amount))

        if amount <= Decimal(0):
            raise ValueError(
                f"{category_type.title()} amount must be greater than zero."
            )

        if category_type == "expense" and amount > existing_account.balance:
            raise ValueError("Insufficient account balance.")

        description = description.strip()

        if not description:
            raise ValueError("Enter a valid description.")

        if not isinstance(transaction_date, date):
            raise TypeError("Transaction date must be a date object.")

        if transaction_date > datetime.now().astimezone().date():
            raise ValueError("Transaction date cannot be in the future.")

        if category_type == "income":
            existing_account.balance += amount
        else:
            existing_account.balance -= amount

        transaction_object = Transaction(
            # MySQL replaces this temporary valid ID with AUTO_INCREMENT.
            transaction_id=1,
            profile_id=profile_id,
            account=existing_account,
            category=existing_category,
            amount=amount,
            description=description,
            transaction_date=transaction_date,
        )

        self.account_repository.update(existing_account)
        self.transaction_repository.add(transaction_object)

        return transaction_object

    def update(
        self,
        profile_id: int,
        transaction_id: int,
        account: Account,
        category: Category,
        amount: Decimal,
        description: str,
        transaction_date: date,
    ) -> Transaction:
        """Update and persist an existing record."""
        if transaction_id <= 0:
            raise ValueError("Enter a valid transaction ID.")

        existing_transaction = self.transaction_repository.get_by_id(
            transaction_id, profile_id
        )

        if not existing_transaction:
            raise ValueError("This transaction doesn't exist.")

        if not isinstance(account, Account):
            raise TypeError("Account must be an Account object.")

        if not isinstance(category, Category):
            raise TypeError("Category must be a Category object.")

        current_account = self.account_repository.get_by_id(
            account.account_id, profile_id
        )

        if not current_account:
            raise ValueError("This account doesn't exist.")

        current_category = self.category_repository.get_by_id(
            category.category_id, profile_id
        )

        if not current_category:
            raise ValueError("This category doesn't exist.")

        category_type = current_category.category_type.lower()

        if category_type not in ("income", "expense"):
            raise ValueError("Category type must be either income or expense.")

        amount = Decimal(str(amount))

        if amount <= Decimal(0):
            raise ValueError("Amount must be greater than zero.")

        description = description.strip()

        if not description:
            raise ValueError("Enter a valid description.")

        if not isinstance(transaction_date, date):
            raise TypeError("Transaction date must be a date object.")

        if transaction_date > datetime.now().astimezone().date():
            raise ValueError("Transaction date cannot be in the future.")

        old_account = self.account_repository.get_by_id(
            existing_transaction.account.account_id, profile_id
        )

        if not old_account:
            raise ValueError("The original transaction account doesn't exist.")

        old_category_type = existing_transaction.category.category_type.lower()

        # Cancel the effect of the old transaction.
        if old_category_type == "income":
            old_account_balance = old_account.balance - existing_transaction.amount

            if old_account_balance < Decimal(0):
                raise ValueError(
                    "Cannot update this income transaction because "
                    "reversing it would make the account balance "
                    "negative."
                )

        elif old_category_type == "expense":
            old_account_balance = old_account.balance + existing_transaction.amount

        else:
            raise ValueError("The original transaction has an invalid category type.")

        same_account = old_account.account_id == current_account.account_id

        if same_account:
            available_balance = old_account_balance
        else:
            available_balance = current_account.balance

        # Apply the effect of the new transaction.
        if category_type == "income":
            new_account_balance = available_balance + amount

        else:
            if amount > available_balance:
                raise ValueError("Insufficient account balance.")

            new_account_balance = available_balance - amount

        updated_transaction = Transaction(
            transaction_id=transaction_id,
            profile_id=profile_id,
            account=current_account,
            category=current_category,
            amount=amount,
            description=description,
            transaction_date=transaction_date,
        )

        if same_account:
            old_account.balance = new_account_balance

            updated_transaction.account = old_account

            self.account_repository.update(old_account)

        else:
            # Restore the old account balance.
            old_account.balance = old_account_balance
            self.account_repository.update(old_account)

            # Apply the transaction to the new account.
            current_account.balance = new_account_balance
            self.account_repository.update(current_account)

        self.transaction_repository.update(updated_transaction)

        return updated_transaction

    def remove(self, profile_id: int, transaction_id: int) -> None:
        """Remove the selected record."""
        if transaction_id <= 0:
            raise ValueError("Enter a valid transaction ID.")

        existing_transaction = self.transaction_repository.get_by_id(
            transaction_id, profile_id
        )

        if not existing_transaction:
            raise ValueError("This transaction doesn't exist.")

        account = self.account_repository.get_by_id(
            existing_transaction.account.account_id, profile_id
        )

        if not account:
            raise ValueError("The transaction account doesn't exist.")

        category_type = existing_transaction.category.category_type.lower()

        # Reverse the effect of the transaction.
        if category_type == "income":
            new_balance = account.balance - existing_transaction.amount

            if new_balance < Decimal(0):
                raise ValueError(
                    "Cannot remove this income transaction because "
                    "the account balance would become negative."
                )

            account.balance = new_balance

        elif category_type == "expense":
            account.balance += existing_transaction.amount

        else:
            raise ValueError("The transaction has an invalid category type.")

        self.account_repository.update(account)
        self.transaction_repository.remove(existing_transaction)

    def sort_by_date(
        self,
        profile_id: int,
        descending: bool = False,
    ) -> list[Transaction]:
        """Return transactions sorted by date."""
        transactions = self.transaction_repository.get_all(profile_id)

        return sorted(
            transactions,
            key=lambda transaction: transaction.transaction_date,
            reverse=descending,
        )

    def sort_by_amount(
        self,
        profile_id: int,
        descending: bool = False,
    ) -> list[Transaction]:
        """Return transactions sorted by amount."""
        transactions = self.transaction_repository.get_all(profile_id)

        return sorted(
            transactions,
            key=lambda transaction: transaction.amount,
            reverse=descending,
        )

    def monthly_summary(
        self,
        profile_id: int,
        year: int,
        month: int,
    ) -> dict:
        """Return transaction totals for a calendar month."""
        if year <= 0:
            raise ValueError("Enter a valid year.")

        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12.")

        transactions = self.transaction_repository.get_all(profile_id)

        monthly_transactions = [
            transaction
            for transaction in transactions
            if transaction.transaction_date.year == year
            and transaction.transaction_date.month == month
        ]

        total_income = Decimal(0)
        total_expense = Decimal(0)

        for transaction in monthly_transactions:
            category_type = transaction.category.category_type.strip().lower()

            if category_type == "income":
                total_income += transaction.amount

            elif category_type == "expense":
                total_expense += transaction.amount

        return {
            "year": year,
            "month": month,
            "total_income": total_income,
            "total_expense": total_expense,
            "net_amount": total_income - total_expense,
            "transaction_count": len(monthly_transactions),
        }
