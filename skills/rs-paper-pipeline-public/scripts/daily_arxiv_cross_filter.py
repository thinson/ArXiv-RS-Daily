#!/usr/bin/env python3
"""
从 arXiv 拉取今天+昨天提交的论文，先按遥感关键词 OR 初筛，
再用 LLM 筛选“遥感 x 基础模型/计算机视觉/人工智能交叉”论文，
最后去重（已存在于 GitHub issues 的 arXiv id）并调用现有流程更新/创建 issue。
"""

import re
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
from github import Github, Auth

from paper_processor import process_paper, call_llm
import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
REPO_NAME = os.getenv("GITHUB_REPO", "owner/repo")
ARXIV_API = "https://export.arxiv.org/api/query"

RS_KEYWORDS = [
    "remote sensing", "satellite image", "satellite imagery", "earth observation",
    "hyperspectral", "multispectral", "synthetic aperture radar", "sar",
    "uav", "geolocalization", "change detection", "land cover",
]


def fetch_recent_candidates(max_results=150, days_back=2):
    query = " OR ".join([f"all:{k}" for k in RS_KEYWORDS])
    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    url = f"{ARXIV_API}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=90) as r:
        xml_text = r.read().decode("utf-8", errors="ignore")

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(xml_text)
    items = []

    today = datetime.now().date()
    valid_days = {today - timedelta(days=i) for i in range(days_back)}

    for e in root.findall("atom:entry", ns):
        aid = (e.find("atom:id", ns).text or "").strip().split("/")[-1]
        title = (e.find("atom:title", ns).text or "").strip().replace("\n", " ")
        abs_text = (e.find("atom:summary", ns).text or "").strip().replace("\n", " ")
        published = (e.find("atom:published", ns).text or "").strip()
        pdate = None
        try:
            pdate = datetime.strptime(published[:10], "%Y-%m-%d").date()
        except Exception:
            pass

        if pdate not in valid_days:
            continue

        text = f"{title} {abs_text}".lower()
        if not any(k in text for k in RS_KEYWORDS):
            continue

        items.append({
            "arxiv_id": aid,
            "title": title,
            "abstract": abs_text,
            "published": published[:10],
        })
    return items


def llm_cross_filter(candidates):
    if not candidates:
        return []

    payload = []
    for i, c in enumerate(candidates, 1):
        payload.append(f"[{i}] id={c['arxiv_id']} | title={c['title']} | abstract={c['abstract'][:500]}")

    prompt = (
        "你是论文筛选助手。请从候选中筛选出同时满足："
        "(1) 与遥感相关；(2) 与基础模型/计算机视觉/人工智能有明确交叉。\n"
        "返回严格 JSON 数组，只包含保留论文的 arxiv_id 字符串，例如: [\"2603.12345\",\"2603.54321\"]。\n\n"
        + "\n".join(payload)
    )
    out = call_llm(prompt, max_tokens=1200, timeout=180).strip()

    try:
        m = re.search(r"\[[\s\S]*\]", out)
        arr = json.loads(m.group(0) if m else out)
        keep = set(x.strip() for x in arr if isinstance(x, str))
        return [c for c in candidates if c["arxiv_id"] in keep]
    except Exception:
        # LLM 解析失败时，保守降级：关键词交叉筛选
        hard_kw = ["foundation model", "pretrain", "vision-language", "cv", "computer vision", "ai", "artificial intelligence", "mamba", "transformer"]
        out_items = []
        for c in candidates:
            t = (c["title"] + " " + c["abstract"]).lower()
            if any(k in t for k in hard_kw):
                out_items.append(c)
        return out_items


def load_existing_arxiv_ids(repo):
    ids = set()
    for issue in repo.get_issues(state="all"):
        body = issue.body or ""
        m = re.search(r"arxiv\.org/abs/([^\)\s]+)", body)
        if m:
            ids.add(m.group(1).strip())
    return ids



def _require_env():
    required = ["GITHUB_TOKEN", "GITHUB_REPO"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise RuntimeError(f"Missing env: {', '.join(missing)}")

def main(dry_run=False, days_back=2, stats_out: str | None = None):
    _require_env()
    g = Github(auth=Auth.Token(GITHUB_TOKEN))
    repo = g.get_repo(REPO_NAME)

    print("[1/5] 拉取今天+昨天候选...")
    cands = fetch_recent_candidates(max_results=180, days_back=days_back)
    cand_count = len(cands)
    print(f"  候选数: {cand_count}")

    print("[2/5] LLM 交叉筛选...")
    selected = llm_cross_filter(cands)
    selected_count = len(selected)
    print(f"  入选数: {selected_count}")

    print("[3/5] 读取 issue 去重...")
    existing = load_existing_arxiv_ids(repo)
    todo = [x for x in selected if x["arxiv_id"] not in existing]
    existing_count = len(selected) - len(todo)
    todo_count = len(todo)
    print(f"  已存在: {existing_count}，待处理: {todo_count}")

    stats = {
        "date": datetime.now().strftime("%Y%m%d"),
        "candidate_count": cand_count,
        "llm_selected_count": selected_count,
        "existing_count": existing_count,
        "todo_count": todo_count,
    }
    if stats_out:
        Path(stats_out).parent.mkdir(parents=True, exist_ok=True)
        Path(stats_out).write_text(json.dumps(stats, ensure_ascii=False), encoding="utf-8")

    if dry_run:
        print("[DRY RUN] 列表如下:")
        for x in todo:
            print(f"  - {x['arxiv_id']} | {x['published']} | {x['title'][:90]}")
        return

    print("[4/5] 提交 issue（不重复）...")
    for x in todo:
        aid = x["arxiv_id"]
        print(f"  -> 处理 {aid}")
        # 未指定 issue_number 时，process_paper 会按标题匹配更新；匹配不到则失败（当前 Phase1 策略）
        process_paper(aid, issue_number=None)

    print("[5/5] 完成")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--days", type=int, default=2)
    parser.add_argument("--stats-out", dest="stats_out", help="输出统计 JSON 文件路径")
    args = parser.parse_args()

    main(dry_run=args.dry_run, days_back=args.days, stats_out=args.stats_out)
