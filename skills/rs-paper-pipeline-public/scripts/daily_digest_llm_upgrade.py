#!/usr/bin/env python3
import re
import json
from collections import defaultdict
from pathlib import Path
from github import Github, Auth
from paper_processor import call_llm
import os

TOKEN = os.getenv("GITHUB_TOKEN", "")
REPO = os.getenv("GITHUB_REPO", "owner/repo")


def extract_author(body: str) -> str:
    m = re.search(r"\| \*\*作者\*\* \|([^|]+)\|", body or "")
    return m.group(1).strip() if m else "-"


def extract_report_title(issue: dict) -> str:
    body = issue.get("body") or ""
    # 从报告首行提取完整标题：# [YYYYMMDD] Full Title
    m = re.search(r"^#\s*\[(\d{8})\]\s+(.+)$", body, re.MULTILINE)
    if m:
        return f"[{m.group(1)}] {m.group(2).strip()}"
    return issue.get("title") or ""


def extract_paper_date(issue: dict) -> str | None:
    # 1) 优先使用纯日期 label（如 20260309）
    for l in issue.get("labels", []):
        name = l.get("name", "") if isinstance(l, dict) else ""
        if re.fullmatch(r"\d{8}", name):
            return name

    # 2) 其次从正文标题中提取（如 # [20260309] ...）
    body = issue.get("body") or ""
    bm = re.search(r"\[(\d{8})\]", body)
    if bm:
        return bm.group(1)

    # 3) 最后回退到 issue 标题前缀
    tm = re.match(r"^\[(\d{8})\]\s+", issue.get("title") or "")
    return tm.group(1) if tm else None


def build_digest_with_llm(date: str, papers: list, stats: dict | None = None) -> str:
    items = []
    for i, p in enumerate(papers, 1):
        labels = [l["name"] for l in p.get("labels", []) if l["name"] not in [date, "日报"]]
        items.append({
            "idx": i,
            "issue": p["number"],
            "title": extract_report_title(p),
            "authors": extract_author(p.get("body") or ""),
            "labels": labels,
            "url": p["html_url"],
        })

    prompt = (
        "你是遥感AI日报编辑。请基于给定论文列表输出严格JSON：\n"
        "{\n"
        "  \"overview\": \"120-180字，概述今日研究趋势\",\n"
        "  \"highlights\": [\"3条，每条20-40字\"],\n"
        "  \"one_liners\": [{\"idx\":1,\"summary\":\"每篇一句话，25-45字\"}],\n"
        "  \"observations\": [\"2条，偏分析判断，每条24-48字\"]\n"
        "}\n"
        "要求：中文、客观、不要编造细节。\n\n"
        f"日期: {date}\n候选: {json.dumps(items, ensure_ascii=False)}"
    )
    out = call_llm(prompt, max_tokens=1800, timeout=240)
    m = re.search(r"\{[\s\S]*\}", out)
    data = {"overview": "", "highlights": [], "one_liners": []}
    if m:
        try:
            data = json.loads(m.group(0))
        except Exception:
            pass

    one_map = {x.get("idx"): x.get("summary", "") for x in data.get("one_liners", []) if isinstance(x, dict)}

    overview_text = data.get("overview") or "今日论文总体呈现出遥感与AI交叉深化趋势。"
    if stats:
        overview_text = (
            f"今日共检索候选论文 {stats.get('candidate_count', 0)} 篇；"
            f"关键词+LLM 智能匹配遥感交叉论文 {stats.get('llm_selected_count', 0)} 篇；"
            f"最终纳入日报 {len(items)} 篇。\n\n" + overview_text
        )

    lines = [f"# 日报 {date}", "", "## 📌 今日概况", "", overview_text, ""]

    hs = data.get("highlights") or []
    if hs:
        lines += ["## ✨ 今日亮点", ""]
        for h in hs[:3]:
            lines.append(f"- {h}")
        lines.append("")

    lines += ["## 🗂 今日文章列表", "", "| 标题 | 作者 | 一句话概括 | Issue |", "|---|---|---|---|"]
    for i, p in enumerate(items, 1):
        summary = one_map.get(i) or f"聚焦{('、'.join(p['labels'][:2]) if p['labels'] else '遥感AI方法')}，给出可复现的模型与评测方案。"
        lines.append(f"| {p['title']} | {p['authors']} | {summary} | [#{p['issue']}]({p['url']}) |")

    obs = data.get("observations") or [
        "基础模型与遥感任务结合持续增强，评测与推理能力成为关键。",
        "多数工作关注算法有效性与泛化，而非硬件实现。",
    ]
    lines += ["", "## 🔎 观察", ""]
    for o in obs[:2]:
        lines.append(f"- {o}")

    lines += ["", "---", "", "Powered by OpenClaw🦞"]
    return "\n".join(lines)



def _require_env():
    required = ["GITHUB_TOKEN", "GITHUB_REPO"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise RuntimeError(f"Missing env: {', '.join(missing)}")

def main(target_date: str | None = None, stats_json: str | None = None):
    _require_env()
    g = Github(auth=Auth.Token(TOKEN))
    repo = g.get_repo(REPO)

    stats_map = {}
    if stats_json:
        try:
            obj = json.loads(Path(stats_json).read_text(encoding="utf-8"))
            if isinstance(obj, dict) and obj.get("date"):
                stats_map[obj["date"]] = obj
        except Exception:
            pass

    issues = [i for i in repo.get_issues(state="open") if "pull_request" not in i.raw_data]
    paper_by_date = defaultdict(list)
    digest_issue_by_date = {}

    for it in issues:
        t = it.title
        if "日报" not in t:
            paper_date = extract_paper_date(it.raw_data)
            if paper_date:
                paper_by_date[paper_date].append(it.raw_data)
        dm = re.search(r"日报\s*(\d{8})", t)
        if dm:
            digest_issue_by_date[dm.group(1)] = it

    out_dir = Path("/tmp/RS-PaperClaw/daily_reports")
    out_dir.mkdir(parents=True, exist_ok=True)

    dates = sorted(paper_by_date.keys())
    if target_date:
        dates = [d for d in dates if d == target_date]

    if not dates:
        print(f"NO_DIGEST_DATE target={target_date or 'ALL'}")
        return

    for date in dates:
        md = build_digest_with_llm(
            date,
            sorted(paper_by_date[date], key=lambda x: x["number"]),
            stats=stats_map.get(date),
        )
        (out_dir / f"{date}.md").write_text(md, encoding="utf-8")

        title = f"日报 {date}"
        labels = [date, "日报"]
        if date in digest_issue_by_date:
            digest_issue_by_date[date].edit(body=md, title=title, labels=labels)
            print(f"UPDATED digest issue {date} -> #{digest_issue_by_date[date].number}")
        else:
            ni = repo.create_issue(title=title, body=md, labels=labels)
            print(f"CREATED digest issue {date} -> #{ni.number}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--date", dest="date", help="仅生成指定日期日报，格式 YYYYMMDD")
    parser.add_argument("--stats-json", dest="stats_json", help="筛选统计 JSON 文件路径")
    args = parser.parse_args()

    main(target_date=args.date, stats_json=args.stats_json)
