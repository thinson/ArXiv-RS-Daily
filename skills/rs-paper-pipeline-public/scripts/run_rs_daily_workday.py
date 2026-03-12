#!/usr/bin/env python3
"""
工作日 09:05 自动执行：
1) 抓取并筛选“当天”遥感xAI论文，生成/更新单篇 issue
2) 生成当天日报 issue
3) 推送日报到 Feishu 私聊
"""

import subprocess
from datetime import datetime
from github import Github, Auth
import os

TOKEN = os.getenv("GITHUB_TOKEN", "")
REPO = os.getenv("GITHUB_REPO", "owner/repo")
FEISHU_TARGET = os.getenv("FEISHU_TARGET", "user:your_open_id")
WORKDIR = "/home/openclaw/.openclaw/workspace"


def run(cmd: list[str]):
    print("$", " ".join(cmd))
    subprocess.run(cmd, cwd=WORKDIR, check=True)


def get_today_digest(date_str: str):
    g = Github(auth=Auth.Token(TOKEN))
    repo = g.get_repo(REPO)
    title = f"日报 {date_str}"
    for issue in repo.get_issues(state="open"):
        if issue.title.strip() == title:
            return issue
    return None



def _require_env():
    required = ["GITHUB_TOKEN", "GITHUB_REPO"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise RuntimeError(f"Missing env: {', '.join(missing)}")

def main():
    _require_env()
    date_str = datetime.now().strftime("%Y%m%d")

    stats_path = f"memory/rs_daily_stats_{date_str}.json"

    # 1) 当天论文筛选+处理
    run(["python3", "scripts/daily_arxiv_cross_filter.py", "--days", "1", "--stats-out", stats_path])

    # 2) 仅生成当天日报（包含筛选统计数字）
    run(["python3", "scripts/daily_digest_llm_upgrade.py", "--date", date_str, "--stats-json", stats_path])

    # 3) 同步日报 markdown 到仓库 daily_reports（按年月归档 + README）
    run(["python3", "scripts/sync_daily_reports_to_repo.py"])

    # 4) 推送到 Feishu
    issue = get_today_digest(date_str)
    if not issue:
        text = f"📭 今日（{date_str}）未生成日报：没有命中当天论文或生成失败。"
    else:
        body = (issue.body or "").strip()
        preview = body[:1200] + ("\n..." if len(body) > 1200 else "")
        text = (
            f"📌 遥感AI日报 {date_str}\n"
            f"Issue: {issue.html_url}\n\n"
            f"{preview}"
        )

    run([
        "openclaw", "message", "send",
        "--channel", "feishu",
        "--target", FEISHU_TARGET,
        "--message", text,
    ])


if __name__ == "__main__":
    main()
