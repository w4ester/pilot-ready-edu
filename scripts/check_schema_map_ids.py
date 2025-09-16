"""Verify schema map table_ids are sequential and unique.

Run:
    python scripts/check_schema_map_ids.py
"""

import json
import sys
from pathlib import Path

SCHEMA_MAP = Path("01_database_schema_map_updated_v2.json")


def main() -> int:
    if not SCHEMA_MAP.exists():
        print(f"Schema map not found: {SCHEMA_MAP}", file=sys.stderr)
        return 1

    data = json.loads(SCHEMA_MAP.read_text())
    tables = data.get("tables", [])
    ids = [table.get("table_id") for table in tables]

    if any(id_ is None for id_ in ids):
        print("One or more tables are missing a table_id.", file=sys.stderr)
        return 1

    expected = list(range(1, len(ids) + 1))
    if ids != expected:
        print("table_id sequence mismatch.", file=sys.stderr)
        print(f"  expected: {expected}", file=sys.stderr)
        print(f"  actual:   {ids}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
