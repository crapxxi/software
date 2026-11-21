# Expense Tracker

Small command-line tool to record personal expenses in a local JSON file and print reports.
No network access, no third-party runtime dependencies.

## Setup

Requires Python 3.9+.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
```

## Usage

```bash
python -m expense_tracker add 2026-11-01 food 12.50 "lunch"
python -m expense_tracker list                    # --format text|csv|json
python -m expense_tracker report --format csv     # totals per category
python -m expense_tracker split 3                 # share per person
```

Data is stored in `expenses.json` in the current directory. Override with `--file PATH`
or the `EXPENSES_FILE` environment variable.

Amounts must be positive with at most 2 decimal places. Since v0.2.0 they are stored and
printed in JSON as strings (`"12.50"`) so money stays exact; data files from v0.1.0 still load.
Invalid input prints `error: ...` and exits with code 2.

> Known limitation: CSV exports are not escaped against spreadsheet formulas. Do not open a CSV
> export in a spreadsheet program if descriptions came from an untrusted source.

## Development

```bash
.venv/bin/python -m pytest          # tests (pytest is configured to find the package)
.venv/bin/ruff check .              # lint
.venv/bin/python -m build --wheel   # build
scripts/run_checks.sh               # all of the above + CLI behaviour probes
```

See `AGENTS.md` for rules that apply to AI coding agents and `ACCEPTANCE_CRITERIA.md` for
behaviour that must not change.
