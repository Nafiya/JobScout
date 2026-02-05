import logging
import os
import sys
import time

import schedule
import yaml
from dotenv import load_dotenv

from matcher import filter_matching_jobs
from notifier import notify_all
from scraper import fetch_jobs
from storage import cleanup_old, get_connection, is_seen, mark_seen

# ── Setup ────────────────────────────────────────────────────────────────────

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("agent.log"),
    ],
)
logger = logging.getLogger("job-agent")


def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


# ── Pipeline ─────────────────────────────────────────────────────────────────

def run_pipeline(config: dict):
    """Single run of the job-fetch pipeline."""
    logger.info("=" * 60)
    logger.info("Starting job fetch cycle")

    # 1. Fetch jobs from LinkedIn
    jobs = fetch_jobs(config)
    if not jobs:
        logger.info("No jobs fetched this cycle")
        return

    # 2. Score and filter
    matches = filter_matching_jobs(jobs, config)
    if not matches:
        logger.info("No jobs matched the threshold this cycle")
        return

    # 3. Filter out already-seen jobs
    conn = get_connection()
    new_matches = [(job, score) for job, score in matches if not is_seen(conn, job.job_id)]

    if not new_matches:
        logger.info("All matched jobs were already notified previously")
        conn.close()
        return

    logger.info(f"{len(new_matches)} new matching job(s) to notify about")

    # 4. Send notifications
    notify_all(new_matches, config)

    # 5. Mark as seen
    for job, score in new_matches:
        mark_seen(conn, job.job_id, job.title, job.company, job.url, score)

    # 6. Periodic cleanup
    cleanup_old(conn)
    conn.close()

    logger.info("Cycle complete")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    config = load_config()

    logger.info("LinkedIn Job Fetch Agent started")
    logger.info(f"Keywords: {config['criteria'].get('keywords', [])}")
    logger.info(f"Skills: {len(config['criteria'].get('skills', []))} configured")
    logger.info(f"Companies: {config['criteria'].get('companies', [])}")
    logger.info(f"Match threshold: {config.get('match_threshold', 90)}%")

    # Single-run mode (for GitHub Actions / cron deployments)
    if "--once" in sys.argv:
        logger.info("Running in single-run mode")
        run_pipeline(config)
        return

    # Continuous mode (for local development)
    interval = config.get("schedule", {}).get("interval_minutes", 5)
    logger.info(f"Checking every {interval} minute(s)")

    run_pipeline(config)

    schedule.every(interval).minutes.do(run_pipeline, config=config)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Agent stopped by user")


if __name__ == "__main__":
    main()
