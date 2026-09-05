"""Income and expense category routes."""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from domain.spending_category import Category
from webapp.auth import get_current_user, login_required
from webapp.services import category_service

category_bp = Blueprint("category", __name__)

_CATEGORY_TYPES = ("income", "expense")


@category_bp.route("/categories")   
@login_required
def index():
    user = get_current_user()
    categories = category_service.category_repository.get_all(user.user_id)
    return render_template(
        "categories/index.html",
        categories=categories,
        category_types=_CATEGORY_TYPES,
    )


@category_bp.route("/categories/create", methods=["POST"])
@login_required
def create():
    user = get_current_user()
    name = request.form.get("name", "").strip()
    category_type = request.form.get("category_type", "").strip().lower()

    try:
        category_service.add_category(user.user_id, name, category_type)
    except ValueError as error:
        flash(str(error), "danger")
        return redirect(url_for("category.index"))

    flash("Category created successfully.", "success")
    return redirect(url_for("category.index"))


@category_bp.route("/categories/<int:category_id>/update", methods=["POST"])
@login_required
def update(category_id: int):
    user = get_current_user()
    name = request.form.get("name", "").strip()
    category_type = request.form.get("category_type", "").strip().lower()

    try:
        category_service.update(user.user_id, category_id, name, category_type)
    except ValueError as error:
        flash(str(error), "danger")
        return redirect(url_for("category.index"))

    flash("Category updated successfully.", "success")
    return redirect(url_for("category.index"))


@category_bp.route("/categories/<int:category_id>/delete", methods=["POST"])
@login_required
def delete(category_id: int):
    user = get_current_user()
    try:
        category_service.remove(user.user_id, category_id)
    except ValueError as error:
        flash(str(error), "danger")
        return redirect(url_for("category.index"))
    flash("Category deleted successfully.", "success")
    return redirect(url_for("category.index"))
