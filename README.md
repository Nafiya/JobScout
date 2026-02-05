# 🚀 JobScout

**JobScout** is a fully vibe-coded, Python-based job-fetch agent built for **personal use** to simplify and automate job searching.

It runs entirely using **GitHub Actions**, periodically fetching and filtering job postings based on **custom skills, companies, roles, and locations** — without any UI, backend server, Node.js, or REST APIs.

---

## 🧠 Why JobScout?

Job searching is repetitive and time-consuming. JobScout was built to:

- Automate job discovery
- Reduce manual searching
- Focus only on **relevant roles**
- Stay lightweight and maintenance-free

This project is intentionally simple, opinionated, and optimized for **individual job seekers**.

---

## ⚙️ How It Works

- Written entirely in **Python**
- Runs on a scheduled **GitHub Actions workflow**
- Fetches job postings from configured sources
- Filters jobs based on:
  - Skills
  - Job titles
  - Companies
  - Locations
- Outputs results (logs / files / notifications – depending on implementation)

No servers. No databases. No frontend.

---

## 🧩 Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)

---

## 📁 Project Structure

```text
JobScout/
├── .github/
│   └── workflows/
│       └── jobscout.yml        # GitHub Actions workflow
├── src/
│   ├── fetchers/               # Job source fetch logic
│   ├── filters/                # Skill / company / location filters
│   └── main.py                 # Entry point
├── config/
│   └── config.json             # Skills, companies, locations
├── requirements.txt
└── README.md

---

## 🔁 Running JobScout (GitHub Actions)

JobScout is designed to run automatically using GitHub Actions.

### Default Behavior
- Runs on a schedule (e.g., daily or weekly)
- Executes the Python script
- Fetches and filters jobs based on your config

You **do not** need to run anything locally unless you want to test changes.

---

## 🍴 Fork & Use It Yourself

You can easily fork this project and customize it for your own job search.

### 1️⃣ Fork the Repository
Click **Fork** on GitHub to create your own copy.

---

### 2️⃣ Update Job Preferences
Edit the configuration file:

```json
{
  "skills": ["Java", "Spring Boot", "Angular"],
  "job_titles": ["Senior Software Engineer", "Backend Developer"],
  "companies": ["Google", "Amazon", "Microsoft"],
  "
### 3️⃣ Configure Schedule (Optional)
Edit .github/workflows/jobscout.yml to control how often the job runs:

schedule:
  - cron: "0 8 * * 1-5"

### 4️⃣ Enable GitHub Actions
	•	Push your changes
	•	Go to the Actions tab
	•	Enable workflows if prompted

JobScout will now run automatically.

### 5️⃣ Run Locally (Optional)
For testing or development:

pip install -r requirements.txt
python src/main.py



