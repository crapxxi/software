#!/usr/bin/env bash
# Runs tests, lint, build and CLI behaviour probes; prints commands, output and exit codes.
# Usage: scripts/run_checks.sh <python-interpreter>   (run from repository root)
PY="${1:-.venv/bin/python}"
BIN="$(dirname "$PY")"
T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT

run() {
  echo "\$ $*"
  out="$("$@" 2>&1)"; code=$?
  if [ "$(printf '%s\n' "$out" | wc -l)" -gt 25 ]; then
    printf '%s\n' "$out" | tail -n 25 | sed 's/^/  /'
  else
    printf '%s\n' "$out" | sed 's/^/  /'
  fi
  echo "  [exit code: $code]"; echo
}
cli() { run "$PY" -m expense_tracker --file "$@"; }

echo "# Checks for commit $(git rev-parse --short HEAD) — $(date '+%Y-%m-%d %H:%M %Z')"
echo "# Env: macOS $(sw_vers -productVersion 2>/dev/null), $("$PY" --version)"
echo "# Data files are created in a temporary directory (shown below as \$T)"; echo

echo "## 1. Tests (as documented in README: plain 'pytest')"
run "$BIN/pytest" -q
echo "## 2. Tests (python -m pytest, adds cwd to sys.path)"
run "$PY" -m pytest -q
echo "## 3. Lint"
run "$BIN/ruff" check .
echo "## 4. Build"
rm -rf "$T/dist"; run "$PY" -m build --wheel --outdir "$T/dist" .

echo "## 5. Smoke test"
cli "$T/e.json" add 2026-11-01 food 12.50 lunch
cli "$T/e.json" add 2026-11-02 transport 3 bus
cli "$T/e.json" report
cli "$T/e.json" split 2

echo "## 6. Probe: money arithmetic 0.10 + 0.20"
cli "$T/f.json" add 2026-11-01 food 0.10
cli "$T/f.json" add 2026-11-01 food 0.20
cli "$T/f.json" report --format json

echo "## 7. Probe: invalid input"
cli "$T/g.json" add 2026-11-01 food -50
cli "$T/g.json" add 2026-11-01 food abc
cli "$T/e.json" split 0

echo "## 8. Probe: CSV formula injection"
cli "$T/h.json" add 2026-11-01 food 1 '=HYPERLINK("http://evil.example","x")'
cli "$T/h.json" list --format csv

echo "## 9. Probe: corrupt data file"
echo '{broken' > "$T/c.json"
cli "$T/c.json" list

echo "## 10. Probe: unknown output format"
cli "$T/e.json" list --format xml
