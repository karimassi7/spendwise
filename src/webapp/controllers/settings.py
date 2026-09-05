"""Profile & settings routes: name, currency, income, and password."""

from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, url_for

from flask import session

from webapp.auth import (
    get_current_user,
    hash_password,
    login_required,
    verify_password,
)
from webapp.services import profile_service

settings_bp = Blueprint("settings", __name__)

_CURRENCIES = ("USD", "LBP")


@settings_bp.route("/settings", methods=["GET", "POST"])
@login_required
def index():
    user = get_current_user()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        currency = request.form.get("currency", user.currency).strip().upper()

        try:
            monthly_income = Decimal(
                request.form.get("monthly_income", "0").strip()
            )
        except (InvalidOperation, ValueError):
            monthly_income = Decimal(0)

        if not name:
            flash("Name is required.", "danger")
        elif currency not in _CURRENCIES:
            flash("Currency must be USD or LBP.", "danger")
        elif monthly_income <= 0:
            flash("Monthly income must be greater than zero.", "danger")
        else:
            try:
                user = profile_service.update_profile(
                    user_id=user.user_id,
                    name=name,
                    currency=currency,
                    monthly_income=monthly_income,
                    email=user.email,
                    password_hash=user.password_hash,
                )
            except ValueError as error:
                flash(str(error), "danger")
            else:
                flash("Profile updated successfully.", "success")

    return render_template(
        "settings/index.html", user=user, currencies=_CURRENCIES
    )


@settings_bp.route("/settings/password", methods=["POST"])
@login_required
def change_password():
    user = get_current_user()

    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not verify_password(current_password, user.password_hash):
        flash("Your current password is incorrect.", "danger")
        return redirect(url_for("settings.index"))

    if len(new_password) < 6:
        flash("New password must be at least 6 characters.", "danger")
        return redirect(url_for("settings.index"))

    if new_password != confirm_password:
        flash("New passwords do not match.", "danger")
        return redirect(url_for("settings.index"))

    profile_service.update_profile(
        user_id=user.user_id,
        name=user.name,
        currency=user.currency,
        monthly_income=user.monthly_income,
        email=user.email,
        password_hash=hash_password(new_password),
    )
    flash("Password changed successfully.", "success")
    return redirect(url_for("settings.index"))


@settings_bp.route("/settings/delete", methods=["POST"])
@login_required
def delete_account():
    user = get_current_user()
    profile_service.remove_profile(user.user_id)

    session.clear()
    flash("Your account and all data were deleted.", "info")
    return redirect(url_for("auth.register"))
