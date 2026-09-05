"""Account management routes (cash / bank / savings)."""

from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, url_for

from domain.account import Account
from webapp.auth import get_current_user, login_required
from webapp.services import account_service

account_bp = Blueprint("account", __name__)

_ACCOUNT_TYPES = ("cash", "bank", "savings")


@account_bp.route("/accounts")
@login_required
def index():
    user = get_current_user()
    accounts = account_service.account_repository.get_all(user.user_id)
    total_balance = account_service.get_total_balance(user.user_id)
    return render_template(
        "accounts/index.html",
        accounts=accounts,
        total_balance=total_balance,
        account_types=_ACCOUNT_TYPES,
        currency=user.currency,
    )


@account_bp.route("/accounts/create", methods=["POST"])
@login_required
def create():
    user = get_current_user()
    name = request.form.get("name", "").strip()
    account_type = request.form.get("account_type", "").strip().lower()
    try:
        balance = Decimal(request.form.get("balance", "0").strip())
    except (InvalidOperation, ValueError):
        balance = Decimal(0)

    try:
        account_service.create_account(
            profile_id=user.user_id,
            name=name,
            balance=balance,
            account_type=account_type,
        )
    except ValueError as error:
        flash(str(error), "danger")
        return redirect(url_for("account.index"))

    flash("Account created successfully.", "success")
    return redirect(url_for("account.index"))


@account_bp.route("/accounts/<int:account_id>/update", methods=["POST"])
@login_required
def update(account_id: int):
    user = get_current_user()
    name = request.form.get("name", "").strip()
    account_type = request.form.get("account_type", "").strip().lower()
    try:
        balance = Decimal(request.form.get("balance", "0").strip())
    except (InvalidOperation, ValueError):
        balance = Decimal(0)

    try:
        account_service.update(
            profile_id=user.user_id,
            account_id=account_id,
            name=name,
            balance=balance,
            account_type=account_type,
        )
    except ValueError as error:
        flash(str(error), "danger")
        return redirect(url_for("account.index"))

    flash("Account updated successfully.", "success")
    return redirect(url_for("account.index"))


@account_bp.route("/accounts/<int:account_id>/delete", methods=["POST"])
@login_required
def delete(account_id: int):
    user = get_current_user()
    try:
        account_service.remove(user.user_id, account_id)
    except ValueError as error:
        flash(str(error), "danger")
        return redirect(url_for("account.index"))
    flash("Account deleted successfully.", "success")
    return redirect(url_for("account.index"))
