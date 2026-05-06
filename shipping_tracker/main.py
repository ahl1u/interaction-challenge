import json
from pathlib import Path

from src.clean import clean_html
from src.parser import parse_email


def main() -> None:
    """Preview parsed fixture output for parser development."""
    fixtures_dir = Path(__file__).parent / "fixtures"
    for fixture in sorted(fixtures_dir.glob("*.html")):
        print(f"===== {fixture.name} =====")
        parsed = parse_email(clean_html(fixture.read_text()))
        print(json.dumps(parsed, indent=2, sort_keys=True))
        print()


if __name__ == "__main__":
    main()
