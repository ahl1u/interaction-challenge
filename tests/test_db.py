from src.db import init_db, upsert_order


def test_upsert_matches_missing_order_id_by_tracking_number(tmp_path):
    conn = init_db(str(tmp_path / "orders.db"))
    first = {
        "order_id": "1029384756",
        "retailer": "StockX",
        "status": "shipped",
        "carrier": "UPS",
        "tracking_number": "1Z999AA10123456784",
        "estimated_delivery": "2026-05-12",
        "item_summary": "Jordan 4 Retro Bred Reimagined",
        "confidence": 0.95,
    }
    follow_up = {
        "order_id": None,
        "retailer": None,
        "status": "out_for_delivery",
        "carrier": "UPS",
        "tracking_number": "1Z999AA10123456784",
        "estimated_delivery": None,
        "item_summary": None,
        "confidence": 0.95,
    }

    upsert_order(conn, first, "email-1")
    transition = upsert_order(conn, follow_up, "email-2")

    assert transition is not None
    assert transition.prev_status == "shipped"
    assert transition.new_status == "out_for_delivery"

    order = conn.execute(
        "SELECT order_id, retailer, status, item_summary FROM orders"
    ).fetchone()
    assert order["order_id"] == "1029384756"
    assert order["retailer"] == "StockX"
    assert order["status"] == "out_for_delivery"
    assert order["item_summary"] == "Jordan 4 Retro Bred Reimagined"
