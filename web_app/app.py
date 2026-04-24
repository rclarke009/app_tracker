import gunicorn
import requests
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
import os
from datetime import datetime


app = FastAPI()

class JobNoteIn(BaseModel):
    """What the user submits (e.g. paste job ad text, or free-form note)."""
    text: str

def call_llm(user_text: str) -> str:
    """Replace with your provider (OpenAI, Anthropic, local Ollama, etc.)."""
    api_key = os.environ.get("OPENAI_API_KEY")  # example
    if not api_key:
        return "[configure OPENAI_API_KEY]"
    # Example: OpenAI chat completions — adjust model/URL for your stack
    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "Summarize the job in one line for a tracker row."},
                {"role": "user", "content": user_text},
            ],
        },
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"].strip()



@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/log-job")
def log_job(body: JobNoteIn):
    summary = call_llm(body.text)
    # sheet = get_sheet()
    # sheet.append_row([datetime.utcnow().isoformat(), body.text[:200], summary])
    return {"summary": summary, "ok": True}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
