import logging
from typing import List

from jobspy import scrape_jobs

from models import Job

logger = logging.getLogger(__name__)

# Map config values to JobSpy job_type values
JOB_TYPE_MAP = {
    "full-time": "fulltime",
    "part-time": "parttime",
    "contract": "contract",
    "internship": "internship",
}


def _build_search_queries(keywords: list, skills: list, companies: list) -> list:
    """Build combined search queries from keywords, skills, and companies.

    Instead of searching each term individually, combines them:
      - Each keyword paired with top skills (e.g. "Java developer Spring Boot REST API")
      - Each company paired with primary keyword (e.g. "Google Java developer")
    """
    queries = []
    top_skills = " ".join(skills[:4]) if skills else ""
    primary_keyword = keywords[0] if keywords else ""

    # Keyword + skills combinations
    for kw in keywords:
        if top_skills:
            queries.append(f"{kw} {top_skills}")
        else:
            queries.append(kw)

    # Company + primary keyword combinations
    for company in companies:
        if primary_keyword:
            queries.append(f"{primary_keyword} {company}")
        else:
            queries.append(company)

    # If only skills configured (no keywords or companies), search skills directly
    if not keywords and not companies and skills:
        queries.append(" ".join(skills[:6]))

    return queries


def fetch_jobs(config: dict) -> List[Job]:
    """Fetch jobs from LinkedIn using JobSpy (free, no API key needed)."""
    criteria = config["criteria"]
    keywords = criteria.get("keywords", [])
    skills = criteria.get("skills", [])
    companies = criteria.get("companies", [])

    all_jobs: List[Job] = []

    # Build combined search queries (keyword + skills + company)
    search_queries = _build_search_queries(keywords, skills, companies)
    logger.info(f"Built {len(search_queries)} combined search queries")

    # Scrape params
    location = criteria.get("location", "")
    job_type = JOB_TYPE_MAP.get(criteria.get("job_type", ""), None)
    is_remote = criteria.get("job_type", "") == "remote"
    company_ids = criteria.get("linkedin_company_ids", None)

    for query in search_queries:
        jobs = _scrape_query(query, location, job_type, is_remote, company_ids)
        all_jobs.extend(jobs)

    # Deduplicate by job_id
    seen_ids = set()
    unique_jobs = []
    for job in all_jobs:
        if job.job_id not in seen_ids:
            seen_ids.add(job.job_id)
            unique_jobs.append(job)

    logger.info(f"Fetched {len(unique_jobs)} unique jobs total")
    return unique_jobs


def _scrape_query(
    query: str,
    location: str,
    job_type: str | None,
    is_remote: bool,
    company_ids: list | None,
) -> List[Job]:
    """Run a single JobSpy scrape for a search query."""
    try:
        kwargs = {
            "site_name": ["linkedin"],
            "search_term": query,
            "location": location,
            "results_wanted": 25,
            "hours_old": 24,
            "linkedin_fetch_description": True,
            "verbose": 0,
        }

        if job_type:
            kwargs["job_type"] = job_type
        if is_remote:
            kwargs["is_remote"] = True
        if company_ids:
            kwargs["linkedin_company_ids"] = company_ids

        df = scrape_jobs(**kwargs)

        if df is None or df.empty:
            logger.info(f"No results for query '{query}'")
            return []

        jobs = []
        for _, row in df.iterrows():
            job_url = str(row.get("job_url", ""))
            job_id = str(row.get("id", "")) or job_url

            jobs.append(
                Job(
                    job_id=job_id,
                    title=str(row.get("title", "")),
                    company=str(row.get("company", "")),
                    location=str(row.get("location", "")),
                    url=job_url,
                    description=str(row.get("description", "")),
                    experience_level=str(row.get("job_level", "")),
                    job_type=str(row.get("job_type", "")),
                    posted_date=str(row.get("date_posted", "")),
                )
            )

        logger.info(f"Found {len(jobs)} jobs for query '{query}'")
        return jobs

    except Exception as e:
        logger.error(f"Scrape failed for query '{query}': {e}")
        return []
