import hashlib
from sqlite3 import Connection

from src.clean import clean_html
from src.db import upsert_order
from src.parser import parse_email


def process_email(html: str, conn: Connection) -> dict:
    """Process one raw HTML email through the shipping tracker pipeline."""
    cleaned = clean_html(html)
    email_hash = hashlib.sha256(cleaned.encode("utf-8")).hexdigest()
    parsed = parse_email(cleaned)
    if parsed is None:
        return {"status": "parse_failed"}

    transition = upsert_order(conn, parsed, email_hash)
    if transition is None:
        return {"status": "skipped", "parsed_status": parsed.get("status")}

    return {
        "status": "updated_silently",
        "order_id": parsed.get("order_id"),
        "retailer": parsed.get("retailer"),
        "prev_status": transition.prev_status,
        "new_status": transition.new_status,
    }
