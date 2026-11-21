"""Output formats (Strategy pattern): one class per format, selected by name in cli.py."""
import csv
import io
import json


class TextFormatter:
    def expenses(self, expenses):
        return "".join(
            f"{e.date}  {e.category:<12} {e.amount:>10.2f}  {e.description}\n" for e in expenses
        )

    def report(self, by_category, total):
        lines = [f"{cat:<12} {amount:>10.2f}" for cat, amount in by_category.items()]
        lines.append(f"{'TOTAL':<12} {total:>10.2f}")
        return "\n".join(lines) + "\n"


class CsvFormatter:
    def _write(self, rows):
        buf = io.StringIO()
        csv.writer(buf).writerows(rows)
        return buf.getvalue()

    def expenses(self, expenses):
        rows = [["date", "category", "amount", "description"]]
        rows += [[e.date, e.category, e.amount, e.description] for e in expenses]
        return self._write(rows)

    def report(self, by_category, total):
        rows = [["category", "amount"]]
        rows += [[cat, amount] for cat, amount in by_category.items()]
        rows.append(["TOTAL", total])
        return self._write(rows)


class JsonFormatter:
    def expenses(self, expenses):
        return json.dumps([e.to_dict() for e in expenses], indent=2) + "\n"

    def report(self, by_category, total):
        return json.dumps({"by_category": by_category, "total": total}, indent=2) + "\n"


FORMATTERS = {
    "text": TextFormatter(),
    "csv": CsvFormatter(),
    "json": JsonFormatter(),
}
