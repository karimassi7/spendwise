MAIN_MENU = {
    "1": "Manage / Switch Profile",
    "2": "Manage Accounts(update)",
    "3": "Show Dashboard",
    "4": "Transactions",
    "5": "Budgets",
    "6": "Savings Goals",
    "7": "Categories",
    "8": "Exit",
}
PROFILE_MENU = {
    "1": "Create Profile",
    "2": "List Profiles",
    "3": "Select Profile",
    "4": "Update Active Profile",
    "5": "Delete Active Profile and Its Data",
    "6": "Back",
}
ACCOUNT_MENU = {
    "1": "create account",
    "2": "update your account",
    "3": "remove account",
    "4": "get your total balance",
    "5": "count your accounts",
    "6": "give your highest balance",
    "7": "give your lowest balance",
    "8": "summary information about all accounts",
    "9": "Back",
}
CATEGORY_MENU = {
    "1": "create category",
    "2": "view categories",
    "3": "update category",
    "4": "remove category",
    "5": "Back",
}
TRANSACTION_MENU = {
    "1": "Add Income",
    "2": "Add Expense",
    "3": "Update Transaction",
    "4": "Delete Transaction",
    "5": "view transactions by date or sort",
    "6": "view transactions by amount(sort)",
    "7": "monthly summary",
    "8": "Back",
}

BUDGET_MENU = {
    "1": "Create Budget",
    "2": "View Budget",
    "3": "update Budget",
    "4": "remove Budget",
    "5": "Back",
}
GOAL_MENU = {
    "1": "Create Savings Goal",
    "2": "View Savings Goals",
    "3": "Add Contribution",
    "4": "Delete Savings Goal",
    "5": "Back",
}

CLEAR_SCREEN = "\033[2J\033[H"


def clear_screen() -> None:
    """Clear the terminal and move the cursor to the top-left corner."""
    print(CLEAR_SCREEN, end="")


def display_main_menu() -> None:
    """Display main menu."""
    clear_screen()
    print("========================================")
    print("       SPENDWISE APP")
    print("========================================")
    for key, value in MAIN_MENU.items():
        print(f"{key}. {value}")
    print("========================================")


def display_profile_menu() -> None:
    """Display profile management options."""
    clear_screen()
    print("========================================")
    print("           PROFILE MENU")
    print("========================================")
    for key, value in PROFILE_MENU.items():
        print(f"{key}. {value}")
    print("========================================")


def display_account_menu() -> None:
    """Display account menu."""
    clear_screen()
    print("========================================")
    print("           ACCOUNT   MENU")
    print("========================================")
    for key, value in ACCOUNT_MENU.items():
        print(f"{key}. {value}")
    print("========================================")


def display_category_menu() -> None:
    """Display category menu."""
    clear_screen()
    print("========================================")
    print("          CATEGORY MENU")
    print("========================================")

    for key, value in CATEGORY_MENU.items():
        print(f"{key}. {value}")

    print("========================================")


def display_transaction_menu() -> None:
    """Display transaction menu."""
    clear_screen()
    print("========================================")
    print("         TRANSACTION MENU")
    print("========================================")

    for key, value in TRANSACTION_MENU.items():
        print(f"{key}. {value}")

    print("========================================")


def display_budget_menu() -> None:
    """Display budget menu."""
    clear_screen()
    print("========================================")
    print("           BUDGET MENU")
    print("========================================")

    for key, value in BUDGET_MENU.items():
        print(f"{key}. {value}")

    print("========================================")


def display_goal_menu() -> None:
    """Display goal menu."""
    clear_screen()
    print("========================================")
    print("       SAVINGS GOALS MENU")
    print("========================================")

    for key, value in GOAL_MENU.items():
        print(f"{key}. {value}")

    print("========================================")
