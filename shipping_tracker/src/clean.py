import re
from typing import Optional

from bs4 import BeautifulSoup


def clean_html(html: str) -> str:
    """Convert a shipping email HTML document into LLM-friendly text."""
    soup = BeautifulSoup(html, "html.parser")

    # remove useless css/js
    for tag in soup(["script", "style", "head", "meta", "link"]):
        tag.decompose()

    #remove tracking pixels
    for img in soup.find_all("img"):
        width = _dimension_value(img.get("width"))
        height = _dimension_value(img.get("height"))
        if (width is not None and width <= 2) or (height is not None and height <= 2):
            img.decompose()

    #check links for tracking number
    for link in soup.find_all("a"):
        href = link.get("href")
        if href and any(term in href.lower() for term in ("track", "tracking", "tracknum")):
            link.append(f" [link: {href}]")

    #all text
    text = soup.get_text(separator="\n")
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _dimension_value(value: Optional[str]) -> Optional[int]:
    """Return the leading integer dimension from an HTML attribute."""
    if value is None:
        return None
    match = re.match(r"\s*(\d+)", value)
    if match is None:
        return None
    return int(match.group(1))
