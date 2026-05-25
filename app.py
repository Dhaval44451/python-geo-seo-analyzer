import os
from datetime import datetime
from typing import Any

import openai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from analyzers.geo import analyze_geo
from analyzers.scoring import (
    calculate_ai_visibility_score,
    calculate_geo_score,
    calculate_seo_score,
    calculate_technical_score,
)
from analyzers.seo import analyze_seo
from utils.crawler import fetch_page, fetch_text_file
from utils.url_validator import get_base_url, is_valid_url, normalize_url

load_dotenv = None

try:
    from dotenv import load_dotenv as _load_dotenv
    load_dotenv = _load_dotenv
except ImportError:
    pass

if load_dotenv:
    load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI(
    title="SEO Analyzer Python",
    description="Python API for SEO / GEO analysis with optional AI summary generation.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html", media_type="text/html")

@app.get("/app")
async def serve_frontend():
    return FileResponse("static/index.html", media_type="text/html")


class AnalyzeRequest(BaseModel):
    url: str


class AnalyzeResponse(BaseModel):
    url: str
    normalized_url: str
    analyze_date: str
    title: str | None
    description: str | None
    load_time_ms: int
    scores: dict
    seo_analysis: dict
    geo_analysis: dict
    issues: list
    ai_summary: str | None


def generate_ai_summary(data: dict) -> str:
    if not OPENAI_API_KEY:
        return "OpenAI API key not configured. Set OPENAI_API_KEY to enable AI summaries."

    openai.api_key = OPENAI_API_KEY
    prompt = (
        f"Analyze the website at {data['normalized_url']} and provide a brief executive summary of its overall SEO and AI visibility performance. "
        f"SEO score: {data['scores']['seo']}/100. GEO score: {data['scores']['geo']}/100. "
        f"Technical score: {data['scores']['technical']}/100. AI visibility score: {data['scores']['ai_visibility']}/100. "
        f"Highlight the top 3 improvement areas in 3 sentences."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=180,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        return f"AI summary generation failed: {exc}"


@app.get("/")
async def root():
    return {
        "message": "SEO Analyzer Python API",
        "version": "0.1.0",
        "endpoints": {
            "analyze": "/analyze (POST) - Analyze a website for SEO and GEO",
        },
        "docs": "/docs - Interactive API documentation",
    }


@app.post("/analyze", response_model=AnalyzeResponse)

async def analyze(request: AnalyzeRequest) -> Any:
    url = request.url.strip()

    if not url or not is_valid_url(url):
        raise HTTPException(status_code=400, detail="Invalid URL provided")

    normalized_url = normalize_url(url)
    base_url = get_base_url(normalized_url)

    try:
        page_data = await fetch_page(normalized_url)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to fetch website: {exc}")

    async def fetch_file(path: str) -> dict:
        return await fetch_text_file(f"{base_url}/{path}")

    robots_result, llms_result, sitemap_result = await fetch_file("robots.txt"), await fetch_file("llms.txt"), await fetch_file("sitemap.xml")

    seo_analysis = analyze_seo(page_data["html"], base_url=base_url)
    seo_analysis.update(
        {
            "robots_txt_accessible": robots_result["success"],
            "robots_txt_content": robots_result.get("content", ""),
            "llms_txt_accessible": llms_result["success"],
            "llms_txt_content": llms_result.get("content", ""),
            "sitemap_accessible": sitemap_result["success"],
            "sitemap_content": sitemap_result.get("content", ""),
        }
    )

    if not robots_result["success"]:
        seo_analysis["issues"].append(
            {
                "type": "medium",
                "title": "robots.txt missing or not reachable",
                "description": "The site does not expose a reachable robots.txt file at the root, which can affect crawler directives.",
            }
        )

    if not llms_result["success"]:
        seo_analysis["issues"].append(
            {
                "type": "medium",
                "title": "llms.txt missing or not reachable",
                "description": "The site does not expose a reachable llms.txt file, which can help AI systems discover policies and metadata.",
            }
        )

    if not sitemap_result["success"]:
        seo_analysis["issues"].append(
            {
                "type": "medium",
                "title": "sitemap.xml missing or not reachable",
                "description": "A sitemap helps search engines and AI discover pages more efficiently.",
            }
        )

    geo_analysis = analyze_geo(page_data["html"], seo_analysis)

    seo_score = calculate_seo_score(seo_analysis)
    geo_score = calculate_geo_score(geo_analysis)
    technical_score = calculate_technical_score(seo_analysis, page_data["load_time_ms"])
    ai_visibility_score = calculate_ai_visibility_score(geo_analysis, seo_analysis)

    all_issues = sorted(
        seo_analysis["issues"] + geo_analysis["issues"],
        key=lambda issue: {"critical": 0, "medium": 1, "minor": 2}.get(issue["type"], 3),
    )

    analysis_result = {
        "url": url,
        "normalized_url": normalized_url,
        "analyze_date": datetime.utcnow().isoformat() + "Z",
        "title": page_data.get("title"),
        "description": page_data.get("description"),
        "load_time_ms": page_data.get("load_time_ms", 0),
        "scores": {
            "seo": seo_score,
            "geo": geo_score,
            "technical": technical_score,
            "ai_visibility": ai_visibility_score,
        },
        "seo_analysis": seo_analysis,
        "geo_analysis": geo_analysis,
        "issues": all_issues,
        "ai_summary": generate_ai_summary(
            {
                "normalized_url": normalized_url,
                "scores": {
                    "seo": seo_score,
                    "geo": geo_score,
                    "technical": technical_score,
                    "ai_visibility": ai_visibility_score,
                },
            }
        ),
    }

    return analysis_result
