import json
import os
import re
from typing import Optional

import requests
from dotenv import load_dotenv


MODEL = "anthropic/claude-haiku-4.5"
MAX_INPUT_CHARS = 8000
MAX_TOKENS = 400
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

PROMPT_TEMPLATE = """You are extracting structured shipping information from a retail email.

Return ONLY a JSON object with this exact schema. No prose, no markdown, no code fences.

{{
  "order_id": string | null,
  "carrier": string | null,
  "tracking_number": string | null,
  "status": string,
  "retailer": string | null,
  "estimated_delivery": string | null,
  "item_summary": string | null,
  "confidence": number
}}

Status must be exactly one of: "ordered", "shipped", "out_for_delivery", "delivered", "exception", "unknown".

Status definitions:
- "ordered": order placed/confirmed, not yet shipped
- "shipped": package handed to carrier, in transit
- "out_for_delivery": on the truck for delivery today
- "delivered": package delivered to recipient
- "exception": delivery problem (failed attempt, address issue, damaged, returned, weather delay)
- "unknown": email is not a shipping/order email, OR it is but the status is unclear

If the email is promotional/marketing (e.g., "free shipping weekend", restock alerts, sale announcements) and NOT about a specific order, return status "unknown" with confidence 0.0.

Estimated delivery should be ISO format YYYY-MM-DD if a specific date is given, else null.
Item summary max 100 chars.
Confidence is your 0.0-1.0 confidence in the status field.

Email content:
---
{email_text}
---

JSON:"""


def parse_email(text: str) -> Optional[dict]:
    """Parse cleaned email text into structured shipping information."""
    prompt = PROMPT_TEMPLATE.format(email_text=text[:MAX_INPUT_CHARS])
    response = _call_openrouter(prompt)

    parsed = _parse_json(response)
    if parsed is not None:
        return parsed

    parsed = _parse_json_block(response)
    if parsed is not None:
        return parsed

    fix_prompt = (
        "Return ONLY valid JSON for this invalid model response. "
        "No prose, no markdown, no code fences.\n\n"
        f"Invalid response:\n{response}"
    )
    fixed_response = _call_openrouter(fix_prompt)
    return _parse_json(fixed_response) or _parse_json_block(fixed_response)


def _call_openrouter(prompt: str) -> str:
    """Call OpenRouter and return the first message content."""
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is required")

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": MAX_TOKENS,
    }
    try:
        response = requests.post(
            OPENROUTER_URL,
            json=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=60,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"OpenRouter request failed: {exc}") from exc

    data = response.json()
    return data["choices"][0]["message"]["content"]


def _parse_json(response: str) -> Optional[dict]:
    try:
        parsed = json.loads(response)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _parse_json_block(response: str) -> Optional[dict]:
    match = re.search(r"\{.*\}", response, re.DOTALL)
    if match is None:
        return None
    return _parse_json(match.group(0))
