"""Dashboard routes aggregating a user's financial overview."""

from calendar import monthrange
from datetime import date
from decimal import Decimal

from flask import Blueprint, render_template

from webapp.auth import get_current_user, login_required
from webapp.services import (
    account_service,
    budget_service,
    savings_goal_service,
    transaction_service,
)

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    user = get_current_user()
    profile_id = user.user_id

    transactions = transaction_service.transaction_repository.get_all(profile_id)
    accounts = account_service.account_repository.get_all(profile_id)
    budgets = budget_service.budget_repository.get_all(profile_id)
    goals = savings_goal_service.savings_goal_repository.get_all(profile_id)

    total_balance = account_service.get_total_balance(profile_id)

    total_income = Decimal(0)
    total_expenses = Decimal(0)
    for transaction in transactions:
        if transaction.category.category_type.lower() == "income":
            total_income += transaction.amount
        elif transaction.category.category_type.lower() == "expense":
            total_expenses += transaction.amount
    net_amount = total_income - total_expenses

    budget_list = []
    total_budget_remaining = Decimal(0)
    overspent_budgets = 0
    for budget in budgets:
        spent = budget_service.get_spent_amount(profile_id, budget.budget_id)
        remaining = budget_service.get_remaining_amount(profile_id, budget.budget_id)
        usage = budget_service.get_usage_percentage(profile_id, budget.budget_id)
        status = budget_service.get_status(profile_id, budget.budget_id)
        total_budget_remaining += remaining
        if status == "Over budget":
            overspent_budgets += 1
        budget_list.append(
            {
                "id": budget.budget_id,
                "category": budget.category,
                "category_id": budget.category.category_id,
                "limit": budget.limit_amount,
                "spent": spent,
                "remaining": remaining,
                "usage": usage,
                "status": status,
                "from_date": budget.from_date,
                "to_date": budget.to_date,
            }
        )

    goal_list = []
    upcoming_goals = []
    total_target = Decimal(0)
    total_saved = Decimal(0)
    for goal in goals:
        saved = goal.saved_amount
        target = goal.target_amount
        progress = (
            (saved / target) * Decimal(100) if target > 0 else Decimal(0)
        )
        progress = progress.quantize(Decimal("0.01"))
        remaining = max(target - saved, Decimal(0))
        completed = saved >= target
        total_target += target
        total_saved += saved
        goal_list.append(
            {
                "id": goal.goal_id,
                "name": goal.name,
                "target": target,
                "saved": saved,
                "remaining": remaining,
                "progress": progress,
                "deadline": goal.deadline,
                "completed": completed,
            }
        )
        if not completed:
            upcoming_goals.append(
                {
                    "id": goal.goal_id,
                    "name": goal.name,
                    "remaining": remaining,
                    "deadline": goal.deadline,
                    "progress": progress,
                }
            )
    upcoming_goals.sort(key=lambda g: g["deadline"])

    savings_progress = (
        (total_saved / total_target) * Decimal(100)
        if total_target > 0
        else Decimal(0)
    )
    savings_progress = savings_progress.quantize(Decimal("0.01"))

    recent_transactions = sorted(
        transactions,
        key=lambda t: (t.transaction_date, t.transaction_id),
        reverse=True,
    )[:8]

    # Charts: last 6 months income vs expense, plus category spending.
    month_labels, income_series, expense_series = _monthly_series(
        transactions, user.currency
    )
    category_labels, category_series = _category_spending(
        transactions, user.currency
    )

    return render_template(
        "dashboard.html",
        user=user,
        accounts=accounts,
        total_balance=total_balance,
        total_income=total_income,
        total_expenses=total_expenses,
        net_amount=net_amount,
        account_count=len(accounts),
        budget_list=budget_list,
        total_budget_remaining=total_budget_remaining,
        overspent_budgets=overspent_budgets,
        goal_list=goal_list,
        upcoming_goals=upcoming_goals,
        savings_progress=savings_progress,
        recent_transactions=recent_transactions,
        month_labels=month_labels,
        income_series=income_series,
        expense_series=expense_series,
        category_labels=category_labels,
        category_series=category_series,
    )


def _monthly_series(transactions, currency: str):
    today = date.today()
    labels = []
    income_series = []
    expense_series = []
    for offset in range(5, -1, -1):
        year = today.year
        month = today.month - offset
        while month <= 0:
            month += 12
            year -= 1
        labels.append(f"{year}-{month:02d}")
        income = Decimal(0)
        expense = Decimal(0)
        for transaction in transactions:
            t = transaction.transaction_date
            if t.year == year and t.month == month:
                if transaction.category.category_type.lower() == "income":
                    income += transaction.amount
                elif transaction.category.category_type.lower() == "expense":
                    expense += transaction.amount
        income_series.append(float(income))
        expense_series.append(float(expense))
    return labels, income_series, expense_series


def _category_spending(transactions, currency: str):
    totals = {}
    for transaction in transactions:
        if transaction.category.category_type.lower() != "expense":
            continue
        name = transaction.category.name
        totals[name] = totals.get(name, Decimal(0)) + transaction.amount
    ordered = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
    labels = [name for name, _ in ordered]
    series = [float(amount) for _, amount in ordered]
    return labels, series


def month_name(month_number: int) -> str:
    names = {
        1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
        7: "July", 8: "August", 9: "September", 10: "October", 11: "November",
        12: "December",
    }
    return names.get(month_number, str(month_number))
