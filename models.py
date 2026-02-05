from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Job:
    job_id: str
    title: str
    company: str
    location: str
    url: str
    description: str = ""
    experience_level: str = ""
    job_type: str = ""
    posted_date: str = ""
