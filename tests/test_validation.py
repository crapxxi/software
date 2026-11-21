"""R4: invalid input must be rejected with a readable error and exit code 2, never stored."""
import json

import pytest

from expense_tracker.cli import main


def run_error(capsys, *argv):
    with pytest.raises(SystemExit) as exc:
        main(list(argv))
    captured = capsys.readouterr()
    assert exc.value.code == 2
    assert "Traceback" not in captured.err
    return captured.err


@pytest.mark.parametrize(
    "amount, message",
    [
        ("-50", "positive"),
        ("0", "positive"),
        ("abc", "must be a number"),
        ("NaN", "positive"),
        ("Infinity", "positive"),
        ("1.005", "2 decimal places"),
    ],
)
def test_add_rejects_invalid_amount(tmp_path, capsys, amount, message):
    data_file = tmp_path / "e.json"
    err = run_error(capsys, "--file", str(data_file), "add", "2026-11-01", "food", amount)
    assert message in err
    assert not data_file.exists()


@pytest.mark.parametrize("bad_date", ["not-a-date", "2026-13-01", "01.11.2026"])
def test_add_rejects_invalid_date(tmp_path, capsys, bad_date):
    err = run_error(capsys, "--file", str(tmp_path / "e.json"), "add", bad_date, "food", "1")
    assert "YYYY-MM-DD" in err


def test_add_rejects_empty_category(tmp_path, capsys):
    err = run_error(capsys, "--file", str(tmp_path / "e.json"), "add", "2026-11-01", "  ", "1")
    assert "category" in err


def test_split_rejects_zero_people(tmp_path, capsys):
    err = run_error(capsys, "--file", str(tmp_path / "e.json"), "split", "0")
    assert "at least 1" in err


def test_corrupt_data_file_gives_readable_error_and_is_not_overwritten(tmp_path, capsys):
    data_file = tmp_path / "e.json"
    data_file.write_text("{broken")
    err = run_error(capsys, "--file", str(data_file), "add", "2026-11-01", "food", "1")
    assert "cannot read data file" in err
    assert data_file.read_text() == "{broken"


def test_valid_input_still_accepted(tmp_path, capsys):
    data_file = tmp_path / "e.json"
    main(["--file", str(data_file), "add", "2026-11-01", " food ", "5"])
    assert json.loads(data_file.read_text())[0] == {
        "date": "2026-11-01", "category": "food", "amount": "5.00", "description": ""
    }


def test_legacy_file_with_negative_amount_still_loads(tmp_path, capsys):
    # v0.1.0 accepted negative amounts; existing data must stay readable.
    data_file = tmp_path / "e.json"
    data_file.write_text('[{"date": "2026-11-01", "category": "refund", "amount": -50.0}]')
    main(["--file", str(data_file), "report"])
    assert "TOTAL" in capsys.readouterr().out


def test_data_file_with_non_numeric_amount_gives_readable_error(tmp_path, capsys):
    data_file = tmp_path / "e.json"
    data_file.write_text('[{"date": "2026-11-01", "category": "food", "amount": "abc"}]')
    err = run_error(capsys, "--file", str(data_file), "list")
    assert "cannot read data file" in err
