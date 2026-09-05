"""Authentication helpers for the SpendWise web app.

Uses Werkzeug's password hashing and Flask's signed session cookies.
"""

from functools import wraps

from flask import flash, redirect, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from domain.user_profile import UserProfile
from repositories.profile_repository import ProfileRepository
from service.profile_service import ProfileService

_profile_repository = ProfileRepository()
_profile_service = ProfileService(_profile_repository)


def hash_password(password: str) -> str:
    """Return a securely hashed password."""
    return generate_password_hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Return True when the plaintext password matches the stored hash."""
    if not password_hash:
        return False
    return check_password_hash(password_hash, password)


def register_user(email: str, password: str, name: str,
                  currency: str, monthly_income) -> UserProfile:
    """Create a new user account, raising ValueError on duplicates/bad input."""
    email = email.strip().lower()
    existing = _profile_service.get_by_email(email)
    if existing is not None:
        raise ValueError("An account with this email already exists.")
    if not password or len(password) < 6:
        raise ValueError("Password must be at least 6 characters.")
    return _profile_service.create_profile(
        name=name,
        currency=currency,
        monthly_income=monthly_income,
        email=email,
        password_hash=hash_password(password),
    )


def authenticate_user(email: str, password: str) -> UserProfile | None:
    """Return the profile when credentials are valid, otherwise None."""
    profile = _profile_service.get_by_email(email.strip().lower())
    if profile is None:
        return None
    if not verify_password(password, profile.password_hash):
        return None
    return profile


def get_current_user() -> UserProfile | None:
    """Return the logged-in user from the session, or None."""
    user_id = session.get("user_id")
    if user_id is None:
        return None
    try:
        return _profile_service.get_profile(user_id)
    except ValueError:
        session.clear()
        return None


def login_required(view):
    """Redirect unauthenticated visitors to the sign-in page."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if get_current_user() is None:
            flash("Please sign in to continue.", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped
