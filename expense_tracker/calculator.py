from collections import defaultdict


def total(expenses):
    result = 0.0
    for e in expenses:
        result += e.amount
    return result


def total_by_category(expenses):
    result = defaultdict(float)
    for e in expenses:
        result[e.category] += e.amount
    return dict(result)


def split_evenly(amount, people):
    return round(amount / people, 2)
