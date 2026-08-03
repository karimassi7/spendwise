"""Tests for clean terminal menu rendering."""

from collections.abc import Callable

import pytest

from spendwise.presentation.menu import (
    CLEAR_SCREEN,
    display_account_menu,
    display_budget_menu,
    display_category_menu,
    display_goal_menu,
    display_main_menu,
    display_profile_menu,
    display_transaction_menu,
)


def test_profile_menu_does_not_include_main_menu(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Render only profile options in the profile menu."""
    display_profile_menu()

    output = capsys.readouterr().out
    assert output.startswith(CLEAR_SCREEN)
    assert "PROFILE MENU" in output
    assert "1. Create Profile" in output
    assert "6. Back" in output
    assert "Manage Accounts" not in output
    assert "SPENDWISE APP" not in output


def test_each_menu_clears_the_previous_screen(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Clear the terminal before replacing one menu with another."""
    display_profile_menu()
    display_main_menu()

    output = capsys.readouterr().out
    assert output.count(CLEAR_SCREEN) == 2
    latest_screen = output.split(CLEAR_SCREEN)[-1]
    assert "SPENDWISE APP" in latest_screen
    assert "PROFILE MENU" not in latest_screen


@pytest.mark.parametrize(
    "display_menu",
    (
        display_main_menu,
        display_profile_menu,
        display_account_menu,
        display_category_menu,
        display_transaction_menu,
        display_budget_menu,
        display_goal_menu,
    ),
)
def test_every_menu_starts_with_a_clear_screen(
    display_menu: Callable[[], None], capsys: pytest.CaptureFixture[str]
) -> None:
    """Clear stale terminal content before rendering every menu type."""
    display_menu()

    assert capsys.readouterr().out.startswith(CLEAR_SCREEN)
