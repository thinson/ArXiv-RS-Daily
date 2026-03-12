<div align="center">

# RS-PaperClaw🦞

### 遥感论文自动追踪与分析流水线

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](#)
[![Status](https://img.shields.io/badge/Status-Active-2EA043)](#)
[![Workflow](https://img.shields.io/badge/Workflow-arXiv%20%E2%86%92%20Issue%20%E2%86%92%20Digest-8A2BE2)](#)

**arXiv → 单篇报告 Issue → 每日汇总日报**

English version: **[README_EN.md](./README_EN.md)**

</div>

---

> 📌 **近期论文日报**：查看最近三天汇总与归档 → **[进入日报导航](./daily_reports/README.md)**

## ✨ 项目定位

RS-PaperClaw 每天自动完成：

- 🔎 拉取 arXiv 候选论文（遥感相关）
- 🧠 关键词 + LLM 交叉筛选
- 📝 生成/更新单篇阅读报告（GitHub Issue）
- 🗞️ 生成当天日报（GitHub Issue）
- 🗂️ 同步日报到 `daily_reports/YYYYMM/YYYYMMDD.md`
- 📮 推送日报到飞书

---


## 🎯 为什么以 Issue 为核心？

- 🧭 **可追踪**：单论文单 Issue，历史与改动可回溯。
- 🤝 **易协作**：评论即讨论，补充即沉淀。
- ⚙️ **自动化友好**：稳定更新同一条，便于增量执行。
- 🗂️ **归档闭环**：Issue 动态协作 + 日报静态归档。


## 🧩 核心能力

| 模块 | 输出 |
|---|---|
| 单篇报告 | 基础信息、TL;DR、中文摘要、标签、前三页预览图、10问分析 |
| 日报生成 | 今日概况（含数量统计）、亮点、文章列表、观察 |
| 质量控制 | 过滤占位内容，保障结构完整与可读性 |
| 结果归档 | Issue + Markdown 双轨同步，便于追踪与回溯 |

---

## 🗺️ 目录结构（主分支）

```text
RS-PaperClaw/
├── daily_reports/                    # 日报归档（按年月）
│   ├── README.md
│   └── YYYYMM/YYYYMMDD.md
├── papers/previews/                  # 论文预览图（用于 Issue 展示）
├── skills/rs-paper-pipeline/         # 技能与脚本
│   ├── README.md
│   ├── SKILL.md
│   └── scripts/
│       ├── paper_processor.py
│       ├── daily_arxiv_cross_filter.py
│       ├── daily_digest_llm_upgrade.py
│       ├── run_rs_daily_workday.py
│       └── sync_daily_reports_to_repo.py
└── README_EN.md
```

---

## 🚀 快速开始

### 1) 环境准备

- Python 3.10+
- `pip install PyGithub`
- 系统工具：`poppler-utils`（含 `pdftoppm`、`pdftotext`）

### 2) 配置环境变量

```bash
export GITHUB_TOKEN="..."
export GITHUB_REPO="owner/repo"
export BAILIAN_API_KEY="..."
# 可选
export FEISHU_TARGET="user:xxx"
export LLM_MODEL="MiniMax-M2.5"
```

### 3) 运行当天流程

```bash
python3 skills/rs-paper-pipeline/scripts/run_rs_daily_workday.py
```

---

## ⏰ 定时任务（工作日 09:05）

```cron
CRON_TZ=Asia/Shanghai
5 9 * * 1-5 /usr/bin/python3 /path/to/skills/rs-paper-pipeline/scripts/run_rs_daily_workday.py >> /path/to/logs/rs_daily_workday.log 2>&1
```

---

## 📎 说明

- 默认文档语言为中文；英文请看 [README_EN.md](./README_EN.md)
- 所有脚本均位于 `skills/rs-paper-pipeline/scripts/`

---

<div align="center">

**Powered by OpenClaw🦞**

</div>
