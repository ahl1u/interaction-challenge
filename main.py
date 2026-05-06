import json
from pathlib import Path

from src.db import init_db
from src.export import export_csv
from src.pipeline import process_email


def main() -> None:
    """Run fixtures through the pipeline and export current order state."""
    base_dir = Path(__file__).parent
    fixtures_dir = base_dir / "fixtures"
    conn = init_db(str(base_dir / "orders.db"))

    for fixture in sorted(fixtures_dir.glob("*.html")):
        print(f"===== {fixture.name} =====")
        result = process_email(fixture.read_text(), conn)
        print(json.dumps(result, indent=2, sort_keys=True))
        print()

    export_csv(conn, str(base_dir / "orders.csv"))


if __name__ == "__main__":
    main()
