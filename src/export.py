from sqlite3 import Connection

import pandas as pd


ORDER_COLUMNS = [
    "order_id",
    "retailer",
    "status",
    "carrier",
    "tracking_number",
    "estimated_delivery",
    "item_summary",
    "first_seen_at",
    "last_updated_at",
    "last_notified_status",
]


def export_csv(conn: Connection, path: str) -> None:
    """Export the orders table to a CSV file."""
    df = pd.read_sql_query(f"SELECT {', '.join(ORDER_COLUMNS)} FROM orders", conn)
    df.to_csv(path, index=False)
