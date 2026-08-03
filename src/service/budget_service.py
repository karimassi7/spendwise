from datetime import date
from decimal import Decimal

from domain.budget import Budget
from repositories.budget_repository import BudgetRepository
from repositories.category_repository import CategoryRepository
from repositories.transaction_repository import TransactionRepository


class BudgetService:
    """Provide budget management and reporting operations."""

    def __init__(
        self,
        budget_repository: BudgetRepository,
        category_repository: CategoryRepository,
        transaction_repository: TransactionRepository,
    ) -> None:
        self.budget_repository = budget_repository
        self.category_repository = category_repository
        self.transaction_repository = transaction_repository

    def add(
        self,
        profile_id: int,
        category_id: int,
        limit_amount: Decimal,
        from_date: date,
        to_date: date,
    ) -> Budget:
        """Add a new record."""
        limit_amount = Decimal(str(limit_amount))

        if category_id <= 0:
            raise ValueError("Enter a valid category ID.")

        if limit_amount <= Decimal(0):
            raise ValueError("Budget limit must be greater than zero.")

        if not isinstance(from_date, date):
            raise TypeError("From date must be a date object.")

        if not isinstance(to_date, date):
            raise TypeError("To date must be a date object.")

        if from_date > to_date:
            raise ValueError("From date cannot be after to date.")

        category = self.category_repository.get_by_id(category_id, profile_id)

        if not category:
            raise ValueError("This category ID doesn't exist.")

        if category.category_type.strip().lower() != "expense":
            raise ValueError("A budget must use an expense category.")

        budget = Budget(
            # MySQL replaces this temporary valid ID with AUTO_INCREMENT.
            budget_id=1,
            profile_id=profile_id,
            category=category,
            limit_amount=limit_amount,
            from_date=from_date,
            to_date=to_date,
        )

        self.budget_repository.add(budget)

        return budget

    def remove(self, profile_id: int, budget_id: int) -> None:
        """Remove the selected record."""
        if budget_id <= 0:
            raise ValueError("Enter a valid budget ID.")

        budget = self.budget_repository.get_by_id(budget_id, profile_id)

        if not budget:
            raise ValueError("This budget ID doesn't exist.")

        self.budget_repository.remove(budget)

    def update(
        self,
        profile_id: int,
        budget_id: int,
        category_id: int,
        limit_amount: Decimal,
        from_date: date,
        to_date: date,
    ) -> Budget:
        """Update and persist an existing record."""
        limit_amount = Decimal(str(limit_amount))

        if budget_id <= 0:
            raise ValueError("Enter a valid budget ID.")

        if category_id <= 0:
            raise ValueError("Enter a valid category ID.")

        if limit_amount <= Decimal(0):
            raise ValueError("Budget limit must be greater than zero.")

        if not isinstance(from_date, date):
            raise TypeError("From date must be a date object.")

        if not isinstance(to_date, date):
            raise TypeError("To date must be a date object.")

        if from_date > to_date:
            raise ValueError("From date cannot be after to date.")

        existing_budget = self.budget_repository.get_by_id(budget_id, profile_id)

        if not existing_budget:
            raise ValueError("This budget ID doesn't exist.")

        category = self.category_repository.get_by_id(category_id, profile_id)

        if not category:
            raise ValueError("This category ID doesn't exist.")

        if category.category_type.strip().lower() != "expense":
            raise ValueError("A budget must use an expense category.")

        updated_budget = Budget(
            budget_id=budget_id,
            profile_id=profile_id,
            category=category,
            limit_amount=limit_amount,
            from_date=from_date,
            to_date=to_date,
        )

        self.budget_repository.update(updated_budget)

        return updated_budget

    def get_spent_amount(
        self,
        profile_id: int,
        budget_id: int,
    ) -> Decimal:
        """Return the amount spent against a budget."""
        if budget_id <= 0:
            raise ValueError("Enter a valid budget ID.")

        budget = self.budget_repository.get_by_id(budget_id, profile_id)

        if not budget:
            raise ValueError("This budget ID doesn't exist.")

        transactions = self.transaction_repository.get_all(profile_id)

        spent_amount = Decimal(0)

        for transaction in transactions:
            category_type = transaction.category.category_type.strip().lower()

            same_category = (
                transaction.category.category_id == budget.category.category_id
            )

            inside_period = (
                budget.from_date <= transaction.transaction_date <= budget.to_date
            )

            if category_type == "expense" and same_category and inside_period:
                spent_amount += transaction.amount

        return spent_amount

    def get_remaining_amount(
        self,
        profile_id: int,
        budget_id: int,
    ) -> Decimal:
        """Return the amount remaining."""
        budget = self.budget_repository.get_by_id(budget_id, profile_id)

        if not budget:
            raise ValueError("This budget ID doesn't exist.")

        spent_amount = self.get_spent_amount(profile_id, budget_id)

        remaining_amount = budget.limit_amount - spent_amount

        return remaining_amount

    def get_usage_percentage(
        self,
        profile_id: int,
        budget_id: int,
    ) -> Decimal:
        """Return the budget usage percentage."""
        budget = self.budget_repository.get_by_id(budget_id, profile_id)

        if not budget:
            raise ValueError("This budget ID doesn't exist.")

        spent_amount = self.get_spent_amount(profile_id, budget_id)

        usage_percentage = (spent_amount / budget.limit_amount) * Decimal(100)

        return usage_percentage.quantize(Decimal("0.01"))

    def get_status(
        self,
        profile_id: int,
        budget_id: int,
    ) -> str:
        """Return a human-readable budget status."""
        usage_percentage = self.get_usage_percentage(profile_id, budget_id)

        if usage_percentage > Decimal(100):
            return "Over budget"

        if usage_percentage == Decimal(100):
            return "Budget limit reached"

        if usage_percentage >= Decimal(80):
            return "Warning: Near budget limit"

        return "Under budget"
