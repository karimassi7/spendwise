"""Savings goal routes: targets, deadlines, contributions, completion."""

from datetime import date
from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, url_for

from webapp.auth import get_current_user, login_required
from webapp.services import savings_goal_service

goal_bp = Blueprint("goal", __name__)


def _parse_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        return None


@goal_bp.route("/goals")
@login_required
def index():
    user = get_current_user()
    profile_id = user.user_id
    goals = savings_goal_service.savings_goal_repository.get_all(profile_id)

    goal_list = []
    for goal in goals:
        progress = savings_goal_service.get_progress_percentage(profile_id, goal.goal_id)
        remaining = savings_goal_service.get_remaining_amount(profile_id, goal.goal_id)
        goal_list.append(
            {
                "id": goal.goal_id,
                "name": goal.name,
                "target": goal.target_amount,
                "saved": goal.saved_amount,
                "remaining": remaining,
                "progress": progress,
                "deadline": goal.deadline,
                "completed": savings_goal_service.is_completed(profile_id, goal.goal_id),
            }
        )

    completed_count = sum(1 for g in goal_list if g["completed"])

    return render_template(
        "goals/index.html",
        goals=goal_list,
        completed_count=completed_count,
        currency=user.currency,
    )


@goal_bp.route("/goals/create", methods=["POST"])
@login_required
def create():
    user = get_current_user()
    profile_id = user.user_id
    name = request.form.get("name", "").strip()

    try:
        target_amount = Decimal(request.form.get("target_amount", "0").strip())
        saved_amount = Decimal(request.form.get("saved_amount", "0").strip())
    except (InvalidOperation, ValueError):
        target_amount = Decimal(0)
        saved_amount = Decimal(0)

    deadline = _parse_date(request.form.get("deadline", "")) or date.today()

    try:
        savings_goal_service.add(
            profile_id=profile_id,
            name=name,
            target_amount=target_amount,
            saved_amount=saved_amount,
            deadline=deadline,
        )
    except (ValueError, TypeError) as error:
        flash(str(error), "danger")
        return redirect(url_for("goal.index"))

    flash("Savings goal created successfully.", "success")
    return redirect(url_for("goal.index"))


@goal_bp.route("/goals/<int:goal_id>/update", methods=["POST"])
@login_required
def update(goal_id: int):
    user = get_current_user()
    profile_id = user.user_id
    name = request.form.get("name", "").strip()

    try:
        target_amount = Decimal(request.form.get("target_amount", "0").strip())
        saved_amount = Decimal(request.form.get("saved_amount", "0").strip())
    except (InvalidOperation, ValueError):
        target_amount = Decimal(0)
        saved_amount = Decimal(0)

    deadline = _parse_date(request.form.get("deadline", "")) or date.today()

    try:
        savings_goal_service.update(
            profile_id=profile_id,
            goal_id=goal_id,
            name=name,
            target_amount=target_amount,
            saved_amount=saved_amount,
            deadline=deadline,
        )
    except (ValueError, TypeError) as error:
        flash(str(error), "danger")
        return redirect(url_for("goal.index"))

    flash("Savings goal updated successfully.", "success")
    return redirect(url_for("goal.index"))


@goal_bp.route("/goals/<int:goal_id>/contribute", methods=["POST"])
@login_required
def contribute(goal_id: int):
    user = get_current_user()
    try:
        amount = Decimal(request.form.get("amount", "0").strip())
    except (InvalidOperation, ValueError):
        amount = Decimal(0)

    try:
        savings_goal_service.add_savings(
            profile_id=user.user_id,
            goal_id=goal_id,
            amount=amount,
        )
    except ValueError as error:
        flash(str(error), "danger")
        return redirect(url_for("goal.index"))

    flash("Contribution added successfully.", "success")
    return redirect(url_for("goal.index"))


@goal_bp.route("/goals/<int:goal_id>/delete", methods=["POST"])
@login_required
def delete(goal_id: int):
    user = get_current_user()
    try:
        savings_goal_service.remove(user.user_id, goal_id)
    except ValueError as error:
        flash(str(error), "danger")
        return redirect(url_for("goal.index"))
    flash("Savings goal deleted successfully.", "success")
    return redirect(url_for("goal.index"))
