# RS Paper Pipeline (Public, Sanitized)

A publish-ready pipeline for:

1. Fetching daily arXiv candidates (remote sensing related)
2. LLM-based cross filtering (RS × AI/CV/Foundation Models)
3. Generating/updating per-paper GitHub issues
4. Generating daily digest issues
5. Syncing digest markdown to `daily_reports/YYYYMM/YYYYMMDD.md`
6. Pushing daily digest to Feishu

## 0) Prerequisites

- Python 3.10+
- `pip install PyGithub`
- System tools (for PDF/images):
  - `pdftoppm`
  - `pdftotext`
- OpenClaw CLI available if you want Feishu push via `openclaw message send`

## 1) Setup

Copy and edit env file:

```bash
cp .env.example .env
```

Required environment variables:

- `GITHUB_TOKEN=...`
- `GITHUB_REPO=owner/repo`
- `BAILIAN_API_KEY=...`

Optional:

- `LLM_MODEL=MiniMax-M2.5`
- `FEISHU_TARGET=user:your_open_id`

Load env in shell:

```bash
set -a
source .env
set +a
```

## 2) Quick Start (One-shot for today)

```bash
python3 scripts/run_rs_daily_workday.py
```

This runs:

- daily candidate filtering (`--days 1`)
- digest generation for today
- markdown sync to `daily_reports/`
- Feishu message push

## 3) Step-by-step Commands

### A. Filter and process today's papers

```bash
python3 scripts/daily_arxiv_cross_filter.py \
  --days 1 \
  --stats-out memory/rs_daily_stats_$(date +%Y%m%d).json
```

### B. Build digest for a date

```bash
python3 scripts/daily_digest_llm_upgrade.py \
  --date 20260312 \
  --stats-json memory/rs_daily_stats_20260312.json
```

### C. Sync digest markdown to repo

```bash
python3 scripts/sync_daily_reports_to_repo.py
```

## 4) Output Structure

- Per-paper issues in your GitHub repo
- Digest issues titled: `日报 YYYYMMDD`
- Synced files:
  - `daily_reports/YYYYMM/YYYYMMDD.md`
  - `daily_reports/README.md` (latest 3 days, newest first)

## 5) Cron Example (Weekdays 09:05, Asia/Shanghai)

```cron
CRON_TZ=Asia/Shanghai
5 9 * * 1-5 /usr/bin/python3 /path/to/scripts/run_rs_daily_workday.py >> /path/to/logs/rs_daily_workday.log 2>&1
```

## 6) Notes

- This public package is sanitized; no hardcoded secrets.
- If no papers match on a day, digest may be skipped and a notification is sent.
- `paper_processor.py` includes TL;DR generation in the basic info table.
