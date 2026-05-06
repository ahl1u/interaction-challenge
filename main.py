import json
from pathlib import Path

from src.db import init_db
from src.pipeline import process_email


def main() -> None:
    """Run fixtures through the pipeline without notification."""
    base_dir = Path(__file__).parent
    fixtures_dir = base_dir / "fixtures"
    conn = init_db(str(base_dir / "orders.db"))

    for fixture in sorted(fixtures_dir.glob("*.html")):
        print(f"===== {fixture.name} =====")
        result = process_email(fixture.read_text(), conn)
        print(json.dumps(result, indent=2, sort_keys=True))
        print()


if __name__ == "__main__":
    main()
