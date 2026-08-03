from decimal import Decimal

from spendwise.domain.account import Account
from spendwise.domain.budget import Budget
from spendwise.domain.savings_goal import SavingsGoal
from spendwise.domain.spending_category import Category
from spendwise.domain.transaction import Transaction
from spendwise.domain.user_profile import UserProfile


def format_money(amount: Decimal, currency: str) -> str:
    """Format an amount using the selected currency."""
    return f"{Decimal(str(amount)):,.2f} {currency.upper()}"


def display_profile(profile: UserProfile) -> None:
    """Display profile."""
    print(f"Name: {profile.name}")
    print(f"Currency: {profile.currency}")
    print(f"Monthly Income: {format_money(profile.monthly_income, profile.currency)}")


def display_accounts(accounts: list[Account], currency: str) -> None:
    """Display accounts."""
    print(f"{'ID':<5}{'Name':<20}{'Type':<12}{'Balance'}")
    for account in accounts:
        print(
            f"{account.account_id:<5}"
            f"{account.name:<20}"
            f"{account.account_type.title():<12}"
            f"{format_money(account.balance, currency)}"
        )


def display_categories(categories: list[Category]) -> None:
    """Display categories."""
    print(f"{'ID':<5}{'Name':<20}{'Type'}")
    for category in categories:
        print(
            f"{category.category_id:<5}"
            f"{category.name:<20}"
            f"{category.category_type.title()}"
        )


def display_transactions(transactions: list[Transaction], currency: str) -> None:
    """Display transactions."""
    print(f"{'ID':<5}{'Date':<13}{'Account':<15}{'Category':<15}{'Type':<12}{'Amount'}")
    for transaction in transactions:
        print(
            f"{transaction.transaction_id:<5}"
            f"{transaction.transaction_date!s:<13}"
            f"{transaction.account.name:<15}"
            f"{transaction.category.name:<15}"
            f"{transaction.category.category_type.title():<12}"
            f"{format_money(transaction.amount, currency)}"
        )


def display_monthly_summary(summary: dict[str, Decimal | int], currency: str) -> None:
    """Display monthly summary."""
    print("Monthly Summary")
    print()
    print(f"Total Income: {format_money(summary['total_income'], currency)}")
    print(f"Total Expense: {format_money(summary['total_expense'], currency)}")
    print(f"Net Amount: {format_money(summary['net_amount'], currency)}")
    print(f"Transactions: {summary['transaction_count']}")


def display_budget(
    budget: Budget,
    spent_amount: Decimal,
    remaining_amount: Decimal,
    usage_percentage: Decimal,
    status: str,
    currency: str,
) -> None:
    """Display budget."""
    print(f"Category: {budget.category.name}")
    print(f"Limit: {format_money(budget.limit_amount, currency)}")
    print(f"Spent: {format_money(spent_amount, currency)}")
    print(f"Remaining: {format_money(remaining_amount, currency)}")
    print(f"Usage: {usage_percentage}%")
    print(f"Status: {status}")


def display_goal(goal: SavingsGoal, currency: str) -> None:
    """Display goal."""
    remaining = goal.target_amount - goal.saved_amount
    progress = (goal.saved_amount / goal.target_amount) * Decimal(100)

    print(f"Goal: {goal.name}")
    print(f"Target: {format_money(goal.target_amount, currency)}")
    print(f"Saved: {format_money(goal.saved_amount, currency)}")
    print(f"Remaining: {format_money(remaining, currency)}")
    print(f"Progress: {progress:.0f}%")


def display_dashboard(
    total_balance: Decimal,
    total_income: Decimal,
    total_expenses: Decimal,
    net_amount: Decimal,
    budget_remaining: Decimal,
    savings_progress: Decimal,
    currency: str,
) -> None:
    """Display dashboard."""
    print("SPENDWISE DASHBOARD")
    print()
    print(f"Total Balance: {format_money(total_balance, currency)}")
    print(f"Total Income: {format_money(total_income, currency)}")
    print(f"Total Expenses: {format_money(total_expenses, currency)}")
    print(f"Net Amount: {format_money(net_amount, currency)}")
    print(f"Budget Remaining: {format_money(budget_remaining, currency)}")
    print(f"Savings Progress: {savings_progress}%")
