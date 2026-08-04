from decimal import Decimal

import pytest

from domain.user_profile import UserProfile


def test_name_cannot_be_a_number() -> None:
    with pytest.raises(ValueError, match="Name cannot be a number"):
        UserProfile("123", "USD", 1, Decimal("100"))


@pytest.mark.parametrize("monthly_income", [Decimal("0"), Decimal("-1")])
def test_monthly_income_must_be_greater_than_zero(
    monthly_income: Decimal,
) -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        UserProfile("Alice", "USD", 1, monthly_income)
