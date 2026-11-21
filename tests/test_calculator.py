from expense_tracker.calculator import total, total_by_category, split_evenly
from expense_tracker.models import Expense


def sample():
    return [
        Expense("2026-11-01", "food", 12.5, "lunch"),
        Expense("2026-11-02", "transport", 3.0, "bus"),
        Expense("2026-11-03", "food", 7.5, "coffee"),
    ]


def test_total():
    assert total(sample()) == 23.0


def test_total_by_category():
    assert total_by_category(sample()) == {"food": 20.0, "transport": 3.0}


def test_split_evenly():
    assert split_evenly(30, 3) == 10.0
