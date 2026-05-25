from typing import Any


def calculate_seo_score(seo_data: dict[str, Any]) -> int:
    score = 0

    if seo_data.get("has_title"):
        title_len = seo_data.get("title_length", 0)
        score += 15 if 30 <= title_len <= 60 else 10

    if seo_data.get("has_meta_description"):
        meta_len = seo_data.get("meta_description_length", 0)
        score += 15 if 120 <= meta_len <= 160 else 10

    h1_count = seo_data.get("h1_count", 0)
    score += 15 if h1_count == 1 else 8 if h1_count > 0 else 0

    score += min(10, seo_data.get("h2_count", 0) * 2)

    total_images = seo_data.get("total_images", 0)
    alt_issues = seo_data.get("image_alt_issues", 0)
    score += 10 if total_images == 0 else max(0, int((total_images - alt_issues) / total_images * 10))

    if seo_data.get("has_canonical"):
        score += 10
    if seo_data.get("has_og_tags"):
        score += 10
    if seo_data.get("has_schema"):
        score += 10

    word_count = seo_data.get("word_count", 0)
    score += 5 if word_count >= 300 else 3 if word_count >= 150 else 0

    return min(100, round(score))


def calculate_geo_score(geo_data: dict[str, Any]) -> int:
    score = 0
    score += geo_data.get("content_chunking", 0) * 0.25
    score += 15 if geo_data.get("conversational_readability") else 0
    score += 15 if geo_data.get("faq_presence") else 0
    score += min(15, geo_data.get("entity_richness", 0) / 20 * 15)
    score += geo_data.get("ai_snippet_readiness", 0) * 0.20
    score += min(10, geo_data.get("eeat_signals", 0) / 6 * 10)
    score += geo_data.get("structured_content", 0) * 0.10
    score += 5 if geo_data.get("ai_crawler_friendly") else 0
    score += 5 if geo_data.get("citation_friendly") else 0
    score += 5 if geo_data.get("has_topic_clustering") else 0
    return min(100, round(score))


def calculate_technical_score(seo_data: dict[str, Any], load_time_ms: int | None) -> int:
    score = 100
    if load_time_ms and load_time_ms > 3000:
        score -= min(20, (load_time_ms - 3000) / 500)
    if not seo_data.get("has_title"):
        score -= 15
    if not seo_data.get("has_meta_description"):
        score -= 10
    if not seo_data.get("has_canonical"):
        score -= 5
    alt_issues = seo_data.get("image_alt_issues", 0)
    score -= min(10, alt_issues * 2)
    return max(0, min(100, round(score)))


def calculate_ai_visibility_score(geo_data: dict[str, Any], seo_data: dict[str, Any]) -> int:
    score = 0
    score += geo_data.get("ai_snippet_readiness", 0) * 0.30
    score += geo_data.get("content_chunking", 0) * 0.25
    score += min(20, geo_data.get("entity_richness", 0) / 25 * 20)
    score += min(15, geo_data.get("eeat_signals", 0) / 8 * 15)
    score += 10 if seo_data.get("has_schema") else 0
    return min(100, round(score))
