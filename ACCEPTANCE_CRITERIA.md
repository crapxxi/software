# Acceptance criteria

These must remain true after every change. Each one is checked by an automated test in `tests/test_cli.py`
(AC5 by the commands themselves).

| ID  | Criterion | Verified by |
|-----|-----------|-------------|
| AC1 | `add DATE CATEGORY AMOUNT [DESCRIPTION]` stores the expense in the `--file` JSON file and prints `Added: DATE CATEGORY AMOUNT` (amount with 2 decimals); `list` then shows it. | `test_ac1_add_persists_and_list_shows_expense` |
| AC2 | `report` (text) prints one line per category with its total and a final `TOTAL` line equal to the sum of all expenses, 2 decimals. | `test_ac2_report_totals_per_category_and_overall` |
| AC3 | `list` and `report` support `--format text|csv|json`; CSV output starts with a header row; JSON output is valid JSON. | `test_ac3_list_and_report_support_text_csv_json` |
| AC4 | `split N` prints `Each person pays: X` where X is total / N rounded to 2 decimals. | `test_ac4_split_prints_rounded_share` |
| AC5 | `python -m pytest`, `ruff check .` and `python -m build --wheel` all succeed on a clean checkout. | `scripts/run_checks.sh` |
