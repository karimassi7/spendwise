"""Server-rendered web controllers for SpendWise."""

from webapp.controllers.account import account_bp
from webapp.controllers.auth import auth_bp
from webapp.controllers.budget import budget_bp
from webapp.controllers.category import category_bp
from webapp.controllers.dashboard import dashboard_bp
from webapp.controllers.goal import goal_bp
from webapp.controllers.settings import settings_bp
from webapp.controllers.transaction import transaction_bp

__all__ = [
    "account_bp",
    "auth_bp",
    "budget_bp",
    "category_bp",
    "dashboard_bp",
    "goal_bp",
    "settings_bp",
    "transaction_bp",
]
