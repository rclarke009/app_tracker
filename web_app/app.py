import gunicorn
from datetime import datetime
import logging
import os
import json

import requests
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel, ValidationError
from fastapi import HTTPException

from jobapp_tracker.web_app.models import JobInfo, UserInput, JobExtraction
from jobapp_tracker.db import add_job, get_jobs

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI()

load_dotenv()


EXTRACTION_SYSTEM = """You extract structured fields from job postings.
Return ONLY valid JSON (no markdown, no prose) with exactly these keys:
- "job_title": string or null if not clearly stated
- "salary": string or null — copy compensation EXACTLY as written in the posting (range, hourly, etc.). If absent, null. Do not invent numbers.
- "job_summary": string — concise summary of the role. If the posting separates required vs nice-to-have qualifications, use two short labeled parts (e.g. "Required: ..." and "Nice to have: ..."). If it does not separate them, write one coherent summary; do not invent sections.
Base everything ONLY on the user's text."""



def extract_job_fields(job_text: str) -> JobExtraction:
    api_key = os.environ.get("OPENAI_API_KEY")  # example
    if not api_key:
        logger.error("OPENAI_API_KEY is not set")
        raise HTTPException(
            status_code=503,
            detail="Extraction is not configured on this server",
        )

    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "gpt-4o-mini",
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": EXTRACTION_SYSTEM},
                    {
                        "role": "user",
                        "content": f"Job posting text:\n\n{job_text}",
                    },
                ],
            },
            timeout=120,
        )
        r.raise_for_status()

    except requests.Timeout:
        logger.exception("OpenAI request timed out")
        raise HTTPException(
            status_code=503,
            detail="Extraction service timed out; try again later",
        )
    except requests.RequestException:
        logger.exception("OpenAI request failed")
        raise HTTPException(
            status_code=502,
            detail="Extraction service returned an error",
        )

    raw = r.json()["choices"][0]["message"]["content"].strip()
    try:
        return JobExtraction.model_validate_json(raw)
    except ValidationError as e:
        # Fallback: try plain json.loads then validate (if model wraps oddly)
        return JobExtraction.model_validate(json.loads(raw))


@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/log-job")
def log_job(body: UserInput):
    if not (body.job_text or "").strip():
        raise HTTPException(
            status_code=400,
            detail="job_text cannot be empty",
        )

    extraction_data = extract_job_fields(body.job_text)
    summary = extraction_data.job_summary
    salary = extraction_data.salary
    title = extraction_data.job_title

    url_str = str(body.job_url) if body.job_url else ""
    resume = str(body.resume_choice) if body.resume_choice else ""

    job_to_add = JobInfo(
        datetime.now().isoformat(), 
        body.job_text,
        url_str, 
        resume, 
        title, 
        salary,
        summary
    )
    add_job(job_to_add)
    return {"summary": summary, "ok": True}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
