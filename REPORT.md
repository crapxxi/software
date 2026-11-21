# Software Engineering — Assignment #05

**AI-assisted repository customization, agent readiness and software risk governance**

| | |
|---|---|
| Student | _Surname Name_ |
| Repository | `se-assignment-05-expense-tracker` (local git repository, exported as archive) |
| Baseline version | tag `baseline` = commit `1b851b6` |
| Final version | tag `final` (see `git log`) |
| AI assistant | Claude Code (CLI), model Claude Opus 5.5 (`claude-opus-5-5`), Anthropic |
| Date | 2026-11-21 |

All command output quoted in this report is copied from files in `docs/evidence/`, which were produced
by running the commands, not written by hand. Nothing in this report claims a check that was not run;
section 7.4 lists what was **not** executed.

---

## 0. Scenario and starting point

**Project.** *Expense Tracker*: a small offline Python CLI that stores expenses in a local JSON
file and prints listings, per-category reports and even splits. It has no third-party runtime
dependencies and uses only synthetic data. **Disclosure:** the AI assistant wrote the project
for this assignment (commit `1b851b6`), and it was frozen as the baseline before any audit work
started. Everything after that commit follows the assignment workflow.

**Baseline preserved:** `git tag baseline` → `1b851b6`. Every later change is a separate commit:

| Commit | Purpose | Task |
|---|---|---|
| `1b851b6` (tag `baseline`) | Original project v0.1.0 | — |
| `152de21` | AGENTS.md, acceptance criteria + tests, reproducible test setup, pinned dev deps | 1, 2 |
| `392a387` | Strategy refactor of output formats | 3 |
| `884afc2` | Mitigation R1: Decimal money | 7 |
| `ff30976` | Mitigation R4: input validation, readable errors | 7 |
| `6603541` | Version 0.2.0, README: money format and CSV limitation | 9 |
| tag `final` | Report and evidence files | 5, 6, 8, 9, 10 |

(`git log --oneline baseline..final` lists them all.)

**Acceptance criteria.** Defined in `ACCEPTANCE_CRITERIA.md` and checked automatically by `tests/test_cli.py`:

| ID | Criterion |
|---|---|
| AC1 | `add DATE CATEGORY AMOUNT [DESC]` stores the expense in the `--file` JSON and prints `Added: …`; `list` then shows it. |
| AC2 | `report` prints one line per category plus a `TOTAL` line equal to the sum of all expenses (2 decimals). |
| AC3 | `list`/`report` support `--format text\|csv\|json`; the CSV output has a header row and the JSON output is valid. |
| AC4 | `split N` prints `Each person pays: X`, where X = total / N rounded to 2 decimals. |
| AC5 | `python -m pytest`, `ruff check .` and `python -m build --wheel` succeed on a clean checkout. |

---

## 1. Task #01 — Baseline and context

### 1.1 Repository map (baseline)

| Kind | Item |
|---|---|
| Entry points | `python -m expense_tracker` (`expense_tracker/__main__.py`); console script `expense-tracker` → `expense_tracker.cli:main` (`pyproject.toml`) |
| Modules | `cli.py`: argparse with 4 sub-commands (add, list, report, split) and output formatting · `models.py`: `Expense` dataclass · `calculator.py`: total, total by category, split · `storage.py`: JSON load/save, path from `EXPENSES_FILE` env var |
| Dependencies | Runtime: Python standard library only. Dev: `requirements.txt` containing unpinned `pytest` |
| Tests | `tests/test_calculator.py`: 3 unit tests. No CLI tests. |
| Build | `pyproject.toml` (setuptools); no lint config, no CI, no AGENTS.md |

### 1.2 Commands and actual results (baseline `1b851b6`)

Full log: `docs/evidence/01-baseline-checks.txt` (produced by `scripts/run_checks.sh` in a worktree of `baseline`).
Environment: macOS 15.2, Python 3.10.10, pytest 8.3.3, ruff 0.7.4, build 1.2.2.

| Command | Result |
|---|---|
| `pytest -q` (the command given in the README) | **FAIL**, exit 2: `ModuleNotFoundError: No module named 'expense_tracker'` while collecting the tests |
| `python -m pytest -q` | 3 passed, exit 0 |
| `ruff check .` | All checks passed, exit 0 |
| `python -m build --wheel` | Successfully built `expense_tracker-0.1.0-py3-none-any.whl`, exit 0 |
| Smoke test (add ×2, report, split 2) | Correct output (`TOTAL 15.50`, `Each person pays: 7.75`) |

### 1.3 Concrete weaknesses (with evidence)

| # | Weakness | Evidence |
|---|---|---|
| W1 | The documented test command fails | README.md:15 says "Run tests with `pytest`", but `pytest -q` exits 2 with ModuleNotFoundError (probe 1) |
| W2 | Money is stored and summed as `float` | `models.py:8`, `calculator.py:12`. Probe 6: `0.10 + 0.20` gives `"total": 0.30000000000000004` |
| W3 | No input validation | Probe 7: `add … -50` is accepted (exit 0). `add … abc` and `split 0` crash with a raw traceback (`ValueError`, `ZeroDivisionError`) |
| W4 | Duplicated format dispatch; an unknown format is not an error | `cli.py:22-33` and `cli.py:39-54` contain two copies of the same `if/elif` chain. Probe 10: `--format xml` prints "Unknown format" and exits **0** |
| W5 | Unpinned dependency, no agent instructions, no CI | `requirements.txt:1` is `pytest` with no version; there is no `AGENTS.md` and no `.github/` |

### 1.4 Facts vs assumptions vs unverified AI suggestions

- **Observed facts** (reproduced by a command, output in the evidence files): W1–W5, the CSV probe
  (8) and the corrupt-file traceback (9).
- **Assumptions:** the tool is used by one person on their own machine; CSV exports may be
  opened in a spreadsheet program; the data file is small.
- **Unverified AI suggestions** (not reproduced, see the risk register): data loss on an
  interrupted write (R7), lost updates on concurrent writes (R12), "path traversal" (R9) and
  "unsafe JSON deserialisation" (R10). The last two turned out to be unsupported.

---

## 2. Task #02 — Agent instructions

`AGENTS.md` was created in the repository root. It contains:

- **Purpose** and **architecture**: a module map plus the dependency rule
  `cli → calculator, storage → models`; business logic must not do I/O.
- **Setup**: a venv plus the pinned `requirements-dev.txt`.
- **Safe commands** the agent may run without asking: pytest, ruff (without `--fix`), build into
  /tmp, `scripts/run_checks.sh`, the CLI on temp files, read-only git.
- **Coding conventions** and **test expectations**: a test that fails before and passes after
  each fix; acceptance tests must never be edited to make them pass; only real command output
  may be reported.
- **Forbidden actions**: secrets/`.env`/real personal data, deploy/publish/push, destructive
  commands (`rm -rf` outside temp, `git reset --hard`, force push, history rewrites), adding or
  upgrading dependencies without approval, disabling tests or lint, network access beyond setup.
- **Review gates**: work on a branch or worktree; hand-over package; a human re-runs the checks
  before merge; changes to the data format and to money arithmetic need explicit sign-off.

**Loading disclosure:** Claude Code loads `CLAUDE.md` automatically. `CLAUDE.md` contains
only `@AGENTS.md`, which imports the file, so the agent sees the same rules without a second
copy. No manual pasting was needed. With a tool that does not read either file, the AGENTS.md
text would have to be pasted into the prompt, and that would be disclosed here.

The same commit also made the setup reproducible. `pyproject.toml` got
`[tool.pytest.ini_options] pythonpath = ["."]` (this fixes W1), the unpinned `requirements.txt`
was replaced by a pinned `requirements-dev.txt` (W5), the README was corrected, and
`scripts/run_checks.sh` was added.

---

## 3. Task #03 — Focused pattern decision

**Problem (W4 / R5).** `cmd_list` and `cmd_report` each had their own `if/elif` chain over the
same three format names (baseline `cli.py:22-33`, `39-54`). Adding a format (for example
Markdown) meant editing both chains and keeping them consistent. Presentation code was mixed
into the command handlers. The `else` branch also turned an invalid format into a successful
exit.

**Options considered.**

| Option | Verdict |
|---|---|
| Leave as is | Rejected: the duplication is real (2 chains × 3 branches) and has already caused a bug (exit 0 on an unknown format). |
| Dict of plain functions | Workable, but every format needs 2 related functions (`expenses`, `report`) that belong together. |
| **Strategy**: one formatter class per format, chosen by name | **Chosen.** Each class keeps both outputs for its format together. A new format means one new class plus one registry entry. The registry also feeds argparse `choices`. |
| Adapter | Not applicable: there is no foreign interface to adapt. |

**Implementation (one refactoring, commit `392a387`).** New file `expense_tracker/formatters.py`
with `TextFormatter`, `CsvFormatter`, `JsonFormatter` and the `FORMATTERS` registry. `cli.py`
shrank by 26 lines, and both handlers became single lines: `FORMATTERS[args.format].expenses(...)`.

| | Before | After |
|---|---|---|
| Format dispatch sites | 2 (`cmd_list`, `cmd_report`) | 1 (registry lookup) |
| Places to edit when adding a format | 2 if/elif chains + help text | 1 class + 1 dict entry |
| `cli.py` imports | argparse, csv, io, json, sys | argparse (+ formatters) |
| Unknown format | prints "Unknown format", exit 0 | argparse error, exit 2 |

**Proof that the acceptance criteria still hold** (`docs/evidence/03-pattern-refactor-equivalence.txt`):

- Byte-for-byte comparison of all 6 combinations (list/report × text/csv/json) on the same
  synthetic data, baseline vs refactor: `diff` reports no differences. Both outputs are
  47 lines with identical SHA-256 (`3ec810f6…`).
- `python -m pytest -q`: 8 passed (AC1–AC4 plus a new test for unknown-format rejection).
  `ruff check .`: passed.

---

## 4. Task #04 — Read-only risk review

**Method.** The AI assistant was asked to list candidate risks for baseline `1b851b6` **without
modifying files**: it could only read sources and run the CLI against temp files. Each candidate
was then checked against the code and a reproducible command (probes 1–10 in
`docs/evidence/01-baseline-checks.txt`).

| ID | Candidate finding (AI-proposed) | Category | Classification | Evidence / reasoning |
|---|---|---|---|---|
| R1 | Money kept in binary `float` gives inexact totals | Correctness | **Confirmed** | `models.py:8`, `calculator.py:12`. Probe 6 output: `0.30000000000000004` |
| R2 | The documented test command does not work, so agents/CI cannot verify changes | Agent operations | **Confirmed** | README.md:15. Probe 1: `pytest` exits 2 with `ModuleNotFoundError` |
| R3 | CSV formula injection: descriptions starting with `=`,`+`,`-`,`@` are exported unescaped | Security | **Confirmed** (output); spreadsheet execution not tested | `cli.py:29`. Probe 8 output: `"=HYPERLINK(""http://evil.example"",""x"")"` |
| R4 | No validation of amount, date, category or people count | Correctness | **Confirmed** | `cli.py:14`, `calculator.py:19`. Probe 7: `-50` accepted; `abc` → ValueError traceback; `split 0` → ZeroDivisionError |
| R5 | Duplicated format conditionals; unknown format exits 0 | Maintainability | **Confirmed** | `cli.py:22-54`. Probe 10: "Unknown format", exit 0 |
| R6 | Unpinned dependency, so builds are not reproducible | Dependency | **Confirmed** | `requirements.txt:1` = `pytest` (no version) |
| R7 | `save_expenses` writes in place (`open(path, "w")`); an interruption mid-write truncates the data file | Correctness | **Plausible / unverified** | `storage.py:18` matches the pattern, but no crash during a write was reproduced |
| R8 | A corrupt data file crashes the CLI with a traceback | Correctness | **Confirmed** | Probe 9: `JSONDecodeError` traceback, exit 1 |
| R9 | "`--file` / `EXPENSES_FILE` allow path traversal and arbitrary file overwrite" | Security | **Unsupported** | Local single-user CLI: the path comes from the same user who runs the program, with that user's permissions. There is no privilege boundary to cross. |
| R10 | "`json.load` on the data file allows unsafe deserialisation / code execution" | Security | **Unsupported** | `json` only builds dict/list/str/number/bool/None; unlike `pickle`/`yaml.load`, it never executes code. |
| R11 | No CI, so checks run only when someone remembers | Agent operations | **Confirmed** | There is no `.github/` or other CI config in the repository |
| R12 | Two concurrent `add` calls can lose one update (read-modify-write without a lock) | Correctness | **Plausible / unverified** | Follows from `cli.py:12-15` + `storage.py`; not reproduced |

12 candidates in 5 categories: 8 confirmed, 2 plausible/unverified, 2 unsupported.

---

## 5. Task #05 — Risk register

Scale: likelihood (L) 1 = rare, 2 = possible, 3 = likely in normal use; impact (I) 1 = cosmetic,
2 = wrong or blocked result for the user, 3 = wrong money figures or data loss. Score = L × I.
Owner = the student (single-person project).

| ID | Category | Cause → event → consequence | Component | Evidence | L | I | **Score** | Mitigation | Verification plan | Residual risk |
|---|---|---|---|---|---|---|---|---|---|---|
| R1 | Correctness | float arithmetic → totals such as 0.30000000000000004 → wrong amounts in JSON/CSV reports, errors accumulate | models, calculator | Probe 6 | 3 | 3 | **9** | M1: Decimal in cents, stored as strings | Unit + CLI tests on exact sums; probe 6 rerun | `split` rounds each share, so 10.00 / 3 → 3.33 × 3 = 9.99 (1 cent not allocated) |
| R4 | Correctness | no validation → negative/NaN/invalid amounts stored or crash → corrupt totals, tracebacks | cli, models, calculator | Probe 7 | 3 | 2 | **6** | M2: validate new input, readable errors, exit 2 | Parametrised tests; probe 7 rerun | Records written by v0.1.0 are not re-validated on load (deliberate; see 7.2) |
| R2 | Agent ops | README test command fails → agent/CI reports "tests broken" or skips them → unverified changes | README, pyproject | Probe 1 | 3 | 2 | **6** | `pythonpath` in pyproject; README fixed (Task 2) | `pytest -q` from the repo root | None known |
| R5 | Maintainability | duplicated if/elif → formats drift; invalid format exits 0 → scripts miss errors | cli | cli.py:22-54, probe 10 | 2 | 2 | **4** | Strategy refactor (Task 3) | Byte-identical outputs; exit-code test | None known |
| R3 | Security | user text exported to CSV unescaped → opened in a spreadsheet, a formula/link is evaluated → phishing link or data exfiltration via HYPERLINK | formatters (CSV) | Probe 8 | 2 | 2 | **4** | *Planned:* prefix cells starting with `= + - @ \t \r` with `'` (OWASP) | Test with formula-like descriptions | Open: accepted with control (see section 9) |
| R6 | Dependency | unpinned `pytest` → different versions on other machines → non-reproducible results | requirements | requirements.txt:1 | 2 | 2 | **4** | Pinned `requirements-dev.txt` (Task 2) | `pip install -r` + version check Transitive deps (pluggy, packaging…) not locked; `[build-system] requires = ["setuptools"]` is unpinned, so every isolated build downloads it from PyPI (the final build run stalled for minutes on a slow network) |
| R11 | Agent ops | no CI → checks depend on memory → regressions merged | repository | no CI config | 2 | 2 | **4** | *Planned:* CI workflow running `scripts/run_checks.sh` | CI green on a branch | Open |
| R7 | Correctness | in-place write → interruption truncates file → loss of all data | storage | storage.py:18 (code only) | 1 | 3 | **3** | *Planned:* write to a temp file + `os.replace` | Kill a process mid-write | Open, unverified |
| R8 | Correctness | corrupt JSON → raw traceback → user cannot tell what is wrong | storage | Probe 9 | 1 | 2 | **2** | Covered by M2 (readable error) | Test with `{broken` file | File still has to be repaired by hand |
| R12 | Correctness | concurrent writes → lost update | storage, cli | code only | 1 | 2 | **2** | Not planned (single-user tool) | — | Accepted |
| R9 | Security | — | — | Unsupported | — | — | — | None needed | — | — |
| R10 | Security | — | — | Unsupported | — | — | — | None needed | — | — |

**Top two confirmed risks for corrective action:**
1. **R1 (score 9).** The highest score, and it breaks the product's core job: exact money figures.
2. **R4 (score 6).** Tied with R2 on score. R4 was ranked higher because it damages user data,
   while R2 affects only the developer workflow. R2 was already resolved as part of the Task 2
   setup and is not counted as one of the two mitigations.

---

## 6. Task #06 — Agent-readiness audit

| Area | Baseline `1b851b6` | Final | Evidence |
|---|---|---|---|
| Readable structure | ✅ small modules, clear names | ✅ + formatters separated, dependency rule documented | `AGENTS.md` architecture section |
| README accuracy | ❌ test command wrong | ✅ setup, usage, dev commands verified | Probe 1 before/after |
| Reproducible setup | ⚠️ no Python version, unpinned deps | ✅ venv + pinned dev deps; ⚠️ transitive deps unlocked | `requirements-dev.txt` |
| Tests | ⚠️ 3 unit tests, no CLI coverage, broken entry command | ✅ 28 tests: acceptance AC1–AC4, R1/R4 regressions | `05-final-checks.txt` |
| Lint / type checks | ⚠️ ruff passes but is not configured or documented; no type checker | ✅ ruff configured + documented; ❌ no type checker | |
| Build | ✅ wheel builds | ✅ wheel builds | Probe 4 |
| Logging / error reporting | ❌ raw tracebacks | ✅ `error:` on stderr + exit 2; ❌ no logging (acceptable for a CLI) | Probes 7, 9, 10 |
| Security safeguards | ❌ none | ⚠️ input validation; R3 open | Risk register |
| Agent instructions | ❌ none | ✅ AGENTS.md: permissions/safe commands, forbidden actions, review gates; loaded via CLAUDE.md | `AGENTS.md` |
| CI / enforced gates | ❌ none | ❌ none (rules are written, not enforced) | |

**Readiness level: baseline = 1 (Baseline), final = 2 (Documented).**
Justification: the project now has accurate, tested documentation and explicit agent rules.
An agent can set it up, run every check with one command and knows what it must not do.
Level 3 (Agent-ready) is **not** justified because the following evidence is missing:

- CI that runs `scripts/run_checks.sh` on every branch or PR (R11), so the review gates are not enforced;
- a lock file with hashes for transitive dependencies (R6 residual);
- technical enforcement of the forbidden actions, e.g. a permissions deny-list in the agent's
  settings (`.claude/settings.json`) instead of prose alone;
- an open security finding (R3) and an unverified data-loss risk (R7);
- tests on the declared minimum Python (3.9) and on other operating systems.

---

## 7. Task #07 — Mitigation and verification

### 7.1 Mitigation record M1: R1, float money

| Field | Value |
|---|---|
| Change | `models.to_money()` converts to `Decimal` quantised to 0.01. Amounts are stored as strings (`"12.50"`); `total`/`total_by_category` sum Decimals; `split_evenly` rounds ROUND_HALF_UP; JSON reports print amounts as strings. Old data files with float numbers still load. |
| Diff review | Reviewed before commit. Checked: `format(Decimal, ".2f")` keeps the text output identical (AC2 test unchanged); the CSV `list` now prints `12.50` instead of `12.5` (allowed by AC3); report JSON values changed from numbers to strings, a **contract change** recorded as a trade-off. |
| Tests added | `test_total_is_exact_for_cents`, `test_split_rounds_half_up`, `test_storage_round_trip_keeps_exact_amounts`, `test_legacy_float_data_file_still_loads`, `test_report_json_total_is_exact` |
| Result | Probe 6 now prints `"total": "0.30"` (`05-final-checks.txt`) |
| Updated score | L1 × I1 = **1** (was 9) |
| Residual | Remainder cents in `split` are not allocated (10.00 / 3 → 3.33 each). JSON consumers that expected numbers must parse strings. |

### 7.2 Mitigation record M2: R4, input validation

| Field | Value |
|---|---|
| Change | `Expense.create()` validates new input: positive finite amount with ≤ 2 decimals, ISO date, non-empty category. `split_evenly` requires people ≥ 1. `main()` turns `ValueError` into `error: …` on stderr with exit 2. `load_expenses` reports a corrupt file as a readable error and never overwrites it. |
| Diff review | **The first AI-proposed version was rejected in review.** It also validated records when *loading* the file, so a data file written by v0.1.0 that contained a negative amount (which the baseline allowed) would no longer open at all, locking the user out of all their data. Fixed: only new input is validated and stored records load leniently. A regression test was added. The review also found that `decimal.InvalidOperation` is *not* a `ValueError` subclass, so `storage.py` catches `ArithmeticError` as well. |
| Tests added | `tests/test_validation.py`: 16 cases (6 bad amounts, 3 bad dates, empty category, split 0, corrupt file not overwritten, valid input still accepted, legacy negative amount still loads, non-numeric stored amount) |
| Result | Probe 7: `error: amount must be a positive number, got '-50'`, exit 2; `split 0` → `error: number of people must be at least 1`, exit 2 |
| Updated score | L1 × I2 = **2** (was 6) |
| Residual | Invalid records already on disk are not detected; there is no maximum amount check. |

### 7.3 Baseline vs final checks

| Check | Baseline `1b851b6` | Final |
|---|---|---|
| `pytest -q` (README command) | **ERROR**, exit 2 (collection error) | **28 passed**, 0 failed, exit 0 |
| `python -m pytest -q` | 3 passed, exit 0 | 28 passed, exit 0 |
| `ruff check .` | passed | passed |
| `python -m build --wheel` | success | success |
| Probe 6 (0.10 + 0.20) | `0.30000000000000004` | `"0.30"` |
| Probe 7 (`-50` / `abc` / `split 0`) | accepted / traceback / traceback | exit 2 with message ×3 |
| Probe 8 (CSV formula) | exported unescaped | exported unescaped (**R3 open**) |
| Probe 9 (corrupt file) | traceback, exit 1 | `error: cannot read data file …`, exit 2 |
| Probe 10 (`--format xml`) | "Unknown format", exit 0 | argparse error, exit 2 |

**Do the tests really catch the bugs?** The final test files were run against the code *before*
the mitigations (commit `392a387`): **15 failed, 6 passed**. On the final code: **21 passed**
(`docs/evidence/04-tests-fail-before-mitigation.txt`). One of the 15
(`test_valid_input_still_accepted`) fails on the old code only because of the new storage format
(`"5.00"` string, stripped category); that difference is intended.

### 7.4 Not executed / limitations

- Tested only on macOS 15.2 with Python 3.10.10. `pyproject.toml` declares `>=3.9`, but **3.9
  and Linux/Windows were not tested**.
- R3: no spreadsheet program was opened to confirm that the formula is evaluated; only the
  exported text was checked.
- R7/R12: no test kills a write midway or runs concurrent writes.
- `python -m build` needs network access to PyPI (isolated build env, unpinned setuptools). During the final run it stalled for several minutes on a slow connection (see the R6 residual).
- No type checker (mypy/pyright) was run; the project has no type annotations to check.
- Screenshots: all evidence is captured as text logs in `docs/evidence/`. _[Add terminal
  screenshots of `scripts/run_checks.sh` here if your instructor requires images.]_

### 7.5 Updated risk scores

| ID | Before | After | Status |
|---|---|---|---|
| R1 | 9 | 1 | Mitigated (M1) |
| R4 | 6 | 2 | Mitigated (M2) |
| R2 | 6 | 1 | Fixed in Task 2 |
| R5 | 4 | 1 | Fixed in Task 3 |
| R6 | 4 | 2 | Partially fixed (direct deps pinned) |
| R8 | 2 | 1 | Fixed as part of M2 |
| R3 | 4 | 4 | **Open**: accepted with control |
| R11 | 4 | 4 | Open |
| R7 | 3 | 3 | Open, unverified |
| R12 | 2 | 2 | Accepted |

---

## 8. Task #08 — Background agent safeguards (hypothetical design)

**Task given to an asynchronous agent:** "Mitigate R3: neutralise CSV formula injection in
`CsvFormatter`, with tests." No paid background-agent service was used; this is a design.

| Safeguard | Definition |
|---|---|
| Isolation | New branch `agent/r3-csv-escape` from `final`, checked out in a separate worktree (`git worktree add ../et-agent-r3 -b agent/r3-csv-escape final`). No access to `main` or to the user's real `expenses.json`. |
| Allowed files | Write: `expense_tracker/formatters.py`, `tests/test_formatters.py` (new). Read: the whole repository. Any other file → stop and report. |
| Allowed commands | `.venv/bin/python -m pytest`, `.venv/bin/ruff check .`, `scripts/run_checks.sh`, `git diff`, `git add`, `git commit` on its own branch only. |
| Prohibited | Push, merge, rebase or tag; editing `requirements*.txt` or `pyproject.toml`; network access; editing or deleting existing tests; `--no-verify`; any command from the AGENTS.md "Forbidden actions" list. |
| Limits | 30 min wall-clock, at most 10 test runs. If checks still fail after 3 fix attempts, stop and hand over with the failure explained. |
| Required artifacts | (1) change summary: what, why, alternatives considered; (2) `git diff final...agent/r3-csv-escape`; (3) full output of `scripts/run_checks.sh` with pass/fail totals; (4) build result; (5) risk notes: what is not covered (e.g. other export paths, false positives such as a description starting with `-`), plus anything not verified. |
| Human review gate | The owner reads the diff line by line, re-runs `scripts/run_checks.sh` locally (does not trust the agent's log), checks that AC1–AC5 still pass and that only allowed files changed (`git diff --stat`), and only then merges with `--no-ff`. No release or deploy without this approval. |
| Failure handling | If the agent times out or checks fail: the branch is kept for inspection, nothing is merged, `git worktree remove` cleans up. |
| Rollback | If a defect is found after merge: `git revert -m 1 <merge-commit>` (no history rewrite). The data-file format is not touched by this task, so no data migration or restore is needed. |

---

## 9. Task #09 — Release decision

**Decision for the final version (v0.2.0, tag `final`): CONDITIONAL.**

Supporting evidence:
- **Tests:** 28/28 pass; lint and build pass; the new tests fail on the old code (15 failed),
  which shows they detect the fixed defects.
- **Risk register:** both top risks (R1 = 9, R4 = 6) are mitigated and verified; no open risk
  scores above 4.
- **Readiness:** level 2 (Documented). Setup and checks are reproducible with one command.

Why not GO: confirmed security risk R3 is still open, the declared Python 3.9 support is
unverified, and the data-loss risk R7 is unverified. Why not NO-GO: none of these is critical
for the intended use (personal, offline, single user), and each has an explicit control and owner:

| Condition | Control | Owner | Due |
|---|---|---|---|
| R3 open | Release notes say: do not open CSV exports in a spreadsheet when descriptions come from untrusted sources. Fix scheduled as the Task 8 agent task. | Student | Next release |
| Python 3.9 unverified | Run `scripts/run_checks.sh` on 3.9, or raise `requires-python` to `>=3.10` | Student | Before publishing |
| R7 unverified | Users keep a backup copy of `expenses.json`; atomic write planned | Student | Next release |
| R11 no CI | Run `scripts/run_checks.sh` manually before every merge (AGENTS.md review gate 3) | Student | Until CI exists |

---

## 10. Task #10 — AI reflection

> **Note to the student:** the facts below describe what happened in the AI session. Sentences
> marked _[confirm]_ describe **your** personal verification, so only keep them if you really
> did it (re-run `scripts/run_checks.sh`, read the diffs). Rewrite the text in your own words.

I used Claude Code (CLI) with the Claude Opus 5.5 model. Its context was the assignment PDF, the
repository files, and, after Task 2, the AGENTS.md rules, which Claude Code loaded automatically
through a CLAUDE.md import. The assistant wrote the baseline project, the checks, the
refactoring and the mitigations, and proposed the candidate risks.

The most useful suggestion was to prove the Strategy refactoring with a byte-for-byte comparison
of all six output combinations, baseline against refactor. It is much stronger evidence than
"tests still pass", because the original tests did not cover CSV or JSON output at all.

The AI also produced weak or wrong output. Two proposed risks, path traversal and unsafe JSON
deserialisation, were unsupported: the tool is a local single-user CLI, and `json` never
executes code. Its first comparison script ran under zsh, the arguments were not split, every
`add` failed, and the script "proved" equivalence by comparing two empty outputs. The first
validation diff would also have refused to open data files created by the old version. All
three were caught only because each claim was checked against real command output.

_[confirm]_ I personally re-ran `scripts/run_checks.sh` on the baseline and final commits, read
every diff, and checked that the new tests fail on the old code. The tests changed my decisions:
the failing `pytest` command raised R2's priority, and the legacy-file test changed how M2 works.

The repository instructions helped. Once AGENTS.md was in place, the agent ran only the listed
commands, kept test data in temp directories and reported exact outputs. Next, the rules should
be enforced technically, through CI and a permissions deny-list, instead of being trusted as prose.

---

## Appendix A — AI evidence / AI-use record

| # | Tool, date | Prompt summary | Output used | Problems found | Changes made | Verification source |
|---|---|---|---|---|---|---|
| 1 | Claude Code (Claude Opus 5.5), 2026-11-21 | "Look at the Assignment #05 PDF — what has to be done?" | Summary of the 10 tasks and the deliverables | — | — | The PDF itself |
| 2 | same | "Create a suitable directory and do everything required" | Baseline project, `scripts/run_checks.sh`, baseline evidence | The first run of the check script lost exit codes (`\| tail` inside `eval`) | Rewrote the script as a reusable file with real exit codes | `01-baseline-checks.txt` |
| 3 | same | (same session) AGENTS.md, acceptance criteria and tests | AGENTS.md, CLAUDE.md, ACCEPTANCE_CRITERIA.md, `tests/test_cli.py` | Found that `pytest` fails at baseline (not planned, discovered by running it) | Added `pythonpath` config and pinned dev deps | Probe 1 before/after |
| 4 | same | Strategy refactor + equivalence proof | `formatters.py`, refactored `cli.py` | The first equivalence check compared **empty** outputs (zsh did not split `$a`), i.e. false evidence | Re-ran under bash with real data; amended the commit | `03-pattern-refactor-equivalence.txt` (47 lines each, same SHA-256) |
| 5 | same | Read-only risk review of the baseline | 12 candidate risks | R9 and R10 unsupported; R7 and R12 not reproduced | Classified accordingly; not mitigated | Risk register, probes 1–10 |
| 6 | same | Implement M1 (Decimal) | Decimal money, 5 new tests | JSON report contract changed (numbers → strings) | Accepted and documented as a trade-off | `05-final-checks.txt` probe 6 |
| 7 | same | Implement M2 (validation) | Validation, error handling, 16 tests | The first diff locked out legacy data files; `InvalidOperation` is not a `ValueError` | Lenient loading of stored records + regression test; catch `ArithmeticError` | `04-tests-fail-before-mitigation.txt`, `05-final-checks.txt` |
| 8 | same | Review of own process against AGENTS.md | — | The session committed directly to `main`, breaking review gate 1 (agent works on a branch or worktree). AGENTS.md also missed `formatters.py` and forbade the network access that `build` needs | AGENTS.md corrected; the gate is recorded here as not followed in this session | `git log`, AGENTS.md diff |
| 9 | same | Report draft (this file) | Report structure and text | Human verification statements need the student's confirmation | Marked _[confirm]_ in section 10 | — |

## Appendix B — Evidence files

| File | Content |
|---|---|
| `docs/evidence/01-baseline-checks.txt` | `scripts/run_checks.sh` on the baseline: tests, lint, build, probes 1–10 |
| `docs/evidence/03-pattern-refactor-equivalence.txt` | Byte-for-byte output comparison baseline vs refactor |
| `docs/evidence/04-tests-fail-before-mitigation.txt` | Final tests run on pre-mitigation code (15 failed) vs final (21 passed) |
| `docs/evidence/05-final-checks.txt` | `scripts/run_checks.sh` on the final version |

Reproduce any of them: `git checkout <commit> && scripts/run_checks.sh .venv/bin/python`.
