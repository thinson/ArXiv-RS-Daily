#!/usr/bin/env python3
"""
将 GitHub 中“日报 YYYYMMDD” issues 同步到仓库 daily_reports 目录：
- daily_reports/YYYYMM/YYYYMMDD.md
- daily_reports/README.md（展示最新一天日报）
"""

import re
from datetime import datetime
from github import Github, Auth
import os

TOKEN = os.getenv("GITHUB_TOKEN", "")
REPO = os.getenv("GITHUB_REPO", "owner/repo")
BASE_DIR = "daily_reports"


def upsert_file(repo, path: str, content: str, message: str):
    data = content.encode("utf-8")
    try:
        old = repo.get_contents(path)
        repo.update_file(path=path, message=message, content=data, sha=old.sha)
        print(f"UPDATED {path}")
    except Exception:
        repo.create_file(path=path, message=message, content=data)
        print(f"CREATED {path}")


def cleanup_legacy_files(repo):
    # 删除 daily_reports 根目录下旧的扁平日报文件（如 20260311.md）
    try:
        entries = repo.get_contents(BASE_DIR)
    except Exception:
        return

    for e in entries:
        if e.type == "file" and re.fullmatch(r"\d{8}\.md", e.name):
            repo.delete_file(
                path=e.path,
                message=f"cleanup legacy daily report file {e.name}",
                sha=e.sha,
            )
            print(f"DELETED {e.path}")



def _require_env():
    required = ["GITHUB_TOKEN", "GITHUB_REPO"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise RuntimeError(f"Missing env: {', '.join(missing)}")

def main():
    _require_env()
    g = Github(auth=Auth.Token(TOKEN))
    repo = g.get_repo(REPO)

    digest_issues = []
    for it in repo.get_issues(state="open"):
        m = re.fullmatch(r"日报\s*(\d{8})", (it.title or "").strip())
        if m:
            digest_issues.append((m.group(1), it))

    if not digest_issues:
        print("NO_DIGEST_ISSUES")
        return

    digest_issues.sort(key=lambda x: x[0])

    for date, issue in digest_issues:
        ym = date[:6]
        path = f"{BASE_DIR}/{ym}/{date}.md"
        body = (issue.body or "").strip() + "\n"
        upsert_file(repo, path, body, f"sync daily report {date}")

    # 根目录 README 仅展示最近三天（最新在前）
    top3 = sorted(digest_issues, key=lambda x: x[0], reverse=True)[:3]
    lines = ["# Daily Reports", "", "最近三天日报（最新在前）：", ""]
    for date, issue in top3:
        ym = date[:6]
        body = (issue.body or "").strip()
        body = re.sub(
            rf"^#\s*日报\s*{date}\s*$",
            f"# [{date}](./{ym}/{date}.md)",
            body,
            count=1,
            flags=re.MULTILINE,
        )
        lines.append(body)
        lines.append("")
        lines.append("---")
        lines.append("")

    readme = "\n".join(lines).rstrip() + "\n"
    upsert_file(repo, f"{BASE_DIR}/README.md", readme, f"update daily_reports README top3")

    cleanup_legacy_files(repo)

    print(f"DONE latest={top3[0][0]}")


if __name__ == "__main__":
    main()
