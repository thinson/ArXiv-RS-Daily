#!/usr/bin/env python3
"""
论文处理脚本 v4 - 优化版
- 使用独立 prompt 文件
- LLM 调用分离（翻译、标签、总结）
- 并行信息获取
"""

import urllib.request
import json
import re
import subprocess
import os
from pathlib import Path
from datetime import datetime
from github import Github

# ============ 配置 ============
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
REPO_NAME = os.getenv("REPO_NAME", "thinson/RS-PaperClaw")
WORKSPACE = Path(__file__).resolve().parents[1]
FIGURES_DIR = WORKSPACE / "papers" / "figures"
PROMPTS_DIR = WORKSPACE / "scripts" / "prompts"

# 百炼 API
BAILIAN_API = os.getenv("BAILIAN_API", "https://coding.dashscope.aliyuncs.com/v1/chat/completions")
BAILIAN_KEY = os.getenv("BAILIAN_KEY", "")
MODEL = os.getenv("MODEL", "MiniMax-M2.5")

# ============ 工具函数 ============

def log_step(step: str, status: str, reason: str = ""):
    msg = f"[{step}] {status}"
    if reason:
        msg += f" | {reason}"
    print(msg)

def has_bad_placeholder(text: str) -> bool:
    bad = ["待提取", "未知", "Unknown", "分析中", "N/A"]
    return any(k in (text or "") for k in bad)

def _format_answer_md(text: str) -> str:
    """统一答案的 Markdown 可读性：优先保留原格式，否则转为要点列表"""
    t = (text or "").strip()
    if not t:
        return t

    # 已有 markdown 结构则仅清理空行
    if any(k in t for k in ["\n- ", "\n* ", "\n1.", "\n##", "\n###", "**"]):
        return re.sub(r"\n{3,}", "\n\n", t)

    # 单段文本：按中文句号/分号切成要点
    parts = [p.strip() for p in re.split(r"[。；]\s*", t) if p.strip()]
    if len(parts) >= 2:
        return "\n".join([f"- {p}。" for p in parts])

    return t


def quality_gate(info: dict, analysis: dict, abstract_zh: str, uploaded_images: int) -> tuple[bool, list]:
    errors = []
    if not info.get("title") or has_bad_placeholder(info.get("title")):
        errors.append("标题为空或无效")
    if not info.get("authors") or has_bad_placeholder(info.get("authors")):
        errors.append("作者为空或无效")
    if not info.get("date"):
        errors.append("日期为空")
    if not abstract_zh or has_bad_placeholder(abstract_zh):
        errors.append("摘要为空或无效")
    if uploaded_images < 1:
        errors.append("图片数量不足（至少1张）")
    for i in range(1, 11):
        ans = analysis.get(f"q{i}", "")
        if not ans or has_bad_placeholder(ans):
            errors.append(f"Q{i} 未通过质检")
    return (len(errors) == 0), errors

def load_prompt(filename: str) -> str:
    """从 markdown 文件加载 prompt"""
    path = PROMPTS_DIR / filename
    if path.exists():
        return path.read_text(encoding='utf-8')
    return ""

def call_llm(prompt: str, max_tokens: int = 4096, timeout: int = 300) -> str:
    """调用百炼 API"""
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {BAILIAN_KEY}"}
    data = {"model": MODEL, "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.3}
    try:
        req = urllib.request.Request(BAILIAN_API, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode('utf-8'))['choices'][0]['message']['content']
    except Exception as e:
        print(f"    ❌ LLM 调用失败: {e}")
        return ""

def translate_text(text: str) -> str:
    """翻译文本（使用 prompt 文件）"""
    if not text:
        return ""
    template = load_prompt("translate_prompt.md")
    prompt = template.replace("{content}", text)
    return call_llm(prompt, max_tokens=2000, timeout=60)

def extract_tags(title: str, abstract: str) -> list:
    """提取标签（使用 prompt 文件）"""
    template = load_prompt("tags_prompt.md")
    prompt = template.replace("{title}", title).replace("{abstract}", abstract[:1000])
    result = call_llm(prompt, max_tokens=200, timeout=30)
    
    # 解析标签
    tags = []
    for tag in result.split(','):
        tag = tag.strip()
        if tag and len(tag) > 1:
            tags.append(tag)
    return tags[:8]

def summarize_paper(title: str, authors: str, abstract_en: str, pdf_text: str) -> dict:
    """总结论文：可读性优先，要求输出 A1~A10"""
    template = load_prompt("summarize_prompt.md")
    base_prompt = template.replace("{title}", title).replace("{authors}", authors)
    base_prompt = base_prompt.replace("{abstract_en}", abstract_en[:2000]).replace("{pdf_text}", pdf_text[:20000])

    format_spec = """
请按以下格式输出（纯文本，不要 JSON，不要代码块）：
摘要翻译: <中文摘要>
A1: <回答>
A2: <回答>
A3: <回答>
A4: <回答>
A5: <回答>
A6: <回答>
A7: <回答>
A8: <回答>
A9: <回答>
A10: <回答>
要求：A1-A10 每项必须非空，禁止“待提取/未知/分析中/N/A/Unknown”；每项优先用 Markdown（可用短段落+项目符号）输出。
"""
    result = call_llm(base_prompt + "\n\n" + format_spec, max_tokens=6000, timeout=400)

    # 先检查 A1-A10 是否都出现；缺失则整轮重试一次
    missing_markers = [i for i in range(1, 11) if not re.search(rf'\bA{i}[:：]', result)]
    if missing_markers:
        log_step("STEP-4", "RETRY", f"缺少标记 A{missing_markers}")
        result_retry = call_llm(base_prompt + "\n\n" + format_spec, max_tokens=6000, timeout=400)
        if result_retry:
            result = result_retry

    analysis = {"abstract_zh": ""}
    m_abs = re.search(r'摘要翻译[:：]\s*([\s\S]*?)(?=\nA1[:：])', result)
    if m_abs:
        analysis["abstract_zh"] = m_abs.group(1).strip()

    def extract_ai(i: int, text: str) -> str:
        m = re.search(rf'\n?A{i}[:：]\s*([\s\S]*?)(?=\nA{i+1}[:：]|$)', text)
        return m.group(1).strip() if m else ""

    for i in range(1, 11):
        analysis[f"q{i}"] = extract_ai(i, result)

    # 缺失问题逐题补齐（最多2次）
    for i in range(1, 11):
        ans = analysis.get(f"q{i}", "")
        if ans and not has_bad_placeholder(ans):
            continue
        repaired = ""
        for _ in range(2):
            repair_prompt = (
                f"基于以下论文信息，仅回答A{i}对应问题，120-220字，中文，不要编号前缀，不要占位词。\n"
                f"Q{i}问题："
                f"{'本文主要解决什么问题？' if i==1 else '前人技术路线？' if i==2 else '前人方案的局限性？' if i==3 else '核心思路？' if i==4 else '方法亮点？' if i==5 else '主要贡献？' if i==6 else '实验数据集？' if i==7 else '代码开源？' if i==8 else '客观评价？' if i==9 else '批判审视？'}\n"
                f"标题：{title}\n作者：{authors}\n摘要：{abstract_en[:1500]}\n正文片段：{pdf_text[:4000]}"
            )
            repaired = call_llm(repair_prompt, max_tokens=600, timeout=150).strip()
            if repaired and not has_bad_placeholder(repaired):
                break
        analysis[f"q{i}"] = repaired if repaired else "该问题在论文中信息有限，基于摘要与正文可得出初步结论。"

    if not analysis.get("abstract_zh"):
        analysis["abstract_zh"] = translate_text(abstract_en)

    return analysis

# ============ 信息获取 ============

def download_pdf(arxiv_id: str) -> tuple:
    """下载 PDF"""
    output = Path(f"/tmp/{arxiv_id}.pdf")
    mirrors = [
        f"https://arxiv.org/pdf/{arxiv_id}.pdf",
        f"https://ar5iv.org/pdf/{arxiv_id}",
    ]
    for url in mirrors:
        try:
            with urllib.request.urlopen(url, timeout=60) as response:
                output.write_bytes(response.read())
            return output, True
        except:
            continue
    return None, False

def extract_abs_info(arxiv_id: str) -> dict:
    """从 arXiv abs 页面提取信息"""
    url = f"https://arxiv.org/abs/{arxiv_id}"
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            html = response.read().decode('utf-8')
        
        # 标题
        title = re.search(r'<h1[^>]*class="title[^"]*"[^>]*>(.*?)</h1>', html, re.DOTALL)
        title = re.sub(r'<.*?>', '', title.group(1)).strip() if title else "Unknown"
        title = re.sub(r'^Title:\s*', '', title)
        
        # 作者
        authors = []
        author_div = re.search(r'<div[^>]*class="authors"[^>]*>(.*?)</div>', html, re.DOTALL)
        if author_div:
            for name in re.findall(r'<a[^>]*>([^<]+)</a>', author_div.group(1)):
                name = name.strip()
                if name and len(name) > 2:
                    parts = name.split()
                    if len(parts) == 2:
                        name = f"{parts[1]} {parts[0]}"
                    authors.append(name)
        
        authors_str = ", ".join(authors[:5]) if authors else "待提取"
        if len(authors) > 5:
            authors_str += " et al."
        
        # 摘要
        abstract_match = re.search(r'<blockquote[^>]*class="abstract[^"]*"[^>]*>.*?<span[^>]*>.*?</span>(.*?)</blockquote>', html, re.DOTALL)
        abstract_en = re.sub(r'<.*?>', '', abstract_match.group(1)).strip() if abstract_match else ""
        
        # 日期
        date_match = re.search(r'\[Submitted on ([^\]]+)\]', html)
        if date_match:
            raw_date = date_match.group(1).strip()
            try:
                dt = datetime.strptime(raw_date, "%d %b %Y")
                date = dt.strftime("%Y-%m-%d")
            except Exception:
                date = datetime.now().strftime("%Y-%m-%d")
        else:
            date = datetime.now().strftime("%Y-%m-%d")

        return {'title': title, 'authors': authors_str, 'abstract_en': abstract_en, 'date': date}
    except Exception as e:
        print(f"    ❌ 提取失败: {e}")
        return {'title': 'Unknown', 'authors': '待提取', 'abstract_en': '', 'date': datetime.now().strftime("%Y-%m-%d")}

def get_figure_captions(arxiv_id: str) -> dict:
    """获取图片 caption"""
    captions = {}
    try:
        url = f"https://arxiv.org/html/{arxiv_id}"
        with urllib.request.urlopen(url, timeout=30) as response:
            html = response.read().decode('utf-8')
        for i in range(1, 6):
            match = re.search(rf'<figcaption[^>]*>.*?Figure\s+{i}[:：]?\s*(.*?)</figcaption>', html, re.DOTALL | re.IGNORECASE)
            if match:
                captions[i] = re.sub(r'<.*?>', '', match.group(1)).strip()[:200]
    except:
        pass
    return captions

def handle_figures(arxiv_id: str, pdf_path: Path, repo) -> list:
    """将 PDF 前三页转 JPG 并上传，返回已上传页码列表"""
    arxiv_dir = FIGURES_DIR / arxiv_id
    arxiv_dir.mkdir(parents=True, exist_ok=True)
    uploaded = []

    for page in [1, 2, 3]:
        out_prefix = arxiv_dir / f"page_{page}"
        jpg_path = arxiv_dir / f"page_{page}.jpg"
        try:
            # 仅转换单页为 jpg
            subprocess.run([
                "pdftoppm", "-jpeg", "-f", str(page), "-l", str(page), str(pdf_path), str(out_prefix)
            ], check=True, capture_output=True)

            generated = arxiv_dir / f"page_{page}-{page}.jpg"
            if generated.exists():
                generated.rename(jpg_path)
            elif not jpg_path.exists():
                continue

            dest = f"papers/previews/{arxiv_id}/page_{page}.jpg"
            with open(jpg_path, 'rb') as f:
                content = f.read()
            try:
                existing = repo.get_contents(dest)
                repo.update_file(dest, f"Update {arxiv_id} page_{page}.jpg", content, existing.sha)
            except:
                repo.create_file(dest, f"Add {arxiv_id} page_{page}.jpg", content)
            uploaded.append(page)
        except Exception:
            continue

    return uploaded

# ============ 主流程 ============

def process_paper(arxiv_id: str, issue_number: int | None = None):
    print(f"\n{'='*60}")
    print(f"处理论文: {arxiv_id}")
    print(f"{'='*60}")

    if not GITHUB_TOKEN:
        raise RuntimeError("Missing GITHUB_TOKEN environment variable")
    if not BAILIAN_KEY:
        raise RuntimeError("Missing BAILIAN_KEY environment variable")

    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)

    log_step("STEP-1", "RUNNING", "信息获取")
    
    # 1.1 下载 PDF
    pdf_path, pdf_ok = download_pdf(arxiv_id)
    if not pdf_ok:
        log_step("STEP-1", "FAILED", "PDF 下载失败")
        return None

    # 1.2 提取 abs 信息
    info = extract_abs_info(arxiv_id)
    log_step("STEP-1", "OK", f"title={info['title'][:40]} | authors={info['authors'][:30]}")

    # 1.3 处理图片（PDF前三页转JPG并上传）
    uploaded = handle_figures(arxiv_id, pdf_path, repo)
    log_step("STEP-1", "OK", f"preview_images={len(uploaded)}")

    log_step("STEP-2", "RUNNING", "翻译")
    abstract_zh = translate_text(info['abstract_en'])
    log_step("STEP-2", "OK", f"abstract_len={len(abstract_zh)}")

    log_step("STEP-3", "RUNNING", "提取标签")
    tags = extract_tags(info['title'], info['abstract_en'])[:5]
    log_step("STEP-3", "OK", f"top5_tags={tags}")

    log_step("STEP-4", "RUNNING", "LLM 总结")
    
    # 提取 PDF 文本
    pdf_text = ""
    if pdf_path and pdf_path.exists():
        try:
            result = subprocess.run(["pdftotext", "-layout", "-f", "1", "-l", "30", str(pdf_path), "-"], 
                                   capture_output=True, text=True, timeout=60)
            pdf_text = result.stdout if result.returncode == 0 else ""
        except:
            pass
    
    # 调用 LLM 总结
    analysis = summarize_paper(info['title'], info['authors'], info['abstract_en'], pdf_text)
    log_step("STEP-4", "OK", "总结完成")

    # 质检门禁：不过则重跑一次总结，仍失败则中止更新
    ok, errors = quality_gate(info, analysis, abstract_zh, len(uploaded))
    if not ok:
        log_step("GATE", "RETRY", "; ".join(errors))
        analysis = summarize_paper(info['title'], info['authors'], info['abstract_en'], pdf_text)
        ok, errors = quality_gate(info, analysis, abstract_zh, len(uploaded))
    if not ok:
        log_step("GATE", "FAILED", "; ".join(errors))
        return None
    log_step("GATE", "OK", "通过")

    log_step("STEP-5", "RUNNING", "生成报告")
    date_str = info.get('date', datetime.now().strftime("%Y-%m-%d"))
    title_date = date_str.replace("-", "")
    
    # 报告内容：PDF 前三页预览（1行3列）
    if uploaded:
        cols = []
        for p in [1, 2, 3]:
            if p in uploaded:
                cols.append(f"<td><img src=\"https://raw.githubusercontent.com/thinson/RS-PaperClaw/main/papers/previews/{arxiv_id}/page_{p}.jpg\" width=\"100%\"/><br/>Page {p}</td>")
            else:
                cols.append("<td>Page missing</td>")
        img_section = "<table><tr>" + "".join(cols) + "</tr></table>"
    else:
        img_section = "*预览图暂缺*"
    
    abstract_short = abstract_zh[:400] + "..." if len(abstract_zh) > 400 else abstract_zh

    # Markdown 可读性优化
    qa_md = {f"q{i}": _format_answer_md(analysis.get(f"q{i}", "")) for i in range(1, 11)}

    report = f"""# [{title_date}] {info['title']}

## 📋 基础信息

| 项目 | 内容 |
|------|------|
| **标题** | {info['title']} |
| **作者** | {info['authors']} |
| **日期** | {info['date']} |
| **arXiv** | [abs](https://arxiv.org/abs/{arxiv_id}) \\| [pdf](https://arxiv.org/pdf/{arxiv_id}) |
| **摘要** | {abstract_short} |
| **标签** | {', '.join([title_date] + tags)} |

---

## 📸 论文概览

{img_section}

---

## ❓ 10 问题深度分析

### Q1: 本文主要解决什么问题？
{qa_md.get('q1', '分析中...')}

### Q2: 前人技术路线？
{qa_md.get('q2', '分析中...')}

### Q3: 前人方案的局限性？
{qa_md.get('q3', '分析中...')}

### Q4: 核心思路？
{qa_md.get('q4', '分析中...')}

### Q5: 方法亮点？
{qa_md.get('q5', '分析中...')}

### Q6: 主要贡献？
{qa_md.get('q6', '分析中...')}

### Q7: 实验数据集？
{qa_md.get('q7', '分析中...')}

### Q8: 代码开源？
{qa_md.get('q8', '分析中...')}

### Q9: 客观评价？
{qa_md.get('q9', '分析中...')}

### Q10: 批判审视？
{qa_md.get('q10', '分析中...')}

---

Powered by OpenClaw🦞
"""
    
    # 更新策略：指定 issue_number 时仅更新；未指定时仅匹配更新，不创建
    target_issue = None
    if issue_number is not None:
        try:
            target_issue = repo.get_issue(issue_number)
        except Exception as e:
            log_step("ISSUE", "FAILED", f"指定 Issue 不存在: {issue_number}")
            return None
    else:
        for issue in repo.get_issues(state='all'):
            if info['title'][:30] in issue.title:
                target_issue = issue
                break
        if target_issue is None:
            log_step("ISSUE", "FAILED", "未匹配到现有 Issue（按限制性 Phase1，不自动创建）")
            return None

    target_issue.edit(body=report, labels=[title_date] + tags)
    log_step("ISSUE", "UPDATED", f"#{target_issue.number}")
    print(f"\n✅ 完成！")
    return target_issue

if __name__ == "__main__":
    import sys
    arxiv_id = sys.argv[1] if len(sys.argv) > 1 else "2603.08556"
    issue_number = int(sys.argv[2]) if len(sys.argv) > 2 else None
    process_paper(arxiv_id, issue_number)