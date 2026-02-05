# JobScout

**JobScout** is a Python-based job-fetch agent built for **personal use** to automate job searching on LinkedIn.

It scrapes LinkedIn job listings, scores them against your **skills, keywords, and target companies**, and sends email notifications for matching jobs. Runs locally or on **GitHub Actions** for free.

---

## Why JobScout?

Job searching is repetitive and time-consuming. JobScout was built to:

- Automate job discovery on LinkedIn
- Score jobs against your actual skill set
- Send email alerts only for high-match roles
- Run 24/7 for free via GitHub Actions

---

## How It Works

```
LinkedIn ──scrape──> Score by Skills ──match──> Email Notification
              |              |                        |
         JobSpy lib    Weighted 0-100%          Gmail SMTP
                      (skills = 80%)
```

1. **Scrape** — Fetches jobs from LinkedIn using combined keyword + skill + company search queries
2. **Score** — Matches each job against your configured skills (80%), keywords (10%), location (5%), job type (5%)
3. **Deduplicate** — Tracks notified jobs in SQLite so you never get the same job twice
4. **Notify** — Sends an HTML email with job title, company, location, score, and LinkedIn link

---

## Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)
![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)

---

## Project Structure

```text
JobScout/
├── .github/
│   └── workflows/
│       └── job-agent.yml     # GitHub Actions cron workflow
├── main.py                   # Entry point (continuous or single-run mode)
├── scraper.py                # LinkedIn scraping via JobSpy
├── matcher.py                # Skills-weighted scoring engine
├── notifier.py               # Email and WhatsApp notifications
├── storage.py                # SQLite job deduplication
├── models.py                 # Job dataclass
├── config.yaml               # Search criteria and settings
├── requirements.txt          # Python dependencies
├── .env.example              # Credential template
└── README.md
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure credentials

```bash
cp .env.example .env
```

Edit `.env` with your Gmail credentials:

```env
SMTP_SENDER_EMAIL=your@gmail.com
SMTP_SENDER_PASSWORD=your-gmail-app-password
SMTP_RECIPIENT_EMAIL=your@gmail.com
```

**Gmail App Password setup:**
- Enable 2-Step Verification at https://myaccount.google.com/security
- Generate an App Password at https://myaccount.google.com/apppasswords
- Use the 16-character password as `SMTP_SENDER_PASSWORD`

### 3. Customize your search

Edit `config.yaml`:

```yaml
criteria:
  keywords:
    - "Java developer"
    - "backend engineer"
  skills:
    - "Java"
    - "Spring Boot"
    - "Docker"
    - "AWS"
  companies:
    - "Google"
    - "Microsoft"
  location: "Toronto"
  experience_level: "mid-senior"
  job_type: "full-time"

match_threshold: 70
```

### 4. Run

```bash
# Continuous mode (checks every 5 minutes)
python main.py

# Single run (for cron / CI)
python main.py --once
```

---

## Scoring

Jobs are scored 0-100% using weighted criteria:

| Factor | Weight | Description |
|--------|--------|-------------|
| **Skills** | 80% | How many of your listed skills appear in the job description. Matching ~1/3 of listed skills gives full score |
| **Keywords** | 10% | Job title/description matches against keyword list |
| **Location** | 5% | Job location contains target city |
| **Job meta** | 5% | Experience level and job type match |

Only jobs scoring above `match_threshold` trigger notifications.

---

## Deploy to GitHub Actions (Free)

Run JobScout automatically without keeping your machine on.

### 1. Push to GitHub

```bash
git init && git add -A && git commit -m "Initial commit"
gh repo create job-fetch-agent --private --push --source .
```

### 2. Add secrets

Go to **Settings > Secrets and variables > Actions** and add:

| Secret | Value |
|--------|-------|
| `SMTP_SENDER_EMAIL` | Your Gmail address |
| `SMTP_SENDER_PASSWORD` | Your Gmail App Password |
| `SMTP_RECIPIENT_EMAIL` | Recipient email address |

### 3. Enable and run

- Go to the **Actions** tab
- Select **Job Fetch Agent** workflow
- Click **Run workflow** to test manually

The workflow will also run automatically on the cron schedule configured in `.github/workflows/job-agent.yml`.

---

## Optional: WhatsApp Notifications

WhatsApp notifications use the Meta WhatsApp Cloud API (free: 1,000 conversations/month).

1. Create a free app at https://developers.facebook.com
2. Add the WhatsApp product and get your access token + phone number ID
3. Add to `.env`:
   ```env
   WHATSAPP_API_TOKEN=EAAxxxxxxx...
   WHATSAPP_PHONE_NUMBER_ID=123456789012345
   WHATSAPP_RECIPIENT_PHONE=919876543210
   ```
4. Set `whatsapp: enabled: true` in `config.yaml`

---

## Fork & Use It Yourself

1. **Fork** this repository
2. Update `config.yaml` with your skills, keywords, companies, and location
3. Add your Gmail credentials as GitHub Secrets
4. Enable GitHub Actions — JobScout runs automatically

---

## License

MIT
