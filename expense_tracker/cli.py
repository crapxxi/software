import argparse

from .calculator import total, total_by_category, split_evenly
from .formatters import FORMATTERS
from .models import Expense
from .storage import load_expenses, save_expenses, DEFAULT_FILE


def cmd_add(args):
    expenses = load_expenses(args.file)
    expense = Expense(args.date, args.category, float(args.amount), args.description)
    expenses.append(expense)
    save_expenses(expenses, args.file)
    print(f"Added: {expense.date} {expense.category} {expense.amount:.2f}")


def cmd_list(args):
    expenses = load_expenses(args.file)
    print(FORMATTERS[args.format].expenses(expenses), end="")


def cmd_report(args):
    expenses = load_expenses(args.file)
    print(FORMATTERS[args.format].report(total_by_category(expenses), total(expenses)), end="")


def cmd_split(args):
    expenses = load_expenses(args.file)
    share = split_evenly(total(expenses), args.people)
    print(f"Each person pays: {share:.2f}")


def build_parser():
    parser = argparse.ArgumentParser(prog="expense-tracker")
    parser.add_argument("--file", default=DEFAULT_FILE)
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add")
    p_add.add_argument("date")
    p_add.add_argument("category")
    p_add.add_argument("amount")
    p_add.add_argument("description", nargs="?", default="")
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list")
    p_list.add_argument("--format", default="text", choices=FORMATTERS)
    p_list.set_defaults(func=cmd_list)

    p_report = sub.add_parser("report")
    p_report.add_argument("--format", default="text", choices=FORMATTERS)
    p_report.set_defaults(func=cmd_report)

    p_split = sub.add_parser("split")
    p_split.add_argument("people", type=int)
    p_split.set_defaults(func=cmd_split)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
