from dataclasses import dataclass, asdict


@dataclass
class Expense:
    date: str
    category: str
    amount: float
    description: str = ""

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data):
        return Expense(
            date=data["date"],
            category=data["category"],
            amount=float(data["amount"]),
            description=data.get("description", ""),
        )
