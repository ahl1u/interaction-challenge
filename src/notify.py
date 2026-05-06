import os

from dotenv import load_dotenv
from twilio.rest import Client


NOTIFIABLE = {"shipped", "out_for_delivery", "delivered", "exception"}
STATUS_RANK = {"ordered": 0, "shipped": 1, "out_for_delivery": 2, "delivered": 3}


def should_send_sms(transition, confidence: float) -> bool:
    """Return whether an SMS should be sent for a transition."""
    if transition.new_status not in NOTIFIABLE:
        return False
    if confidence < 0.7:
        return False
    if transition.last_notified_status == transition.new_status:
        return False
    if transition.new_status != "exception":
        prev_rank = STATUS_RANK.get(transition.prev_status)
        new_rank = STATUS_RANK.get(transition.new_status)
        if prev_rank is not None and new_rank is not None and new_rank < prev_rank:
            return False
    return True


def format_sms(parsed: dict, status: str) -> str:
    """Format a short SMS notification for a parsed order status."""
    retailer = parsed.get("retailer") or "Your order"
    item = parsed.get("item_summary")
    tracking = parsed.get("tracking_number")

    templates = {
        "shipped": f"📦 {retailer} shipped",
        "out_for_delivery": f"🚚 {retailer} out for delivery today",
        "delivered": f"✅ {retailer} delivered",
        "exception": f"⚠️ {retailer} delivery issue",
    }
    body = templates[status]
    if item:
        body = f"{body} — {item}"
    if status in {"shipped", "out_for_delivery"} and tracking:
        body = f"{body}\nTracking: {tracking}"
    # cap to ensure message is not overly long
    return body[:300]


def send_sms(body: str) -> bool:
    """Send an SMS notification, or print it when DRY_RUN is enabled."""
    load_dotenv()
    dry_run = os.getenv("DRY_RUN", "true").lower() == "true"
    if dry_run:
        print(f"DRY_RUN SMS:\n{body}")
        return True

    try:
        client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
        client.messages.create(
            body=body,
            from_=os.environ["TWILIO_FROM_NUMBER"],
            to=os.environ["TWILIO_TO_NUMBER"],
        )
    except Exception:
        return False
    return True
