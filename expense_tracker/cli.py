import argparse
import csv
import io
import json
import sys

from .calculator import total, total_by_category, split_evenly
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
    if args.format == "text":
        for e in expenses:
            print(f"{e.date}  {e.category:<12} {e.amount:>10.2f}  {e.description}")
    elif args.format == "csv":
        writer = csv.writer(sys.stdout)
        writer.writerow(["date", "category", "amount", "description"])
        for e in expenses:
            writer.writerow([e.date, e.category, e.amount, e.description])
    elif args.format == "json":
        print(json.dumps([e.to_dict() for e in expenses], indent=2))
    else:
        print("Unknown format")


def cmd_report(args):
    expenses = load_expenses(args.file)
    by_cat = total_by_category(expenses)
    if args.format == "text":
        for cat, amount in by_cat.items():
            print(f"{cat:<12} {amount:>10.2f}")
        print(f"{'TOTAL':<12} {total(expenses):>10.2f}")
    elif args.format == "csv":
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["category", "amount"])
        for cat, amount in by_cat.items():
            writer.writerow([cat, amount])
        writer.writerow(["TOTAL", total(expenses)])
        print(buf.getvalue(), end="")
    elif args.format == "json":
        print(json.dumps({"by_category": by_cat, "total": total(expenses)}, indent=2))
    else:
        print("Unknown format")


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
    p_list.add_argument("--format", default="text")
    p_list.set_defaults(func=cmd_list)

    p_report = sub.add_parser("report")
    p_report.add_argument("--format", default="text")
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
