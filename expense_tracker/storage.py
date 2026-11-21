import json
import os

from .models import Expense

DEFAULT_FILE = os.environ.get("EXPENSES_FILE", "expenses.json")


def load_expenses(path=DEFAULT_FILE):
    if not os.path.exists(path):
        return []
    try:
        with open(path) as f:
            data = json.load(f)
        return [Expense.from_dict(item) for item in data]
    except (ValueError, KeyError, TypeError, ArithmeticError) as e:
        raise ValueError(f"cannot read data file {path}: {e}") from None


def save_expenses(expenses, path=DEFAULT_FILE):
    with open(path, "w") as f:
        json.dump([e.to_dict() for e in expenses], f, indent=2)
