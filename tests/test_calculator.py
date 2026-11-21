import json
from decimal import Decimal

from expense_tracker.calculator import total, total_by_category, split_evenly
from expense_tracker.models import Expense, to_money
from expense_tracker.storage import load_expenses, save_expenses


def sample():
    return [
        Expense("2026-11-01", "food", to_money("12.5"), "lunch"),
        Expense("2026-11-02", "transport", to_money("3"), "bus"),
        Expense("2026-11-03", "food", to_money("7.5"), "coffee"),
    ]


def test_total():
    assert total(sample()) == Decimal("23.00")


def test_total_by_category():
    assert total_by_category(sample()) == {"food": Decimal("20.00"), "transport": Decimal("3.00")}


def test_split_evenly():
    assert split_evenly(Decimal("30"), 3) == Decimal("10.00")


def test_total_is_exact_for_cents():
    # R1: with float, 0.10 + 0.20 == 0.30000000000000004
    items = [Expense("2026-11-01", "food", to_money("0.10")), Expense("2026-11-01", "food", to_money("0.20"))]
    assert total(items) == Decimal("0.30")
    assert total([Expense("2026-11-01", "x", to_money("0.10"))] * 10) == Decimal("1.00")


def test_split_rounds_half_up():
    assert split_evenly(Decimal("0.05"), 2) == Decimal("0.03")


def test_storage_round_trip_keeps_exact_amounts(tmp_path):
    path = tmp_path / "e.json"
    save_expenses([Expense("2026-11-01", "food", to_money("0.10"))], str(path))
    assert json.loads(path.read_text())[0]["amount"] == "0.10"
    assert load_expenses(str(path))[0].amount == Decimal("0.10")


def test_legacy_float_data_file_still_loads(tmp_path):
    path = tmp_path / "e.json"
    path.write_text('[{"date": "2026-11-01", "category": "food", "amount": 12.5, "description": ""}]')
    assert load_expenses(str(path))[0].amount == Decimal("12.50")
