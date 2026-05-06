def should_send_sms(transition, confidence: float) -> bool:
    """Return whether an SMS should be sent for a transition."""
    raise NotImplementedError


def format_sms(parsed: dict, status: str) -> str:
    """Format a short SMS notification for a parsed order status."""
    raise NotImplementedError


def send_sms(body: str) -> bool:
    """Send an SMS notification, or print it when DRY_RUN is enabled."""
    raise NotImplementedError
