# SEO Analyzer Python

A Python recreation of the SEO + GEO Optimization Analyzer project. This version uses FastAPI for the backend and includes richer analysis details for SEO, AI visibility, and technical site signals.

## Features

- URL validation and normalization
- HTML fetching with page metadata extraction
- SEO analysis of title, description, headings, canonical tags, Open Graph, image alt text, structured data, and more
- GEO/AI visibility analysis for content chunking, conversational readability, FAQ sections, entity richness, snippet readiness, E-E-A-T, and topic clustering
- Robots.txt, llms.txt, and sitemap.xml detection
- Scoring system for SEO, GEO, technical, and AI visibility performance
- Optional OpenAI integration for generating a summary when `OPENAI_API_KEY` is provided
- **Interactive web frontend** with real-time analysis and visual score displays

## Getting Started

1. Create a virtual environment:

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows
```

2. Install dependencies:

```bash
pip install -e .
```

3. Copy `.env.example` to `.env` and set `OPENAI_API_KEY` if desired.

4. Run the server:

```bash
uvicorn app:app --reload
```

5. Open your browser and go to `http://127.0.0.1:8000` for the interactive frontend!

## Usage

### Web Interface
Visit `http://127.0.0.1:8000` in your browser for the full interactive experience with:
- URL input form
- Real-time analysis with loading indicators
- Visual score cards with progress bars
- Detailed issues list with severity indicators
- Page information display
- AI-powered summaries (if API key configured)

### API Usage
Use the REST API directly:

```bash
curl -X POST "http://127.0.0.1:8000/analyze" -H "Content-Type: application/json" -d '{"url": "https://example.com"}'
```

Or visit `http://127.0.0.1:8000/docs` for interactive API documentation.

