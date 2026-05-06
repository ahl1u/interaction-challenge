from sqlite3 import Connection


def export_csv(conn: Connection, path: str) -> None:
    """Export the orders table to a CSV file."""
    raise NotImplementedError
