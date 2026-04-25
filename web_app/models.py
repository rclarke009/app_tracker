from pydantic import BaseModel, HttpUrl
from dataclasses import dataclass

@dataclass
class JobInfo:
    created_at: str
    job_text: str
    job_url: str | None = None
    resume_choice: str | None = None
    job_title: str | None = None
    salary: str | None = None
    job_summary: str | None = None

class UserInput(BaseModel):
    """Incoming job log: link + free-form text."""

    job_url: HttpUrl | None = None  # optional if sometimes there's no posting link
    job_text: str
    resume_choice: str | None = None


class JobExtraction(BaseModel):
    """Job summary and info from llm"""

    job_title: str | None = None
    salary: str | None = None
    job_summary: str | None = None