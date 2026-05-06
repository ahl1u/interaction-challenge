from dataclasses import dataclass
from datetime import datetime, timezone
import sqlite3
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
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT NOT NULL,
            retailer TEXT,
            status TEXT NOT NULL,
            carrier TEXT,
            tracking_number TEXT,
            estimated_delivery TEXT,
            item_summary TEXT,
            first_seen_at TEXT NOT NULL,
            last_updated_at TEXT NOT NULL,
            last_notified_status TEXT,
            PRIMARY KEY (order_id, retailer)
        );

        CREATE TABLE IF NOT EXISTS status_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL,
            retailer TEXT,
            status TEXT NOT NULL,
            seen_at TEXT NOT NULL,
            raw_email_hash TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_history_order ON status_history(order_id, retailer);
        CREATE UNIQUE INDEX IF NOT EXISTS idx_history_dedup ON status_history(raw_email_hash);
        """
    )
    conn.commit()
    return conn


def upsert_order(conn: Connection, parsed: dict, email_hash: str) -> Optional[Transition]:
    """Insert or update an order from parsed email data."""
    if parsed.get("status") == "unknown" or not parsed.get("order_id"):
        return None

    #check if duplicate email processing
    existing_hash = conn.execute(
        "SELECT 1 FROM status_history WHERE raw_email_hash = ?", (email_hash,)
    ).fetchone()
    if existing_hash is not None:
        return None

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    order_id = parsed["order_id"]
    retailer = parsed.get("retailer")
    status = parsed["status"]

    with conn:
        #check if order exists in db
        existing_order = conn.execute(
            "SELECT status, last_notified_status FROM orders WHERE order_id = ? AND retailer IS ?",
            (order_id, retailer),
        ).fetchone()

        if existing_order is None:
            conn.execute(
                """
                INSERT INTO orders (
                    order_id, retailer, status, carrier, tracking_number,
                    estimated_delivery, item_summary, first_seen_at,
                    last_updated_at, last_notified_status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
                """,
                (
                    order_id,
                    retailer,
                    status,
                    parsed.get("carrier"),
                    parsed.get("tracking_number"),
                    parsed.get("estimated_delivery"),
                    parsed.get("item_summary"),
                    now,
                    now,
                ),
            )
            transition = Transition(True, None, status, None)
        else:
            conn.execute(
                """
                UPDATE orders
                SET status = ?,
                    carrier = COALESCE(?, carrier),
                    tracking_number = COALESCE(?, tracking_number),
                    estimated_delivery = COALESCE(?, estimated_delivery),
                    item_summary = COALESCE(?, item_summary),
                    last_updated_at = ?
                WHERE order_id = ? AND retailer IS ?
                """,
                (
                    status,
                    parsed.get("carrier"),
                    parsed.get("tracking_number"),
                    parsed.get("estimated_delivery"),
                    parsed.get("item_summary"),
                    now,
                    order_id,
                    retailer,
                ),
            )
            transition = Transition(
                False,
                existing_order["status"],
                status,
                existing_order["last_notified_status"],
            )

        conn.execute(
            """
            INSERT INTO status_history (order_id, retailer, status, seen_at, raw_email_hash)
            VALUES (?, ?, ?, ?, ?)
            """,
            (order_id, retailer, status, now, email_hash),
        )

    return transition


def mark_notified(conn: Connection, order_id: str, retailer: Optional[str], status: str) -> None:
    """Record that an SMS was successfully sent for an order status."""
    with conn:
        conn.execute(
            """
            UPDATE orders
            SET last_notified_status = ?
            WHERE order_id = ? AND retailer IS ?
            """,
            (status, order_id, retailer),
        )
