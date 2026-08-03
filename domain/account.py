from decimal import Decimal


class Account:
    """Represent a financial account and its current balance."""

    ACCOUNT_TYPES = ("cash", "bank", "savings")

    def __init__(
        self,
        account_id: int,
        profile_id: int,
        name: str,
        balance: Decimal,
        account_type: str,
    ):
        if account_id <= 0:
            raise ValueError("Enter a valid account ID.")
        self.account_id = account_id

        if profile_id <= 0:
            raise ValueError("Enter a valid profile ID.")
        self.profile_id = profile_id

        if not name.strip():
            raise ValueError("Enter a valid account name.")
        self.name = name.strip()

        balance = Decimal(str(balance))
        if balance < Decimal(0):
            raise ValueError("Balance cannot be negative.")
        self.balance = balance

        account_type = account_type.strip().lower()

        if not account_type:
            raise ValueError("Enter a valid account type.")

        if account_type not in self.ACCOUNT_TYPES:
            raise ValueError(
                f"Invalid account type. Choose one of: {', '.join(self.ACCOUNT_TYPES)}"
            )

        self.account_type = account_type

    def __str__(self):
        return (
            f"ID: {self.account_id} | "
            f"Profile ID: {self.profile_id} | "
            f"Name: {self.name} | "
            f"Balance: {self.balance} | "
            f"Type: {self.account_type}"
        )
