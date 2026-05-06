from pathlib import Path

from src.clean import clean_html


def main() -> None:
    """Preview cleaned fixture output for parser development."""
    fixtures_dir = Path(__file__).parent / "fixtures"
    for fixture in sorted(fixtures_dir.glob("*.html")):
        print(f"===== {fixture.name} =====")
        print(clean_html(fixture.read_text()))
        print()


if __name__ == "__main__":
    main()
