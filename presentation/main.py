from spendwise.presentation.cli import CLI
from spendwise.repositories.account_repository import AccountRepository
from spendwise.repositories.budget_repository import BudgetRepository
from spendwise.repositories.category_repository import CategoryRepository
from spendwise.repositories.profile_repository import ProfileRepository
from spendwise.repositories.savings_goal_repository import (
    SavingsGoalRepository,
)
from spendwise.repositories.transaction_repository import TransactionRepository
from spendwise.service.account_service import AccountService
from spendwise.service.budget_service import BudgetService
from spendwise.service.category_service import CategoryService
from spendwise.service.profile_service import ProfileService
from spendwise.service.savings_goal_service import SavingsGoalService
from spendwise.service.transaction_service import TransactionService


def create_cli() -> CLI:
    """Build the command-line application and its dependencies."""
    account_repository = AccountRepository()
    category_repository = CategoryRepository()
    transaction_repository = TransactionRepository(
        account_repository,
        category_repository,
    )
    budget_repository = BudgetRepository(
        category_repository,
    )
    profile_repository = ProfileRepository()
    savings_goal_repository = SavingsGoalRepository()

    profile_service = ProfileService(
        profile_repository,
        dependent_repositories=(
            transaction_repository,
            budget_repository,
            savings_goal_repository,
            account_repository,
            category_repository,
        ),
    )

    return CLI(
        profile_service=profile_service,
        account_service=AccountService(account_repository),
        category_service=CategoryService(category_repository),
        transaction_service=TransactionService(
            transaction_repository,
            account_repository,
            category_repository,
        ),
        budget_service=BudgetService(
            budget_repository,
            category_repository,
            transaction_repository,
        ),
        savings_goal_service=SavingsGoalService(savings_goal_repository),
    )


if __name__ == "__main__":
    create_cli().run()
