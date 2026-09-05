"""End-to-end web flow tests using the Flask test client.

These tests exercise authentication and per-user data isolation against the
real MySQL database configured through the MYSQL_* environment variables.
Each test cleans up the user it creates.
"""

from decimal import Decimal
import uuid

import pytest

from webapp import services
from webapp.app import create_app


def _unique_email() -> str:
    return f"test-{uuid.uuid4().hex[:10]}@example.com"


def _register(client: object, email: str, password: str = "secret123") -> object:
    return client.post(
        "/register",
        data={
            "name": "Test User",
            "email": email,
            "password": password,
            "currency": "USD",
            "monthly_income": "2000",
        },
        follow_redirects=True,
    )


def _delete_user(email: str) -> None:
    profile = services.profile_service.get_by_email(email)
    if profile is not None:
        services.profile_service.remove_profile(profile.user_id)


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


@pytest.fixture
def user(client):
    """Register a fresh user and delete their records on teardown."""
    email = _unique_email()
    password = "secret123"

    _delete_user(email)
    response = _register(client, email, password)
    assert response.status_code == 200

    yield email, password

    _delete_user(email)


def test_register_redirects_to_dashboard(client, user):
    email, _ = user
    response = client.get("/")
    assert response.status_code == 200
    assert b"Test User" in response.data


def test_bad_credentials_are_rejected(client):
    response = client.post(
        "/login",
        data={"email": "nobody@example.com", "password": "wrong"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Invalid email or password" in response.data


def test_logout_requires_login_for_protected_pages(client, user):
    client.post("/logout")
    response = client.get("/", follow_redirects=True)
    assert response.status_code == 200
    assert b"Sign in" in response.data or b"Login" in response.data


def test_full_financial_workflow(client, user):
    email, password = user
    response = client.get("/")
    assert b"Dashboard" in response.data

    response = client.post(
        "/accounts/create",
        data={"name": "Bank", "balance": "1000", "account_type": "bank"},
        follow_redirects=True,
    )
    assert b"Bank" in response.data

    client.post("/categories/create",
                data={"name": "Salary", "category_type": "income"})
    client.post("/categories/create",
                data={"name": "Food", "category_type": "expense"})

    profile = services.profile_service.get_by_email(email)
    accounts = services.account_service.account_repository.get_all(profile.user_id)
    assert len(accounts) == 1
    account_id = accounts[0].account_id
    categories = services.category_service.category_repository.get_all(
        profile.user_id
    )
    income_category = next(c for c in categories if c.category_type == "income")
    expense_category = next(c for c in categories if c.category_type == "expense")

    response = client.post(
        "/transactions/income",
        data={
            "account_id": account_id,
            "category_id": income_category.category_id,
            "amount": "500",
            "description": "Salary",
            "transaction_date": "2026-09-01",
        },
        follow_redirects=True,
    )
    assert b"Salary" in response.data

    response = client.post(
        "/transactions/expense",
        data={
            "account_id": account_id,
            "category_id": expense_category.category_id,
            "amount": "120",
            "description": "Groceries",
            "transaction_date": "2026-09-01",
        },
        follow_redirects=True,
    )
    assert b"Groceries" in response.data

    response = client.post(
        "/budgets/create",
        data={
            "category_id": expense_category.category_id,
            "limit_amount": "300",
            "from_date": "2026-09-01",
            "to_date": "2026-09-30",
        },
        follow_redirects=True,
    )
    assert b"Food" in response.data

    client.post(
        "/goals/create",
        data={
            "name": "Vacation",
            "target_amount": "2000",
            "saved_amount": "0",
            "deadline": "2026-12-31",
        },
    )
    goals = services.savings_goal_service.savings_goal_repository.get_by_name(
        "Vacation", profile.user_id
    )
    goal = goals[0] if isinstance(goals, list) else goals
    response = client.post(
        f"/goals/{goal.goal_id}/contribute",
        data={"amount": "500"},
        follow_redirects=True,
    )
    assert b"Contribution added" in response.data

    transaction_total = services.transaction_service.transaction_repository.get_all(
        profile.user_id
    )
    assert len(transaction_total) == 2


def test_users_do_not_see_each_others_data(client, user):
    email, password = user

    other_email = _unique_email()
    client.post("/logout")
    _register(client, other_email)
    other = services.profile_service.get_by_email(other_email)
    try:
        services.account_service.create_account(
            profile_id=other.user_id,
            name="Private Account",
            balance=Decimal("1000"),
            account_type="bank",
        )

        client.post("/logout")
        client.post("/login", data={"email": email, "password": password},
                    follow_redirects=True)

        response = client.get("/accounts")
        assert b"Private Account" not in response.data
    finally:
        _delete_user(other_email)


def test_delete_account_cleans_up_data(client, user):
    email, _ = user
    client.post(
        "/accounts/create",
        data={"name": "Temp", "balance": "50", "account_type": "cash"},
        follow_redirects=True,
    )

    profile = services.profile_service.get_by_email(email)
    response = client.post("/settings/delete", follow_redirects=True)
    assert response.status_code == 200
    assert services.profile_service.get_by_email(email) is None

    remaining = services.account_service.account_repository.get_all(profile.user_id)
    assert remaining == []