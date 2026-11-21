from dataclasses import dataclass
from decimal import Decimal

CENT = Decimal("0.01")


def to_money(value):
    """Convert user input or stored JSON (str, int or legacy float) to an exact Decimal in cents."""
    return Decimal(str(value)).quantize(CENT)


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
    def from_dict(data):
        return Expense(
            date=data["date"],
            category=data["category"],
            amount=to_money(data["amount"]),
            description=data.get("description", ""),
        )
