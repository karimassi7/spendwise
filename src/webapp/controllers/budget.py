"""Per-category budget routes with progress and overspending warnings."""

from datetime import date
from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, url_for

from webapp.auth import get_current_user, login_required
from webapp.services import (
    budget_service,
    category_service,
)

budget_bp = Blueprint("budget", __name__)


def _parse_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        return None


@budget_bp.route("/budgets")
@login_required
def index():
    user = get_current_user()
    profile_id = user.user_id

    budgets = budget_service.budget_repository.get_all(profile_id)
    budget_list = []
    for budget in budgets:
        spent = budget_service.get_spent_amount(profile_id, budget.budget_id)
        remaining = budget_service.get_remaining_amount(profile_id, budget.budget_id)
        usage = budget_service.get_usage_percentage(profile_id, budget.budget_id)
        status = budget_service.get_status(profile_id, budget.budget_id)
        budget_list.append(
            {
                "id": budget.budget_id,
                "category": budget.category,
                "limit": budget.limit_amount,
                "spent": spent,
                "remaining": remaining,
                "usage": usage,
                "status": status,
                "from_date": budget.from_date,
                "to_date": budget.to_date,
            }
        )

    expense_categories = [
        c
        for c in category_service.category_repository.get_all(profile_id)
        if c.category_type == "expense"
    ]

    return render_template(
        "budgets/index.html",
        budgets=budget_list,
        expense_categories=expense_categories,
        currency=user.currency,
    )


@budget_bp.route("/budgets/create", methods=["POST"])
@login_required
def create():
    user = get_current_user()
    profile_id = user.user_id

    try:
        category_id = int(request.form.get("category_id", 0) or 0)
        limit_amount = Decimal(request.form.get("limit_amount", "0").strip())
    except (InvalidOperation, ValueError):
        category_id = 0
        limit_amount = Decimal(0)

    from_date = _parse_date(request.form.get("from_date", ""))
    to_date = _parse_date(request.form.get("to_date", ""))

    try:
        budget_service.add(
            profile_id=profile_id,
            category_id=category_id,
            limit_amount=limit_amount,
            from_date=from_date or date.today(),
            to_date=to_date or date.today(),
        )
    except (ValueError, TypeError) as error:
        flash(str(error), "danger")
        return redirect(url_for("budget.index"))

    flash("Budget created successfully.", "success")
    return redirect(url_for("budget.index"))


@budget_bp.route("/budgets/<int:budget_id>/update", methods=["POST"])
@login_required
def update(budget_id: int):
    user = get_current_user()
    profile_id = user.user_id

    try:
        category_id = int(request.form.get("category_id", 0) or 0)
        limit_amount = Decimal(request.form.get("limit_amount", "0").strip())
    except (InvalidOperation, ValueError):
        category_id = 0
        limit_amount = Decimal(0)

    from_date = _parse_date(request.form.get("from_date", ""))
    to_date = _parse_date(request.form.get("to_date", ""))

    try:
        budget_service.update(
            profile_id=profile_id,
            budget_id=budget_id,
            category_id=category_id,
            limit_amount=limit_amount,
            from_date=from_date or date.today(),
            to_date=to_date or date.today(),
        )
    except (ValueError, TypeError) as error:
        flash(str(error), "danger")
        return redirect(url_for("budget.index"))

    flash("Budget updated successfully.", "success")
    return redirect(url_for("budget.index"))


@budget_bp.route("/budgets/<int:budget_id>/delete", methods=["POST"])
@login_required
def delete(budget_id: int):
    user = get_current_user()
    try:
        budget_service.remove(user.user_id, budget_id)
    except ValueError as error:
        flash(str(error), "danger")
        return redirect(url_for("budget.index"))
    flash("Budget deleted successfully.", "success")
    return redirect(url_for("budget.index"))
