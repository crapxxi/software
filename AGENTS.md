# AGENTS.md — instructions for AI coding agents

## Purpose
Expense Tracker is a small, offline Python CLI that records personal expenses in a local JSON
file and prints listings, per-category reports and even splits. It is a teaching project:
correctness of money arithmetic and clear, reviewable diffs matter more than features.

## Architecture
```
expense_tracker/
  __main__.py    entry point for `python -m expense_tracker`
  cli.py         argparse parser + one cmd_* function per subcommand (I/O only)
  models.py      Expense dataclass, (de)serialisation
  calculator.py  pure business logic: totals, per-category totals, split
  formatters.py  output formats (Strategy): text / csv / json, registry FORMATTERS
  storage.py     load/save the JSON data file
tests/           pytest; test_cli.py = acceptance criteria, test_calculator.py = unit tests
scripts/run_checks.sh  full verification (tests, lint, build, CLI probes)
```
Dependency direction: `cli -> calculator, formatters, storage -> models`. Business logic must not print or
read files; `cli.py` must not contain calculations.

## Setup
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
```

## Safe commands (may be run without asking)
- `.venv/bin/python -m pytest` and `.venv/bin/python -m pytest -k <name>`
- `.venv/bin/ruff check .` (no `--fix` unless the human asked for it)
- `.venv/bin/python -m build --wheel --outdir /tmp/et-dist .`
- `scripts/run_checks.sh`
- `python -m expense_tracker --file <path inside a temp dir> ...`
- Read-only git: `git status`, `git diff`, `git log`, `git show`

## Coding conventions
- Python 3.9+, standard library only at runtime. Follow the existing style (PEP 8, ruff defaults).
- Keep functions small; put new logic in `calculator.py`/`models.py`, not in `cli.py`.
- User-facing errors go to stderr with a non-zero exit code, never a raw traceback.
- One logical change per commit; commit message explains *why*.

## Test expectations
- Every behaviour change or bug fix comes with a test that fails before and passes after.
- `python -m pytest` and `ruff check .` must pass before you report a task as done.
- All criteria in `ACCEPTANCE_CRITERIA.md` must keep passing; never edit or delete an
  acceptance test to make it pass — stop and ask instead.
- Report the exact commands you ran and their real output. Never claim a check passed if you
  did not run it.

## Forbidden actions
- Do **not** read, create or commit secrets, tokens, `.env` files or real personal/financial data.
  Use synthetic data in temp directories only; never touch a real `expenses.json`.
- Do **not** deploy, publish packages (`twine upload`, `pip publish`) or push to any remote.
- Do **not** run destructive commands: `rm -rf` outside temp dirs, `git reset --hard`,
  `git push --force`, `git clean -fdx`, history rewrites, deleting branches or tags.
- Do **not** add, remove or upgrade dependencies (requirements files, `pyproject.toml`) without
  explicit human approval; if you think one is needed, explain why and stop.
- Do **not** disable tests, lint rules or checks to make them pass.
- Do **not** access the network except `pip install -r requirements-dev.txt` during setup and
  `python -m build` (its isolated build env downloads setuptools from PyPI).

## Review gates
1. Agent works on a separate branch or worktree, never directly on `main`.
2. Agent hands over: change summary, `git diff`, test/lint/build output, list of risks or
   anything not verified.
3. A human reviews the diff and re-runs `scripts/run_checks.sh` before merging.
4. Changes to `storage.py` (data format) or money arithmetic need an explicit human sign-off.
