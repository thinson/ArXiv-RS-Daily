---
name: rs-paper-pipeline-public
description: Publish-ready RS paper pipeline (sanitized). Use when setting up or demonstrating the remote-sensing arXiv→GitHub issue→daily digest workflow without exposing secrets. Includes secure scripts that require environment variables for GitHub, LLM, and Feishu targets.
---

Use bundled scripts in `scripts/` to run the full workflow with env-based credentials.

## Required Environment Variables

- `GITHUB_TOKEN`
- `GITHUB_REPO` (format: `owner/repo`)
- `BAILIAN_API_KEY` (for LLM calls in paper processing)
- `FEISHU_TARGET` (optional for push script; default placeholder)
- `LLM_MODEL` (optional)

## Workflow

1. Process new daily papers:
   - `python3 scripts/daily_arxiv_cross_filter.py --days 1 --stats-out memory/rs_daily_stats_YYYYMMDD.json`
2. Build digest for target date:
   - `python3 scripts/daily_digest_llm_upgrade.py --date YYYYMMDD --stats-json memory/rs_daily_stats_YYYYMMDD.json`
3. Sync digest markdown to repo:
   - `python3 scripts/sync_daily_reports_to_repo.py`
4. Full scheduled run:
   - `python3 scripts/run_rs_daily_workday.py`

## Notes

- All secrets are removed from code.
- Daily report files are archived by month in `daily_reports/YYYYMM/YYYYMMDD.md`.
- `daily_reports/README.md` shows latest 3 days (newest first).
