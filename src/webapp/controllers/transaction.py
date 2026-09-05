"""Transaction routes: add income/expense, filters, search, sorting."""

from datetime import date
from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, url_for

from webapp.auth import get_current_user, login_required
from webapp.services import (
    account_service,
    category_service,
    transaction_service,
)

transaction_bp = Blueprint("transaction", __name__)


def _parse_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        return None


@transaction_bp.route("/transactions")
@login_required
def index():
    user = get_current_user()
    profile_id = user.user_id

    transactions = transaction_service.transaction_repository.get_all(profile_id)

    # Search
    search = request.args.get("q", "").strip().lower()
    if search:
        transactions = [
            t
            for t in transactions
            if search in t.description.lower()
            or search in t.category.name.lower()
            or search in t.account.name.lower()
        ]

    # Type filter
    kind = request.args.get("type", "").strip().lower()
    if kind in ("income", "expense"):
        transactions = [
            t
            for t in transactions
            if t.category.category_type.lower() == kind
        ]

    # Category filter
    category_id = request.args.get("category", "").strip()
    if category_id.isdigit():
        transactions = [
            t for t in transactions if t.category.category_id == int(category_id)
        ]

    # Account filter
    account_id = request.args.get("account", "").strip()
    if account_id.isdigit():
        transactions = [
            t for t in transactions if t.account.account_id == int(account_id)
        ]

    # Date range
    from_date = _parse_date(request.args.get("from", ""))
    to_date = _parse_date(request.args.get("to", ""))
    if from_date:
        transactions = [t for t in transactions if t.transaction_date >= from_date]
    if to_date:
        transactions = [t for t in transactions if t.transaction_date <= to_date]

    # Sort
    sort = request.args.get("sort", "").strip().lower()
    order = request.args.get("order", "desc").strip().lower()
    descending = order != "asc"
    if sort == "date":
        transactions = sorted(
            transactions,
            key=lambda t: (t.transaction_date, t.transaction_id),
            reverse=descending,
        )
    elif sort == "amount":
        transactions = sorted(
            transactions, key=lambda t: t.amount, reverse=descending
        )
    else:
        transactions = sorted(
            transactions,
            key=lambda t: (t.transaction_date, t.transaction_id),
            reverse=True,
        )

    accounts = account_service.account_repository.get_all(profile_id)
    categories = category_service.category_repository.get_all(profile_id)
    income_categories = [c for c in categories if c.category_type == "income"]
    expense_categories = [c for c in categories if c.category_type == "expense"]

    return render_template(
        "transactions/index.html",
        transactions=transactions,
        accounts=accounts,
        categories=categories,
        income_categories=income_categories,
        expense_categories=expense_categories,
        currency=user.currency,
        filters={"q": search, "type": kind, "category": category_id,
                 "account": account_id, "from": from_date, "to": to_date,
                 "sort": sort, "order": request.args.get("order", "desc")},
    )


def _add_transaction(kind: str):
    user = get_current_user()
    profile_id = user.user_id

    account = account_service.account_repository.get_by_id(
        int(request.form.get("account_id", 0) or 0), profile_id
    )
    category = category_service.category_repository.get_by_id(
        int(request.form.get("category_id", 0) or 0), profile_id
    )
    if not account:
        flash("Please choose a valid account.", "danger")
        return redirect(url_for("transaction.index"))
    if not category:
        flash("Please choose a valid category.", "danger")
        return redirect(url_for("transaction.index"))

    try:
        amount = Decimal(request.form.get("amount", "0").strip())
    except (InvalidOperation, ValueError):
        amount = Decimal(0)
    description = request.form.get("description", "").strip()
    transaction_date = _parse_date(request.form.get("transaction_date", "")) or date.today()

    try:
        if kind == "income":
            transaction_service.add_income(
                profile_id, account, category, amount, description, transaction_date
            )
        else:
            transaction_service.add_expense(
                profile_id, account, category, amount, description, transaction_date
            )
    except (ValueError, TypeError) as error:
        flash(str(error), "danger")
        return redirect(url_for("transaction.index"))

    flash("Transaction recorded successfully.", "success")
    return redirect(url_for("transaction.index"))


@transaction_bp.route("/transactions/income", methods=["POST"])
@login_required
def add_income():
    return _add_transaction("income")


@transaction_bp.route("/transactions/expense", methods=["POST"])
@login_required
def add_expense():
    return _add_transaction("expense")


@transaction_bp.route("/transactions/<int:transaction_id>/update", methods=["POST"])
@login_required
def update(transaction_id: int):
    user = get_current_user()
    profile_id = user.user_id

    account = account_service.account_repository.get_by_id(
        int(request.form.get("account_id", 0) or 0), profile_id
    )
    category = category_service.category_repository.get_by_id(
        int(request.form.get("category_id", 0) or 0), profile_id
    )
    if not account:
        flash("Please choose a valid account.", "danger")
        return redirect(url_for("transaction.index"))
    if not category:
        flash("Please choose a valid category.", "danger")
        return redirect(url_for("transaction.index"))

    try:
        amount = Decimal(request.form.get("amount", "0").strip())
    except (InvalidOperation, ValueError):
        amount = Decimal(0)
    description = request.form.get("description", "").strip()
    transaction_date = _parse_date(request.form.get("transaction_date", "")) or date.today()

    try:
        transaction_service.update(
            profile_id=profile_id,
            transaction_id=transaction_id,
            account=account,
            category=category,
            amount=amount,
            description=description,
            transaction_date=transaction_date,
        )
    except (ValueError, TypeError) as error:
        flash(str(error), "danger")
        return redirect(url_for("transaction.index"))

    flash("Transaction updated successfully.", "success")
    return redirect(url_for("transaction.index"))


@transaction_bp.route("/transactions/<int:transaction_id>/delete", methods=["POST"])
@login_required
def delete(transaction_id: int):
    user = get_current_user()
    try:
        transaction_service.remove(user.user_id, transaction_id)
    except ValueError as error:
        flash(str(error), "danger")
        return redirect(url_for("transaction.index"))
    flash("Transaction deleted successfully.", "success")
    return redirect(url_for("transaction.index"))
