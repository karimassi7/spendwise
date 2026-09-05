from datetime import date
from decimal import Decimal


class SavingsGoal:
    """Represent a savings target and its progress."""

    def __init__(
        self,
        goal_id: int,
        profile_id: int,
        name: str,
        target_amount: Decimal,
        saved_amount: Decimal,
        deadline: date,
    ):
        if goal_id <= 0:
            raise ValueError("Enter a valid goal ID")
        self.goal_id = goal_id

        if profile_id <= 0:
            raise ValueError("Enter a valid profile ID")
        self.profile_id = profile_id

        if not name.strip():
            raise ValueError("Enter a valid goal name")
        self.name = name.strip()

        target_amount = Decimal(str(target_amount))

        if target_amount <= Decimal(0):
            raise ValueError("Target amount must be greater than zero")
        self.target_amount = target_amount

        saved_amount = Decimal(str(saved_amount))

        if saved_amount < Decimal(0):
            raise ValueError("Saved amount cannot be negative")
        self.saved_amount = saved_amount

        if not isinstance(deadline, date):
            raise TypeError("Deadline must be a date object")

        self.deadline = deadline

    def __str__(self) -> str:
        remaining_amount = max(self.target_amount - self.saved_amount, Decimal(0))
        progress_rate = (self.saved_amount / self.target_amount) * Decimal(100)
        is_completed = self.saved_amount >= self.target_amount
        return (
            f"ID: {self.goal_id} | "
            f"Profile ID: {self.profile_id} | "
            f"Goal: {self.name} | "
            f"Target: {self.target_amount} | "
            f"Saved: {self.saved_amount} | "
            f"Remaining: {remaining_amount} | "
            f"Rate: {progress_rate:.2f}% | "
            f"Deadline: {self.deadline} | "
            f"Completed: {is_completed}"
        )
