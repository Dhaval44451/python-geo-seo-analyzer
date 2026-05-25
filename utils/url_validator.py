from urllib.parse import urlparse


def is_valid_url(url: str) -> bool:
    try:
        parsed = urlparse(url if url.startswith(("http://", "https://")) else f"https://{url}")
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False


def normalize_url(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    try:
        parsed = urlparse(url)
        normalized = parsed.geturl()
        return normalized
    except Exception:
        return url


def get_base_url(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"
