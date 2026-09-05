"""Shared service instances used by the web controllers."""

from repositories.account_repository import AccountRepository
from repositories.budget_repository import BudgetRepository
from repositories.category_repository import CategoryRepository
from repositories.profile_repository import ProfileRepository
from repositories.savings_goal_repository import SavingsGoalRepository
from repositories.transaction_repository import TransactionRepository
from service.account_service import AccountService
from service.budget_service import BudgetService
from service.category_service import CategoryService
from service.profile_service import ProfileService
from service.savings_goal_service import SavingsGoalService
from service.transaction_service import TransactionService

account_repository = AccountRepository()
category_repository = CategoryRepository()
transaction_repository = TransactionRepository(
    account_repository,
    category_repository,
)
budget_repository = BudgetRepository(category_repository)
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

account_service = AccountService(account_repository)
category_service = CategoryService(category_repository)
transaction_service = TransactionService(
    transaction_repository,
    account_repository,
    category_repository,
)
budget_service = BudgetService(
    budget_repository,
    category_repository,
    transaction_repository,
)
savings_goal_service = SavingsGoalService(savings_goal_repository)
