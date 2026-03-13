<div align="center">
  <img src="./docs/logo-220.png" alt="RS-PaperClaw Logo" width="120" />

# RS-PaperClaw🦞

### Automated Remote-Sensing Paper Tracking & Analysis Pipeline

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](#)
[![Status](https://img.shields.io/badge/Status-Active-2EA043)](#)
[![Workflow](https://img.shields.io/badge/Workflow-arXiv%20%E2%86%92%20Issue%20%E2%86%92%20Digest-8A2BE2)](#)
[![Pages](https://img.shields.io/badge/GitHub%20Pages-Live-b55f34)](https://thinson.github.io/RS-PaperClaw/)

**arXiv → Per-paper Issue Report → Daily Digest → Visual Reading Portal**

中文版本：**[README.md](./README.md)**

</div>

---

## 🌐 Live Portal

- GitHub Pages: **https://thinson.github.io/RS-PaperClaw/**
- Digest archive: **[daily_reports/](./daily_reports/README.md)**

## 🖼️ UI Preview

> Images are lightly compressed for faster loading while keeping readability.

### Desktop

![RS-PaperClaw Desktop UI](./docs/screenshots/ui-desktop.jpg)

### Mobile

<img src="./docs/screenshots/ui-mobile.jpg" alt="RS-PaperClaw Mobile UI" width="360" />

---

## ✨ What this project does

RS-PaperClaw automates the daily pipeline:

- 🔎 Fetch arXiv candidates (remote-sensing related)
- 🧠 Run keyword + LLM cross filtering
- 📝 Generate / update per-paper reading reports (GitHub Issues)
- 🗞️ Generate daily digest issues
- 🗂️ Sync digest markdown to `daily_reports/YYYYMM/YYYYMMDD.md`
- 📮 Deliver summaries to Feishu

---

## 🎯 Why issue-centric

- 🧭 **Traceable**: one paper, one issue; full history is preserved
- 🤝 **Collaborative**: comments become discussion and knowledge capture
- ⚙️ **Automation-friendly**: stable targets for incremental updates
- 🗂️ **Closed loop**: dynamic issue workflow + static markdown archive

---

## 🧩 Core capabilities

| Module | Output |
|---|---|
| Per-paper report | metadata, TL;DR, Chinese abstract, tags, first-3-page previews, 10-question analysis |
| Daily digest | numeric overview, highlights, article list, observations |
| Quality control | filters placeholders and incomplete structures |
| Archive | issue + markdown dual-track sync |
| Web portal | recent digest browser, mobile cards, issue deep-dive overlay |

---

## 🗺️ Repository layout (main)

```text
RS-PaperClaw/
├── docs/                             # GitHub Pages static site
│   ├── index.html
│   └── logo-220.png
├── daily_reports/                    # digest archive by month
│   ├── README.md
│   └── YYYYMM/YYYYMMDD.md
├── papers/previews/                  # preview images for issue display
├── skills/rs-paper-pipeline/         # skill and scripts
│   ├── README.md
│   ├── SKILL.md
│   └── scripts/
└── README.md
```

---

## 🚀 Quick start

### 1) Requirements

- Python 3.10+
- `pip install PyGithub`
- `poppler-utils` (`pdftoppm`, `pdftotext`)

### 2) Environment variables

```bash
export GITHUB_TOKEN="..."
export GITHUB_REPO="owner/repo"
export BAILIAN_API_KEY="..."
# optional
export FEISHU_TARGET="user:xxx"
export LLM_MODEL="MiniMax-M2.5"
```

### 3) Run today's workflow

```bash
python3 skills/rs-paper-pipeline/scripts/run_rs_daily_workday.py
```

---

## ⏰ Scheduler example

```cron
CRON_TZ=Asia/Shanghai
5 9 * * 1-5 /usr/bin/python3 /path/to/skills/rs-paper-pipeline/scripts/run_rs_daily_workday.py >> /path/to/logs/rs_daily_workday.log 2>&1
```

---

## 📎 Notes

- Chinese README is the default entry: [README.md](./README.md)
- GitHub Pages deployment source: `main` branch + `/docs`

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=thinson/RS-PaperClaw&type=Date)](https://star-history.com/#thinson/RS-PaperClaw&Date)
