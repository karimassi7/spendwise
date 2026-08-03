from decimal import Decimal

from spendwise.domain.account import Account
from spendwise.repositories.account_repository import AccountRepository


class AccountService:
    """Provide account management operations."""

    ACCOUNT_TYPES = ("cash", "bank", "savings")

    def __init__(self, account_repository: AccountRepository):
        self.account_repository = account_repository

    def create_account(
        self,
        profile_id: int,
        name: str,
        balance: Decimal,
        account_type: str,
    ) -> Account:
        """Create and persist an account."""
        name = name.strip()
        account_type = account_type.strip().lower()
        balance = Decimal(str(balance))

        if not name:
            raise ValueError("Enter a valid account name.")

        if balance < Decimal(0):
            raise ValueError("Balance cannot be negative.")

        if account_type not in self.ACCOUNT_TYPES:
            valid_types = ", ".join(self.ACCOUNT_TYPES)
            raise ValueError(f"Invalid account type. Choose one of: {valid_types}")

        if profile_id <= 0:
            raise ValueError("Enter a valid profile ID.")

        if self.account_repository.get_by_name(name, profile_id):
            raise ValueError("An account with this name already exists.")

        new_account = Account(
            # MySQL replaces this temporary valid ID with AUTO_INCREMENT.
            account_id=1,
            profile_id=profile_id,
            name=name,
            balance=balance,
            account_type=account_type,
        )

        self.account_repository.add(new_account)

        return new_account

    def update(
        self,
        profile_id: int,
        account_id: int,
        name: str,
        balance: Decimal,
        account_type: str,
    ) -> Account:
        """Update and persist an existing record."""
        name = name.strip()
        account_type = account_type.strip().lower()
        balance = Decimal(str(balance))

        if not name:
            raise ValueError("Enter a valid account name.")

        if balance < Decimal(0):
            raise ValueError("Balance cannot be negative.")

        if account_id <= 0:
            raise ValueError("Enter a valid account ID.")

        if account_type not in self.ACCOUNT_TYPES:
            valid_types = ", ".join(self.ACCOUNT_TYPES)
            raise ValueError(f"Invalid account type. Choose one of: {valid_types}")

        if not self.account_repository.get_by_id(account_id, profile_id):
            raise ValueError("This ID doesn't exist.")

        # duplicate name are allowed
        account = Account(
            account_id=account_id,
            profile_id=profile_id,
            name=name,
            balance=balance,
            account_type=account_type,
        )

        self.account_repository.update(account)
        return account

    def remove(self, profile_id: int, account_id: int) -> None:
        """Remove the selected record."""
        if account_id <= 0:
            raise ValueError("Please enter a valid account ID.")

        if not self.account_repository.get_by_id(account_id, profile_id):
            raise ValueError("This account ID doesn't exist.")

        account = self.account_repository.get_by_id(account_id, profile_id)
        self.account_repository.remove(account)

    def get_total_balance(self, profile_id: int) -> Decimal:
        """Return the combined balance of all accounts."""
        accounts = self.account_repository.get_all(profile_id)
        total = Decimal(0)
        for account in accounts:
            total += account.balance
        return total

    def count(self, profile_id: int) -> int:
        """Return the number of accounts."""
        accounts = self.account_repository.get_all(profile_id)
        return len(accounts)

    def highest_balance(self, profile_id: int) -> Account:
        """Return the account with the highest balance."""
        accounts = self.account_repository.get_all(profile_id)

        if not accounts:
            raise ValueError("No accounts found.")

        highest = accounts[0]

        for account in accounts:
            if account.balance > highest.balance:
                highest = account

        return highest

    def lowest_balance(self, profile_id: int) -> Account:
        """Return the account with the lowest balance."""
        accounts = self.account_repository.get_all(profile_id)

        if not accounts:
            raise ValueError("No accounts found.")

        lowest = accounts[0]

        for account in accounts:
            if account.balance < lowest.balance:
                lowest = account

        return lowest

    def summarize(self, profile_id: int) -> dict:
        """
            Returns summary information about all accounts.

        - Number of accounts
        - Total balance
        - Highest balance account
        - Lowest balance account
        """

        return {
            "account_count": self.count(profile_id),
            "total_balance": self.get_total_balance(profile_id),
            "highest_balance_account": self.highest_balance(profile_id),
            "lowest_balance_account": self.lowest_balance(profile_id),
        }
