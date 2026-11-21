"""Acceptance tests: CLI behaviour that must stay true after every change (see ACCEPTANCE_CRITERIA.md)."""
import csv
import io
import json

from expense_tracker.cli import main


def run(capsys, *argv):
    main(list(argv))
    return capsys.readouterr().out


def seed(capsys, data_file):
    run(capsys, "--file", data_file, "add", "2026-11-01", "food", "12.50", "lunch")
    run(capsys, "--file", data_file, "add", "2026-11-02", "transport", "3", "bus")
    run(capsys, "--file", data_file, "add", "2026-11-03", "food", "7.50", "coffee")


def test_ac1_add_persists_and_list_shows_expense(tmp_path, capsys):
    data_file = str(tmp_path / "e.json")
    out = run(capsys, "--file", data_file, "add", "2026-11-01", "food", "12.50", "lunch")
    assert out.strip() == "Added: 2026-11-01 food 12.50"

    stored = json.loads((tmp_path / "e.json").read_text())
    assert len(stored) == 1 and stored[0]["category"] == "food"

    out = run(capsys, "--file", data_file, "list")
    assert "2026-11-01" in out and "food" in out and "12.50" in out and "lunch" in out


def test_ac2_report_totals_per_category_and_overall(tmp_path, capsys):
    data_file = str(tmp_path / "e.json")
    seed(capsys, data_file)
    lines = run(capsys, "--file", data_file, "report").splitlines()
    assert lines == [
        "food              20.00",
        "transport          3.00",
        "TOTAL             23.00",
    ]


def test_ac3_list_and_report_support_text_csv_json(tmp_path, capsys):
    data_file = str(tmp_path / "e.json")
    seed(capsys, data_file)

    rows = list(csv.reader(io.StringIO(run(capsys, "--file", data_file, "list", "--format", "csv"))))
    assert rows[0] == ["date", "category", "amount", "description"]
    assert len(rows) == 4

    rows = list(csv.reader(io.StringIO(run(capsys, "--file", data_file, "report", "--format", "csv"))))
    assert rows[0] == ["category", "amount"]
    assert rows[-1][0] == "TOTAL"

    listed = json.loads(run(capsys, "--file", data_file, "list", "--format", "json"))
    assert [e["description"] for e in listed] == ["lunch", "bus", "coffee"]

    report = json.loads(run(capsys, "--file", data_file, "report", "--format", "json"))
    assert set(report) == {"by_category", "total"}
    assert set(report["by_category"]) == {"food", "transport"}


def test_ac4_split_prints_rounded_share(tmp_path, capsys):
    data_file = str(tmp_path / "e.json")
    seed(capsys, data_file)
    assert run(capsys, "--file", data_file, "split", "3").strip() == "Each person pays: 7.67"
