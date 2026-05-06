from sqlite3 import Connection


def process_email(html: str, conn: Connection) -> dict:
    """Process one raw HTML email through the shipping tracker pipeline."""
    raise NotImplementedError
