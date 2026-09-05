"""Sign up, sign in and sign out routes."""

from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from webapp.auth import authenticate_user, get_current_user, register_user

auth_bp = Blueprint("auth", __name__)

_CURRENCIES = ("USD", "LBP")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if get_current_user() is not None:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.", "danger")
        else:
            user = authenticate_user(email, password)
            if user is None:
                flash("Invalid email or password.", "danger")
            else:
                session.clear()
                session["user_id"] = user.user_id
                flash(f"Welcome back, {user.name}!", "success")
                return redirect(url_for("dashboard.index"))

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if get_current_user() is not None:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        currency = request.form.get("currency", "USD").strip().upper()

        try:
            monthly_income = Decimal(request.form.get("monthly_income", "0").strip())
        except (InvalidOperation, ValueError):
            monthly_income = Decimal("0")

        if not name:
            flash("Name is required.", "danger")
        elif currency not in _CURRENCIES:
            flash("Currency must be USD or LBP.", "danger")
        elif monthly_income <= 0:
            flash("Monthly income must be greater than zero.", "danger")
        else:
            try:
                user = register_user(email, password, name, currency, monthly_income)
            except ValueError as error:
                flash(str(error), "danger")
            else:
                session.clear()
                session["user_id"] = user.user_id
                flash("Account created successfully. Welcome to SpendWise!", "success")
                return redirect(url_for("dashboard.index"))

    return render_template("auth/register.html")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("auth.login"))
