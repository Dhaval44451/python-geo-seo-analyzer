import httpx
import time
from typing import Any

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
             " (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
COMMON_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://www.google.com/",
}
TIMEOUT = 15.0


async def fetch_page(url: str) -> dict[str, Any]:
    start = time.time()

    async with httpx.AsyncClient(timeout=TIMEOUT, headers=COMMON_HEADERS, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()

    html = response.text
    elapsed = int((time.time() - start) * 1000)

    title = None
    description = None
    try:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "lxml")
        title = soup.title.string.strip() if soup.title and soup.title.string else None
        description = (
            soup.find("meta", attrs={"name": "description"})
            and soup.find("meta", attrs={"name": "description"}).get("content")
        )
    except Exception:
        pass

    return {
        "url": url,
        "html": html,
        "title": title,
        "description": description,
        "status_code": response.status_code,
        "load_time_ms": elapsed,
    }


async def fetch_text_file(url: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=TIMEOUT, headers=COMMON_HEADERS, follow_redirects=True) as client:
        response = await client.get(url)
    return {
        "success": response.status_code == 200,
        "status_code": response.status_code,
        "content": response.text if response.status_code == 200 else "",
    }


def extract_links(html: str, base_url: str) -> dict[str, list[str]]:
    from bs4 import BeautifulSoup
    from urllib.parse import urlparse, urljoin

    soup = BeautifulSoup(html, "lxml")
    base_origin = urlparse(base_url).netloc
    internal_urls = set()
    external_urls = set()

    for anchor in soup.find_all("a", href=True):
        href = anchor["href"].strip()
        if not href or href.startswith("mailto:") or href.startswith("javascript:"):
            continue
        try:
            absolute_url = urljoin(base_url, href)
            parsed = urlparse(absolute_url)
            if parsed.netloc == base_origin:
                internal_urls.add(absolute_url)
            else:
                external_urls.add(absolute_url)
        except Exception:
            continue

    return {"internal": sorted(internal_urls), "external": sorted(external_urls)}
