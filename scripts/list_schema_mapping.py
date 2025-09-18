"""Generate a mapping report of SQL tables vs SQLAlchemy models.

Usage:
    python scripts/list_schema_mapping.py [--format markdown|csv]

The script scans `db/database_schema_consolidated.sql` for `CREATE TABLE`
statements and `backend/app/db/models.py` for SQLAlchemy models that
declare `__tablename__`. It prints a checklist indicating which SQL
tables have corresponding ORM classes and which ORM classes refer to
unknown tables.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Iterable

SQL_PATH = Path("db/database_schema_consolidated.sql")
MODELS_PATH = Path("backend/app/db/models.py")

CREATE_TABLE_REGEX = re.compile(
    r"CREATE\s+TABLE\s+IF\s+NOT\s+EXISTS\s+(\w+)", re.IGNORECASE
)
CLASS_REGEX = re.compile(r"^class\s+(?P<class_name>\w+)\(Base\):", re.MULTILINE)
TABLENAME_REGEX = re.compile(
    r"__tablename__\s*=\s*\"(?P<table>[^\"]+)\"|__tablename__\s*=\s*\'(?P<table_sq>[^\']+)\'"
)


def extract_sql_tables(sql_text: str) -> list[str]:
    """Return ordered list of table names from the SQL snapshot."""

    return CREATE_TABLE_REGEX.findall(sql_text)


def extract_orm_mappings(models_text: str) -> dict[str, str]:
    """Return mapping of table name → ORM class name."""

    mappings: dict[str, str] = {}
    for class_match in CLASS_REGEX.finditer(models_text):
        class_start = class_match.end()
        class_body = models_text[class_start : class_start + 500]
        tablename_match = TABLENAME_REGEX.search(class_body)
        if not tablename_match:
            continue
        table = tablename_match.group("table") or tablename_match.group("table_sq")
        mappings[table] = class_match.group("class_name")
    return mappings


def to_markdown(report_rows: Iterable[tuple[str, str, str]]) -> None:
    print("| Status | Table | ORM Class |")
    print("| --- | --- | --- |")
    for status, table, cls in report_rows:
        print(f"| {status} | `{table}` | {cls or ''} |")


def to_csv(report_rows: Iterable[tuple[str, str, str]]) -> None:
    writer = csv.writer(sys.stdout)
    writer.writerow(["status", "table", "orm_class"])
    for row in report_rows:
        writer.writerow(row)


def main() -> int:
    parser = argparse.ArgumentParser(description="List schema mapping coverage")
    parser.add_argument("--format", choices={"markdown", "csv"}, default="markdown")
    args = parser.parse_args()

    if not SQL_PATH.exists():
        parser.error(f"SQL file not found: {SQL_PATH}")
    if not MODELS_PATH.exists():
        parser.error(f"Models file not found: {MODELS_PATH}")

    sql_tables = extract_sql_tables(SQL_PATH.read_text())
    orm_map = extract_orm_mappings(MODELS_PATH.read_text())

    seen_tables = set()
    report_rows: list[tuple[str, str, str]] = []

    for table in sql_tables:
        seen_tables.add(table)
        status = "[x]" if table in orm_map else "[ ]"
        report_rows.append((status, table, orm_map.get(table, "")))

    # Include ORM classes that reference tables not in SQL snapshot
    for table, cls in sorted(orm_map.items()):
        if table not in seen_tables:
            report_rows.append(("[?]", table, cls))

    if args.format == "markdown":
        to_markdown(report_rows)
    else:
        to_csv(report_rows)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
