from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP

from .models import CENT


def total(expenses):
    return sum((e.amount for e in expenses), Decimal("0.00"))


def total_by_category(expenses):
    result = defaultdict(lambda: Decimal("0.00"))
    for e in expenses:
        result[e.category] += e.amount
    return dict(result)


def split_evenly(amount, people):
    return (Decimal(amount) / people).quantize(CENT, rounding=ROUND_HALF_UP)
