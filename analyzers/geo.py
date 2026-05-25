from bs4 import BeautifulSoup
from typing import Any


def analyze_geo(html: str, seo_data: dict[str, Any]) -> dict[str, Any]:
    soup = BeautifulSoup(html, "lxml")
    body_text = soup.body.get_text(separator=" ", strip=True) if soup.body else ""
    issues: list[dict[str, Any]] = []

    paragraph_count = len(soup.find_all("p"))
    list_count = len(soup.find_all(["ul", "ol"]))
    header_count = len(soup.find_all(["h2", "h3", "h4"]))

    content_chunking = min(100, 30 + paragraph_count * 2 + list_count * 4 + header_count * 3)
    if content_chunking < 60:
        issues.append({
            "type": "medium",
            "title": "Weak content chunking",
            "description": "The page should use more headings, lists, and sections to make content easier for AI systems to parse.",
        })

    conversational_count = len([token for token in ["you", "your", "we", "our", "let's", "let us"] if token.lower() in body_text.lower()])
    conversational_readability = conversational_count >= 4
    if not conversational_readability:
        issues.append({
            "type": "minor",
            "title": "Formal tone detected",
            "description": "A more conversational tone helps AI systems generate helpful responses for user-focused queries.",
        })

    faq_section = bool(
        soup.find(lambda tag: tag.name in {"h2", "h3"} and "faq" in tag.get_text(strip=True).lower())
        or soup.select_one(".faq")
        or soup.select_one("[data-faq]")
    )
    if not faq_section:
        issues.append({
            "type": "medium",
            "title": "Missing FAQ section",
            "description": "FAQ sections are favored by AI and search systems when generating concise answers to user questions.",
        })

    entity_patterns = [
        r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",
        r"\$\d+[\d,\.]*",
        r"\d+%",
        r'"[^\n"]+"',
    ]
    import re

    entity_count = sum(len(re.findall(pattern, body_text)) for pattern in entity_patterns)
    if entity_count < 10:
        issues.append({
            "type": "medium",
            "title": "Low entity richness",
            "description": "The page includes few names, statistics, or quotes, which can reduce AI relevance signals.",
        })

    direct_answer = bool(re.search(r"^[A-Z][^\.!?]{20,}[\.!?]", body_text))
    structured_answers = bool(soup.find("strong") or soup.find("b"))
    snippet_readiness = 0
    snippet_readiness += 30 if direct_answer else 0
    snippet_readiness += 25 if structured_answers else 0
    snippet_readiness += 20 if seo_data.get("h2_count", 0) > 0 else 0
    snippet_readiness += 15 if faq_section else 0
    snippet_readiness += 10 if seo_data.get("has_schema") else 0
    snippet_readiness = min(100, snippet_readiness)
    if snippet_readiness < 60:
        issues.append({
            "type": "medium",
            "title": "Low AI snippet readiness",
            "description": "The page structure is not optimized for quick answer generation by AI systems.",
        })

    eeat_signals = 0
    if re.search(r"\b(expert|specialist|professional|experienced|certified)\b", body_text, re.IGNORECASE):
        eeat_signals += 1
    if soup.select_one("[class*=author], [class*=byline], .expert-bio"):
        eeat_signals += 1
    if re.search(r"\b(years? of experience|since \d{4}|decades?)\b", body_text, re.IGNORECASE):
        eeat_signals += 1
    if seo_data.get("has_schema"):
        eeat_signals += 1
    if soup.find("link", rel="me"):
        eeat_signals += 1
    if re.search(r"\b(award|recognized|featured|published)\b", body_text, re.IGNORECASE):
        eeat_signals += 1
    if soup.find("a", href=lambda value: value and value.startswith("https")):
        eeat_signals += 1

    if eeat_signals < 3:
        issues.append({
            "type": "medium",
            "title": "Weak E-E-A-T signals",
            "description": "The content lacks strong expertise, authoritativeness, or trust indicators.",
        })

    structured_content = 0
    structured_content += 25 if soup.find(["ul", "ol"]) else 0
    structured_content += 25 if soup.find(["dl", ".definition"]) else 0
    structured_content += 25 if soup.find("table") else 0
    structured_content += 25 if soup.find("blockquote") else 0
    if structured_content < 50:
        issues.append({
            "type": "minor",
            "title": "Minimal structured content",
            "description": "Using lists, tables, and quotes improves AI parsing and content relevance.",
        })

    robots_meta = soup.find("meta", attrs={"name": "robots"})
    ai_crawler_friendly = bool(robots_meta is None or "noindex" not in (robots_meta.get("content") or "").lower()) and bool(soup.find("link", rel="canonical"))

    citation_friendly = bool(soup.find(["strong", "em"]) or soup.select("[class*=citation]"))

    topic_clusters = len({heading.get_text(strip=True) for heading in soup.find_all(["h2", "h3"]) if heading.get_text(strip=True)})
    has_topic_clustering = topic_clusters > 3
    if not has_topic_clustering:
        issues.append({
            "type": "minor",
            "title": "Low topic clustering",
            "description": "Add more distinct headings to help AI understand related subtopics.",
        })

    return {
        "content_chunking": content_chunking,
        "conversational_readability": conversational_readability,
        "faq_presence": faq_section,
        "entity_richness": entity_count,
        "ai_snippet_readiness": snippet_readiness,
        "eeat_signals": eeat_signals,
        "structured_content": structured_content,
        "ai_crawler_friendly": ai_crawler_friendly,
        "citation_friendly": citation_friendly,
        "has_topic_clustering": has_topic_clustering,
        "issues": issues,
    }
