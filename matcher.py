import logging
from typing import List, Tuple

from models import Job

logger = logging.getLogger(__name__)

# Scoring weights (must sum to 100)
WEIGHT_SKILLS = 80
WEIGHT_KEYWORDS = 10
WEIGHT_LOCATION = 5
WEIGHT_JOB_META = 5  # experience level + job type


def score_job(job: Job, config: dict) -> float:
    """
    Score a job against configured criteria.
    Returns a percentage (0-100).

    Breakdown:
      - Skills match:       80%  (skills found in title or description)
      - Keywords match:     10%  (keyword found in title or description)
      - Location match:      5%  (location contains target location)
      - Job type/exp match:  5%  (experience level or job type match)
    """
    criteria = config["criteria"]
    score = 0.0

    # --- Skills scoring (80%) — dominant factor ---
    skills = criteria.get("skills", [])
    if skills:
        searchable = f"{job.title} {job.description}".lower()
        matched = sum(1 for skill in skills if skill.lower() in searchable)
        # Expect ~1/3 of listed skills to match (min 3) for full score,
        # since the skills list is broad and no single job needs all of them.
        expected = max(3, len(skills) // 3)
        ratio = min(1.0, matched / expected)
        score += ratio * WEIGHT_SKILLS
    else:
        score += WEIGHT_SKILLS  # no skills configured = full score

    # --- Keyword scoring (10%) ---
    keywords = criteria.get("keywords", [])
    if keywords:
        searchable = f"{job.title} {job.description}".lower()
        matched = sum(1 for kw in keywords if kw.lower() in searchable)
        score += (matched / len(keywords)) * WEIGHT_KEYWORDS
    else:
        score += WEIGHT_KEYWORDS  # no keywords configured = full score

    # --- Location scoring (5%) ---
    target_location = criteria.get("location", "")
    if target_location:
        if target_location.lower() in job.location.lower():
            score += WEIGHT_LOCATION
    else:
        score += WEIGHT_LOCATION  # no location configured = full score

    # --- Job type / experience level scoring (5%) ---
    meta_score = 0.0
    target_exp = criteria.get("experience_level", "")
    target_type = criteria.get("job_type", "")
    meta_parts = 0

    if target_exp:
        meta_parts += 1
        if target_exp.lower() in job.experience_level.lower() or target_exp.lower() in job.description.lower():
            meta_score += 1
    if target_type:
        meta_parts += 1
        if target_type.lower() in job.job_type.lower() or target_type.lower() in job.description.lower():
            meta_score += 1

    if meta_parts > 0:
        score += (meta_score / meta_parts) * WEIGHT_JOB_META
    else:
        score += WEIGHT_JOB_META  # nothing configured = full score

    return round(score, 2)


def filter_matching_jobs(jobs: List[Job], config: dict) -> List[Tuple[Job, float]]:
    """Return jobs that meet or exceed the match threshold, with their scores."""
    threshold = config.get("match_threshold", 90)
    matches = []

    for job in jobs:
        s = score_job(job, config)
        logger.debug(f"Job '{job.title}' at '{job.company}' scored {s:.1f}%")
        if s >= threshold:
            matches.append((job, s))
            logger.info(f"MATCH: '{job.title}' at '{job.company}' — {s:.1f}%")

    logger.info(f"{len(matches)} jobs matched out of {len(jobs)} (threshold: {threshold}%)")
    return matches
