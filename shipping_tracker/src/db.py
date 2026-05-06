from dataclasses import dataclass
from sqlite3 import Connection
from typing import Optional


@dataclass
class Transition:
    """Represents an order status transition after processing an email."""

    is_new_order: bool
    prev_status: Optional[str]
    new_status: str
    last_notified_status: Optional[str]


def init_db(path: str) -> Connection:
    """Create and return a SQLite connection with required tables/indexes."""
    raise NotImplementedError


def upsert_order(conn: Connection, parsed: dict, email_hash: str) -> Transition | None:
    """Insert or update an order from parsed email data."""
    raise NotImplementedError


def mark_notified(conn: Connection, order_id: str, retailer: str | None, status: str) -> None:
    """Record that an SMS was successfully sent for an order status."""
    raise NotImplementedError
