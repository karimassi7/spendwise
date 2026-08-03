from datetime import date, datetime
from decimal import Decimal

from spendwise.domain.savings_goal import SavingsGoal
from spendwise.repositories.savings_goal_repository import SavingsGoalRepository


class SavingsGoalService:
    """Provide savings goal management operations."""

    def __init__(self, savings_goal_repository: SavingsGoalRepository):
        self.savings_goal_repository = savings_goal_repository

    def add(
        self,
        profile_id: int,
        name: str,
        target_amount: Decimal,
        saved_amount: Decimal,
        deadline: date,
    ) -> SavingsGoal:
        """Add a new record."""
        name = name.strip()
        target_amount = Decimal(str(target_amount))
        saved_amount = Decimal(str(saved_amount))
        if not name:
            raise ValueError("Enter a valid goal name")
        if target_amount <= Decimal(0):
            raise ValueError("Target amount must be greater than zero")
        if saved_amount < Decimal(0):
            raise ValueError("Saved amount cannot be negative")
        if saved_amount > target_amount:
            raise ValueError("Saved amount cannot exceed target amount")
        if not isinstance(deadline, date):
            raise TypeError("Please enter a valid deadline")
        if deadline < datetime.now().astimezone().date():
            raise ValueError("Deadline cannot be in the past")

        goal = SavingsGoal(
            # MySQL replaces this temporary valid ID with AUTO_INCREMENT.
            goal_id=1,
            profile_id=profile_id,
            name=name,
            target_amount=target_amount,
            saved_amount=saved_amount,
            deadline=deadline,
        )

        self.savings_goal_repository.add(goal)
        return goal

    def remove(self, profile_id: int, goal_id: int) -> None:
        """Remove the selected record."""
        if goal_id <= 0:
            raise ValueError("Please enter a valid goal ID.")
        save = self.savings_goal_repository.get_by_id(goal_id, profile_id)
        if not save:
            raise ValueError("This goal ID doesn't exist.")
        self.savings_goal_repository.remove(save)

    def update(
        self,
        profile_id: int,
        goal_id: int,
        name: str,
        target_amount: Decimal,
        saved_amount: Decimal,
        deadline: date,
    ) -> SavingsGoal:
        """Update and persist an existing record."""
        if goal_id <= 0:
            raise ValueError("Please enter a valid goal ID.")
        existing_goal = self.savings_goal_repository.get_by_id(goal_id, profile_id)
        if not existing_goal:
            raise ValueError("This goal ID doesn't exist.")

        name = name.strip()
        target_amount = Decimal(str(target_amount))
        saved_amount = Decimal(str(saved_amount))
        if not name:
            raise ValueError("Enter a valid goal name.")
        if target_amount <= Decimal(0):
            raise ValueError("Target amount must be greater than zero.")
        if saved_amount < Decimal(0):
            raise ValueError("Saved amount cannot be negative.")
        if saved_amount > target_amount:
            raise ValueError("Saved amount cannot exceed target amount.")
        if not isinstance(deadline, date):
            raise TypeError("Please enter a valid deadline.")
        if deadline < datetime.now().astimezone().date():
            raise ValueError("Deadline cannot be in the past.")

        updated_goal = SavingsGoal(
            goal_id=goal_id,
            profile_id=profile_id,
            name=name,
            target_amount=target_amount,
            saved_amount=saved_amount,
            deadline=deadline,
        )

        self.savings_goal_repository.update(updated_goal)

        return updated_goal

    def add_savings(
        self,
        profile_id: int,
        goal_id: int,
        amount: Decimal,
    ) -> SavingsGoal:
        """Add funds to a savings goal."""
        if goal_id <= 0:
            raise ValueError("Please enter a valid goal ID.")

        existing_goal = self.savings_goal_repository.get_by_id(goal_id, profile_id)

        if not existing_goal:
            raise ValueError("This goal ID doesn't exist.")

        amount = Decimal(str(amount))

        if amount <= Decimal(0):
            raise ValueError("Savings amount must be greater than zero.")

        new_saved_amount = existing_goal.saved_amount + amount

        if new_saved_amount > existing_goal.target_amount:
            raise ValueError("Saved amount cannot exceed target amount")

        updated_goal = SavingsGoal(
            goal_id=existing_goal.goal_id,
            profile_id=profile_id,
            name=existing_goal.name,
            target_amount=existing_goal.target_amount,
            saved_amount=new_saved_amount,
            deadline=existing_goal.deadline,
        )

        self.savings_goal_repository.update(updated_goal)

        return updated_goal

    def get_remaining_amount(self, profile_id: int, goal_id: int) -> Decimal:
        """Return the amount remaining."""
        if goal_id <= 0:
            raise ValueError("Please enter a valid goal ID.")

        existing_goal = self.savings_goal_repository.get_by_id(goal_id, profile_id)
        if not existing_goal:
            raise ValueError("This goal ID doesn't exist.")
        remaining = existing_goal.target_amount - existing_goal.saved_amount
        return max(remaining, Decimal(0))

    def get_progress_percentage(self, profile_id: int, goal_id: int) -> Decimal:
        """Return the savings goal progress percentage."""
        if goal_id <= 0:
            raise ValueError("Please enter a valid goal ID.")
        existing_goal = self.savings_goal_repository.get_by_id(goal_id, profile_id)
        if not existing_goal:
            raise ValueError("This goal ID doesn't exist.")
        rate = (existing_goal.saved_amount / existing_goal.target_amount) * Decimal(100)
        return rate.quantize(Decimal("0.01"))

    def is_completed(self, profile_id: int, goal_id: int) -> bool:
        """Return whether the savings goal is complete."""
        if goal_id <= 0:
            raise ValueError("Please enter a valid goal ID.")
        existing_goal = self.savings_goal_repository.get_by_id(goal_id, profile_id)
        if not existing_goal:
            raise ValueError("This goal ID doesn't exist.")
        return existing_goal.saved_amount >= existing_goal.target_amount
