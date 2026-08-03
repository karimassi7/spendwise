from datetime import date
from decimal import Decimal, InvalidOperation

from spendwise.service.account_service import AccountService
from spendwise.service.budget_service import BudgetService
from spendwise.service.category_service import CategoryService
from spendwise.service.profile_service import ProfileService
from spendwise.service.savings_goal_service import SavingsGoalService
from spendwise.service.transaction_service import TransactionService

from .formatter import (
    display_accounts,
    display_budget,
    display_categories,
    display_dashboard,
    display_goal,
    display_monthly_summary,
    display_profile,
    display_transactions,
    format_money,
)
from .menu import (
    display_account_menu,
    display_budget_menu,
    display_category_menu,
    display_goal_menu,
    display_main_menu,
    display_profile_menu,
    display_transaction_menu,
)


class CLI:
    """Provide the interactive SpendWise command-line interface"""

    def __init__(
        self,
        profile_service: ProfileService,
        account_service: AccountService,
        category_service: CategoryService,
        transaction_service: TransactionService,
        budget_service: BudgetService,
        savings_goal_service: SavingsGoalService,
    ) -> None:
        self.profile_service = profile_service
        self.account_service = account_service
        self.category_service = category_service
        self.transaction_service = transaction_service
        self.budget_service = budget_service
        self.savings_goal_service = savings_goal_service
        self.active_profile_id: int | None = None

    def run(self) -> None:
        """Run the interactive command-line application."""
        while True:
            display_main_menu()
            if self.active_profile_id is not None:
                active_profile = self.profile_service.get_profile(
                    self.active_profile_id
                )
                print(
                    f"Active profile: {active_profile.name} "
                    f"(ID {active_profile.user_id})"
                )
            choice = input("Choose an option: ").strip()

            try:
                if choice == "1":
                    self.profile_menu()

                elif choice == "2":
                    self._require_active_profile()
                    self.account_menu()

                elif choice == "3":
                    self._require_active_profile()
                    self.show_dashboard()

                elif choice == "4":
                    self._require_active_profile()
                    self.transaction_menu()

                elif choice == "5":
                    self._require_active_profile()
                    self.budget_menu()

                elif choice == "6":
                    self._require_active_profile()
                    self.goal_menu()

                elif choice == "7":
                    self._require_active_profile()
                    self.category_menu()

                elif choice == "8":
                    break

                else:
                    print("Invalid option.")

            except (ValueError, TypeError, InvalidOperation) as error:
                print(f"Error: {error}")

    def profile_menu(self) -> None:
        """Run the interactive profile menu."""
        first_render = True
        while True:
            if not first_render:
                input("\nPress Enter to continue...")
            first_render = False
            display_profile_menu()
            choice = input("Choose an option: ").strip()
            try:
                if choice == "6":
                    return
                if choice == "1":
                    profile = self.profile_service.create_profile(
                        name=input("Enter name: ").strip(),
                        currency=input("Enter currency: ").strip(),
                        monthly_income=Decimal(input("Enter monthly income: ").strip()),
                    )
                    self.active_profile_id = profile.user_id
                    print("Profile created and selected successfully.")
                    display_profile(profile)
                elif choice == "2":
                    profiles = self.profile_service.get_profiles()
                    if not profiles:
                        print("No profiles found.")
                    for profile in profiles:
                        marker = (
                            " (active)"
                            if profile.user_id == self.active_profile_id
                            else ""
                        )
                        print(f"{profile}{marker}")
                elif choice == "3":
                    profile_id = int(input("Enter profile ID: ").strip())
                    profile = self.profile_service.get_profile(profile_id)
                    self.active_profile_id = profile.user_id
                    print(f"Selected profile: {profile.name}")
                elif choice == "4":
                    profile_id = self._require_active_profile()
                    profile = self.profile_service.update_profile(
                        user_id=profile_id,
                        name=input("Enter new name: ").strip(),
                        currency=input("Enter new currency: ").strip(),
                        monthly_income=Decimal(
                            input("Enter new monthly income: ").strip()
                        ),
                    )
                    print("Profile updated successfully.")
                    display_profile(profile)
                elif choice == "5":
                    profile_id = self._require_active_profile()
                    confirmation = (
                        input(
                            "Delete this profile and all its financial data? (yes/no): "
                        )
                        .strip()
                        .lower()
                    )
                    if confirmation == "yes":
                        self.profile_service.remove_profile(profile_id)
                        self.active_profile_id = None
                        print("Profile and its financial data were deleted.")
                else:
                    print("Invalid option.")
            except (ValueError, TypeError, InvalidOperation) as error:
                print(f"Error: {error}")

    def _require_active_profile(self) -> int:
        """Return the active profile ID or require profile selection."""
        if self.active_profile_id is None:
            profiles = self.profile_service.get_profiles()
            if len(profiles) == 1:
                self.active_profile_id = profiles[0].user_id
            else:
                raise ValueError(
                    "Select a profile from the profile menu before continuing."
                )
        self.profile_service.get_profile(self.active_profile_id)
        return self.active_profile_id

    def account_menu(self) -> None:
        """Run the interactive account menu."""
        first_render = True
        while True:
            if not first_render:
                input("\nPress Enter to continue...")
            first_render = False
            display_account_menu()
            choice = input("Choose an option: ").strip()

            try:
                if choice == "9":
                    break

                if choice not in {"1", "2", "3", "4", "5", "6", "7", "8"}:
                    print("Invalid option.")
                    continue

                profile_id = self._require_active_profile()
                currency = self.profile_service.get_profile(profile_id).currency

                if choice == "1":
                    name = input("Enter account name: ").strip()
                    balance = Decimal(input("Enter account balance: ").strip())
                    account_type = input(
                        "Enter account type (cash, bank, savings): "
                    ).strip()

                    account = self.account_service.create_account(
                        profile_id=profile_id,
                        name=name,
                        balance=balance,
                        account_type=account_type,
                    )

                    print("Account created successfully.")
                    display_accounts([account], currency)

                elif choice == "2":
                    account_id = int(input("Enter account ID: ").strip())
                    name = input("Enter new account name: ").strip()
                    balance = Decimal(input("Enter new balance: ").strip())
                    account_type = input(
                        "Enter new type (cash, bank, savings): "
                    ).strip()

                    account = self.account_service.update(
                        profile_id=profile_id,
                        account_id=account_id,
                        name=name,
                        balance=balance,
                        account_type=account_type,
                    )

                    print("Account updated successfully.")
                    display_accounts([account], currency)

                elif choice == "3":
                    account_id = int(input("Enter account ID: ").strip())
                    self.account_service.remove(profile_id, account_id)
                    print("Account removed successfully.")

                elif choice == "4":
                    total = self.account_service.get_total_balance(profile_id)
                    print(f"Total Balance: {format_money(total, currency)}")

                elif choice == "5":
                    count = self.account_service.count(profile_id)
                    print(f"Number of Accounts: {count}")

                elif choice == "6":
                    account = self.account_service.highest_balance(profile_id)
                    print("Highest Balance Account:")
                    display_accounts([account], currency)

                elif choice == "7":
                    account = self.account_service.lowest_balance(profile_id)
                    print("Lowest Balance Account:")
                    display_accounts([account], currency)

                elif choice == "8":
                    summary = self.account_service.summarize(profile_id)
                    print(f"Number of Accounts: {summary['account_count']}")
                    print(
                        f"Total Balance: "
                        f"{format_money(summary['total_balance'], currency)}"
                    )
                    print("Highest Balance Account:")
                    display_accounts(
                        [summary["highest_balance_account"]],
                        currency,
                    )
                    print("Lowest Balance Account:")
                    display_accounts(
                        [summary["lowest_balance_account"]],
                        currency,
                    )

            except (ValueError, TypeError, InvalidOperation) as error:
                print(f"Error: {error}")

    def category_menu(self) -> None:
        """Run the interactive category menu."""
        first_render = True
        while True:
            if not first_render:
                input("\nPress Enter to continue...")
            first_render = False
            display_category_menu()
            choice = input("Choose an option: ").strip()

            try:
                if choice == "5":
                    break

                if choice not in {"1", "2", "3", "4"}:
                    print("Invalid option.")
                    continue

                if choice == "1":
                    category = self.category_service.add_category(
                        profile_id=self._require_active_profile(),
                        name=input("Enter category name: ").strip(),
                        category_type=input(
                            "Enter category type (income, expense): "
                        ).strip(),
                    )
                    print("Category created successfully.")
                    display_categories([category])

                elif choice == "2":
                    categories = self.category_service.category_repository.get_all(
                        self._require_active_profile()
                    )
                    if not categories:
                        print("No categories found.")
                        continue

                    display_categories(categories)

                elif choice == "3":
                    category = self.category_service.update(
                        profile_id=self._require_active_profile(),
                        category_id=int(input("Enter category ID: ")),
                        name=input("Enter new category name: ").strip(),
                        category_type=input(
                            "Enter new type (income, expense): "
                        ).strip(),
                    )
                    print("Category updated successfully.")
                    display_categories([category])

                elif choice == "4":
                    category_id = int(input("Enter category ID: "))
                    self.category_service.remove(
                        self._require_active_profile(), category_id
                    )
                    print("Category removed successfully.")

            except (ValueError, TypeError, InvalidOperation) as error:
                print(f"Error: {error}")

    def show_dashboard(self) -> None:
        """Show dashboard."""
        profile_id = self._require_active_profile()
        profile = self.profile_service.get_profile(profile_id)
        currency = profile.currency

        total_balance = self.account_service.get_total_balance(profile_id)

        transactions = self.transaction_service.transaction_repository.get_all(
            profile_id
        )
        total_income = Decimal(0)
        total_expenses = Decimal(0)

        for transaction in transactions:
            category_type = transaction.category.category_type.lower()

            if category_type == "income":
                total_income += transaction.amount
            elif category_type == "expense":
                total_expenses += transaction.amount

        net_amount = total_income - total_expenses

        budgets = self.budget_service.budget_repository.get_all(profile_id)
        budget_remaining = Decimal(0)

        for budget in budgets:
            budget_remaining += self.budget_service.get_remaining_amount(
                profile_id, budget.budget_id
            )

        goals = self.savings_goal_service.savings_goal_repository.get_all(profile_id)
        total_target = Decimal(0)
        total_saved = Decimal(0)

        for goal in goals:
            total_target += goal.target_amount
            total_saved += goal.saved_amount

        if total_target > Decimal(0):
            savings_progress = (total_saved / total_target) * Decimal(100)
            savings_progress = savings_progress.quantize(Decimal("0.01"))
        else:
            savings_progress = Decimal(0)

        display_dashboard(
            total_balance,
            total_income,
            total_expenses,
            net_amount,
            budget_remaining,
            savings_progress,
            currency,
        )

    def transaction_menu(self) -> None:
        """Run the interactive transaction menu."""
        first_render = True
        while True:
            if not first_render:
                input("\nPress Enter to continue...")
            first_render = False
            display_transaction_menu()
            choice = input("plz enter your option").strip()
            try:
                if choice == "8":
                    break
                if choice not in {"1", "2", "3", "4", "5", "6", "7"}:
                    print("Invalid option.")
                    continue

                profile_id = self._require_active_profile()
                currency = self.profile_service.get_profile(profile_id).currency

                if choice == "1":
                    account_id = int(input("Enter account ID: "))
                    account = self.account_service.account_repository.get_by_id(
                        account_id, profile_id
                    )
                    if not account:
                        raise ValueError("Account ID does not exist.")

                    category_id = int(input("Enter category ID: "))
                    category = self.category_service.category_repository.get_by_id(
                        category_id, profile_id
                    )
                    if not category:
                        raise ValueError("Category ID does not exist.")
                    if category.category_type != "income":
                        raise ValueError("Choose an income category.")

                    transaction = self.transaction_service.add_income(
                        profile_id,
                        account,
                        category,
                        Decimal(input("Enter amount: ").strip()),
                        input("Enter description: ").strip(),
                        date.fromisoformat(input("Enter date (YYYY-MM-DD): ").strip()),
                    )
                    print("Income added successfully.")
                    display_transactions([transaction], currency)

                elif choice == "2":
                    account_id = int(input("Enter account ID: "))
                    account = self.account_service.account_repository.get_by_id(
                        account_id, profile_id
                    )
                    if not account:
                        raise ValueError("Account ID does not exist.")

                    category_id = int(input("Enter category ID: "))
                    category = self.category_service.category_repository.get_by_id(
                        category_id, profile_id
                    )
                    if not category:
                        raise ValueError("Category ID does not exist.")
                    if category.category_type != "expense":
                        raise ValueError("Choose an expense category.")

                    transaction = self.transaction_service.add_expense(
                        profile_id,
                        account,
                        category,
                        Decimal(input("Enter amount: ").strip()),
                        input("Enter description: ").strip(),
                        date.fromisoformat(input("Enter date (YYYY-MM-DD): ").strip()),
                    )
                    print("Expense added successfully.")
                    display_transactions([transaction], currency)

                elif choice == "3":
                    transaction_id = int(input("Enter transaction ID: "))
                    account_id = int(input("Enter account ID: "))
                    account = self.account_service.account_repository.get_by_id(
                        account_id, profile_id
                    )
                    if not account:
                        raise ValueError("Account ID does not exist.")

                    category_id = int(input("Enter category ID: "))
                    category = self.category_service.category_repository.get_by_id(
                        category_id, profile_id
                    )
                    if not category:
                        raise ValueError("Category ID does not exist.")

                    amount = Decimal(input("Enter amount: ").strip())
                    description = input("Enter description: ").strip()
                    transaction_date = date.fromisoformat(
                        input("Enter date (YYYY-MM-DD): ").strip()
                    )

                    updated_transaction = self.transaction_service.update(
                        profile_id=profile_id,
                        transaction_id=transaction_id,
                        account=account,
                        category=category,
                        amount=amount,
                        description=description,
                        transaction_date=transaction_date,
                    )
                    print("Transaction updated successfully.")
                    display_transactions(
                        [updated_transaction],
                        currency,
                    )

                elif choice == "4":
                    transaction_id = int(input("Enter transaction ID: "))
                    self.transaction_service.remove(profile_id, transaction_id)
                    print("Transaction deleted successfully.")

                elif choice == "5":
                    order = (
                        input("Enter A for ascending or D for descending: ")
                        .strip()
                        .lower()
                    )
                    if order not in {"a", "d"}:
                        raise ValueError("Choose A or D.")

                    transactions = self.transaction_service.sort_by_date(
                        profile_id, descending=order == "d"
                    )
                    display_transactions(transactions, currency)

                elif choice == "6":
                    order = (
                        input("Enter A for ascending or D for descending: ")
                        .strip()
                        .lower()
                    )
                    if order not in {"a", "d"}:
                        raise ValueError("Choose A or D.")

                    transactions = self.transaction_service.sort_by_amount(
                        profile_id, descending=order == "d"
                    )
                    display_transactions(transactions, currency)

                elif choice == "7":
                    year = int(input("Enter year: "))
                    month = int(input("Enter month (1-12): "))
                    summary = self.transaction_service.monthly_summary(
                        profile_id,
                        year,
                        month,
                    )
                    display_monthly_summary(summary, currency)

            except (ValueError, TypeError, InvalidOperation) as error:
                print(f"Error: {error}")

    def budget_menu(self) -> None:
        """Run the interactive budget menu."""
        first_render = True
        while True:
            if not first_render:
                input("\nPress Enter to continue...")
            first_render = False
            display_budget_menu()
            choice = input("Choose an option: ").strip()

            try:
                if choice == "5":
                    break

                if choice not in {"1", "2", "3", "4"}:
                    print("Invalid option.")
                    continue

                profile_id = self._require_active_profile()
                currency = self.profile_service.get_profile(profile_id).currency

                if choice == "1":
                    budget = self.budget_service.add(
                        profile_id=profile_id,
                        category_id=int(input("Enter category ID: ")),
                        limit_amount=Decimal(input("Enter budget limit: ").strip()),
                        from_date=date.fromisoformat(
                            input("Enter start date (YYYY-MM-DD): ").strip()
                        ),
                        to_date=date.fromisoformat(
                            input("Enter end date (YYYY-MM-DD): ").strip()
                        ),
                    )
                    print("Budget created successfully.")
                    display_budget(
                        budget,
                        self.budget_service.get_spent_amount(
                            profile_id, budget.budget_id
                        ),
                        self.budget_service.get_remaining_amount(
                            profile_id, budget.budget_id
                        ),
                        self.budget_service.get_usage_percentage(
                            profile_id, budget.budget_id
                        ),
                        self.budget_service.get_status(profile_id, budget.budget_id),
                        currency,
                    )

                elif choice == "2":
                    budgets = self.budget_service.budget_repository.get_all(profile_id)
                    if not budgets:
                        print("No budgets found.")
                        continue

                    for budget in budgets:
                        print(f"\nBudget ID: {budget.budget_id}")
                        print(f"Period: {budget.from_date} to {budget.to_date}")
                        display_budget(
                            budget,
                            self.budget_service.get_spent_amount(
                                profile_id, budget.budget_id
                            ),
                            self.budget_service.get_remaining_amount(
                                profile_id, budget.budget_id
                            ),
                            self.budget_service.get_usage_percentage(
                                profile_id, budget.budget_id
                            ),
                            self.budget_service.get_status(
                                profile_id, budget.budget_id
                            ),
                            currency,
                        )

                elif choice == "3":
                    budget = self.budget_service.update(
                        profile_id=profile_id,
                        budget_id=int(input("Enter budget ID: ")),
                        category_id=int(input("Enter category ID: ")),
                        limit_amount=Decimal(input("Enter budget limit: ").strip()),
                        from_date=date.fromisoformat(
                            input("Enter start date (YYYY-MM-DD): ").strip()
                        ),
                        to_date=date.fromisoformat(
                            input("Enter end date (YYYY-MM-DD): ").strip()
                        ),
                    )
                    print("Budget updated successfully.")
                    display_budget(
                        budget,
                        self.budget_service.get_spent_amount(
                            profile_id, budget.budget_id
                        ),
                        self.budget_service.get_remaining_amount(
                            profile_id, budget.budget_id
                        ),
                        self.budget_service.get_usage_percentage(
                            profile_id, budget.budget_id
                        ),
                        self.budget_service.get_status(profile_id, budget.budget_id),
                        currency,
                    )

                elif choice == "4":
                    budget_id = int(input("Enter budget ID: "))
                    self.budget_service.remove(profile_id, budget_id)
                    print("Budget deleted successfully.")

            except (ValueError, TypeError, InvalidOperation) as error:
                print(f"Error: {error}")

    def goal_menu(self) -> None:
        """Run the interactive goal menu."""
        first_render = True
        while True:
            if not first_render:
                input("\nPress Enter to continue...")
            first_render = False
            display_goal_menu()
            choice = input("Choose an option: ").strip()

            try:
                if choice == "5":
                    break

                if choice not in {"1", "2", "3", "4"}:
                    print("Invalid option.")
                    continue

                profile_id = self._require_active_profile()
                currency = self.profile_service.get_profile(profile_id).currency

                if choice == "1":
                    goal = self.savings_goal_service.add(
                        profile_id=profile_id,
                        name=input("Enter goal name: ").strip(),
                        target_amount=Decimal(input("Enter target amount: ").strip()),
                        saved_amount=Decimal(
                            input("Enter initial saved amount: ").strip()
                        ),
                        deadline=date.fromisoformat(
                            input("Enter deadline (YYYY-MM-DD): ").strip()
                        ),
                    )
                    print("Savings goal created successfully.")
                    print(f"Goal ID: {goal.goal_id}")
                    print(f"Deadline: {goal.deadline}")
                    display_goal(goal, currency)

                elif choice == "2":
                    goals = self.savings_goal_service.savings_goal_repository.get_all(
                        profile_id
                    )
                    if not goals:
                        print("No savings goals found.")
                        continue

                    for goal in goals:
                        print(f"\nGoal ID: {goal.goal_id}")
                        print(f"Deadline: {goal.deadline}")
                        display_goal(goal, currency)

                elif choice == "3":
                    goal = self.savings_goal_service.add_savings(
                        profile_id=profile_id,
                        goal_id=int(input("Enter goal ID: ")),
                        amount=Decimal(input("Enter contribution amount: ").strip()),
                    )
                    print("Contribution added successfully.")
                    print(f"Goal ID: {goal.goal_id}")
                    print(f"Deadline: {goal.deadline}")
                    display_goal(goal, currency)

                elif choice == "4":
                    goal_id = int(input("Enter goal ID: "))
                    self.savings_goal_service.remove(profile_id, goal_id)
                    print("Savings goal deleted successfully.")

            except (ValueError, TypeError, InvalidOperation) as error:
                print(f"Error: {error}")

