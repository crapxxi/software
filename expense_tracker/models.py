from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation

CENT = Decimal("0.01")


def to_money(value):
    """Convert user input or stored JSON (str, int or legacy float) to an exact Decimal in cents."""
    try:
        amount = Decimal(str(value).strip())
    except InvalidOperation:
        raise ValueError(f"amount must be a number, got {value!r}") from None
    if not amount.is_finite() or amount <= 0:
        raise ValueError(f"amount must be a positive number, got {value!r}")
    if amount != amount.quantize(CENT):
        raise ValueError(f"amount must have at most 2 decimal places, got {value!r}")
    return amount.quantize(CENT)


def validate_date(value):
    try:
        date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError(f"date must be in YYYY-MM-DD format, got {value!r}") from None
    return value


def validate_category(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("category must not be empty")
    return value.strip()


@dataclass
class Expense:
    date: str
    category: str
    amount: Decimal
    description: str = ""

    def to_dict(self):
        # Amount is stored as a string ("12.50") so it round-trips without binary rounding.
        return {
            "date": self.date,
            "category": self.category,
            "amount": str(self.amount),
            "description": self.description,
        }

    @staticmethod
    def create(date, category, amount, description=""):
        """Build an Expense from untrusted input, raising ValueError with a readable message."""
        return Expense(validate_date(date), validate_category(category), to_money(amount), description)

    @staticmethod
    def from_dict(data):
        # Records already on disk are not re-validated: files written by v0.1.0 may contain
        # negative or 3-decimal amounts, and refusing to open them would lock users out.
        return Expense(
            date=data["date"],
            category=data["category"],
            amount=Decimal(str(data["amount"])).quantize(CENT),
            description=data.get("description", ""),
        )
