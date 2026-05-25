from bs4 import BeautifulSoup
from typing import Any

from utils.crawler import extract_links


def count_words(text: str) -> int:
    return len([word for word in text.split() if word.strip()])


def analyze_seo(html: str, base_url: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "lxml")
    issues: list[dict[str, Any]] = []

    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    title_length = len(title)
    has_title = title_length > 0

    if not has_title:
        issues.append({
            "type": "critical",
            "title": "Missing page title",
            "description": "A title tag is required for search engines to understand the page topic.",
        })
    elif title_length < 30:
        issues.append({
            "type": "medium",
            "title": "Short title tag",
            "description": f"The title is only {title_length} characters; aim for 30-60 characters.",
        })
    elif title_length > 60:
        issues.append({
            "type": "minor",
            "title": "Long title tag",
            "description": f"The title is {title_length} characters and may be truncated in search results.",
        })

    meta_description = (
        soup.find("meta", attrs={"name": "description"})
        and soup.find("meta", attrs={"name": "description"}).get("content", "")
    ) or ""
    meta_description_length = len(meta_description)
    has_meta_description = meta_description_length > 0

    if not has_meta_description:
        issues.append({
            "type": "critical",
            "title": "Missing meta description",
            "description": "Meta descriptions help search engines and users understand the page summary.",
        })
    elif meta_description_length < 120:
        issues.append({
            "type": "medium",
            "title": "Short meta description",
            "description": f"The meta description is only {meta_description_length} characters; aim for 120-160.",
        })
    elif meta_description_length > 160:
        issues.append({
            "type": "medium",
            "title": "Long meta description",
            "description": f"The meta description is {meta_description_length} characters and may be truncated.",
        })

    h1_tags = [tag.get_text(strip=True) for tag in soup.find_all("h1") if tag.get_text(strip=True)]
    h2_tags = [tag.get_text(strip=True) for tag in soup.find_all("h2") if tag.get_text(strip=True)]
    h3_tags = [tag.get_text(strip=True) for tag in soup.find_all("h3") if tag.get_text(strip=True)]

    if len(h1_tags) == 0:
        issues.append({
            "type": "critical",
            "title": "Missing H1 tag",
            "description": "Each page should have one H1 heading to define the main topic.",
        })
    elif len(h1_tags) > 1:
        issues.append({
            "type": "medium",
            "title": "Multiple H1 tags",
            "description": f"Found {len(h1_tags)} H1 tags. Use only one to avoid confusing search engines.",
        })

    if len(h2_tags) == 0:
        issues.append({
            "type": "minor",
            "title": "No H2 subheadings",
            "description": "H2 headings help structure content and improve readability.",
        })

    canonical = bool(soup.find("link", rel="canonical"))
    if not canonical:
        issues.append({
            "type": "minor",
            "title": "Missing canonical tag",
            "description": "Canonical tags avoid duplicate content issues and consolidate ranking signals.",
        })

    og_tags = bool(soup.find("meta", property="og:title") or soup.find("meta", property="og:description") or soup.find("meta", property="og:image"))
    if not og_tags:
        issues.append({
            "type": "minor",
            "title": "Missing Open Graph tags",
            "description": "Open Graph metadata improves how pages appear when shared on social media.",
        })

    twitter_tags = bool(soup.find("meta", attrs={"name": "twitter:card"}))
    if not twitter_tags:
        issues.append({
            "type": "minor",
            "title": "Missing Twitter card tags",
            "description": "Twitter metadata helps improve social sharing previews on Twitter/X.",
        })

    images = soup.find_all("img")
    image_alt_issues = sum(1 for img in images if not img.get("alt") or not img.get("alt").strip())
    if image_alt_issues > 0:
        issues.append({
            "type": "medium",
            "title": f"Missing alt text on {image_alt_issues} image(s)",
            "description": "Alt text improves image search optimization and accessibility.",
        })

    json_ld = bool(soup.find("script", type="application/ld+json"))
    if not json_ld:
        issues.append({
            "type": "medium",
            "title": "Missing JSON-LD schema markup",
            "description": "Structured data helps search engines understand the page and generate rich results.",
        })

    body_text = soup.body.get_text(separator=" ", strip=True) if soup.body else ""
    word_count = count_words(body_text)
    if word_count < 300:
        issues.append({
            "type": "minor",
            "title": "Thin content",
            "description": f"The page has only {word_count} words. Longer, more comprehensive pages often rank better.",
        })

    links = extract_links(html, base_url)

    return {
        "title": title,
        "title_length": title_length,
        "has_title": has_title,
        "meta_description": meta_description,
        "meta_description_length": meta_description_length,
        "has_meta_description": has_meta_description,
        "h1_count": len(h1_tags),
        "h1_content": h1_tags,
        "h2_count": len(h2_tags),
        "h2_content": h2_tags,
        "h3_count": len(h3_tags),
        "has_canonical": canonical,
        "has_og_tags": og_tags,
        "has_twitter_tags": twitter_tags,
        "image_alt_issues": image_alt_issues,
        "total_images": len(images),
        "internal_links": len(links["internal"]),
        "external_links": len(links["external"]),
        "has_schema": json_ld,
        "word_count": word_count,
        "issues": issues,
    }
