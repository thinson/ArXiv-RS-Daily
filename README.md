# RS-PaperClaw 🦞

**Automated arXiv Remote Sensing Paper Tracker & Analyzer powered by OpenClaw**

**基于 OpenClaw 的 arXiv 遥感论文自动追踪与分析系统**

---

## 📖 Overview / 项目概述

**English:**

RS-PaperClaw is an automated system that tracks, analyzes, and publishes daily remote sensing papers from arXiv. It leverages OpenClaw to:

- 🔍 **Discover**: Automatically fetch the latest remote sensing papers from arXiv API
- 📊 **Analyze**: Generate structured reading reports with 10-question deep analysis framework
- 📤 **Publish**: Auto-create GitHub Issues with formatted reports
- 🖼️ **Visualize**: Convert first 3 PDF pages to JPG previews and embed as 1x3 table

**中文:**

RS-PaperClaw 是一个自动化系统，每日追踪、分析并发布 arXiv 遥感领域论文。基于 OpenClaw 实现：

- 🔍 **发现**：通过 arXiv API 自动获取最新遥感论文
- 📊 **分析**：生成结构化阅读报告，包含 10 问题深度分析框架
- 📤 **发布**：自动创建格式化的 GitHub Issues
- 🖼️ **可视化**：将 PDF 前 3 页转换为 JPG 预览并以 1x3 表格嵌入

---

## 🎯 Features / 核心功能

| Feature / 功能 | Description / 描述 |
|----------------|-------------------|
| **Daily Tracking / 每日追踪** | Automatically fetch papers from arXiv every day / 每日自动获取 arXiv 论文 |
| **Smart Filtering / 智能筛选** | Filter by keywords: remote sensing, satellite, earth observation, etc. / 按关键词筛选 |
| **Duplicate Detection / 去重检测** | Track processed papers to avoid duplicates / 记录已处理论文，避免重复 |
| **Report Generation / 报告生成** | 10-question deep analysis framework / 10 问题深度分析框架 |
| **Auto Publishing / 自动发布** | Create GitHub Issues via API / 通过 API 自动创建 Issues |
| **PDF Preview / PDF 预览** | Convert first 3 PDF pages to JPG and render in 1x3 layout / 将 PDF 前 3 页转 JPG 并以 1x3 布局展示 |

---

## 📋 Report Template / 报告模板

Each paper report includes / 每篇论文报告包含：

### 📋 Basic Info / 基础信息
- Title, Authors, Date, arXiv Link
- Abstract Translation (Chinese) / 摘要翻译

### 📸 Paper Preview / 论文概览
- PDF Page 1-3 preview (JPG)
- Rendered as a single-row 3-column table

### ❓ 10-Question Analysis / 10 问题深度分析
1. **Problem / 解决的问题** - What problem does this paper solve?
2. **Prior Work / 前人工作** - Existing approaches and their limitations
3. **Limitations / 局限性** - What are the gaps in prior work?
4. **Core Idea / 核心思路** - Key insight and approach
5. **Innovations / 方法亮点** - Technical contributions and novelties
6. **Contributions / 主要贡献** - Main contributions of the paper
7. **Experiments / 实验评估** - Datasets and evaluation metrics
8. **Code Availability / 代码开源** - Is code/data available?
9. **Objective Review / 客观评价** - Strengths and weaknesses
10. **Critical Analysis / 批判审视** - Is it revolutionary or incremental?

### 💡 Extensions / 拓展思考
- Related Literature / 相关文献
- Application Scenarios / 应用场景
- Future Directions / 后续方向

---

## 🚀 Quick Start / 快速开始

### Prerequisites / 前置条件

```bash
# Python 3.10+
# Required packages
pip install PyGithub

# System tools (for PDF previews / text extraction)
# Ubuntu/Debian
sudo apt-get install -y poppler-utils
```

### Configuration / 配置

1. **Set environment variables / 设置环境变量**
   ```bash
   export GITHUB_TOKEN="your_github_token"
   export BAILIAN_KEY="your_bailian_api_key"
   # optional
   export REPO_NAME="thinson/RS-PaperClaw"
   export MODEL="MiniMax-M2.5"
   ```

2. **GitHub token permissions / GitHub Token 权限**
   - `Contents`: Read and write
   - `Issues`: Read and write
   - `Metadata`: Read only

### Run / 运行

```bash
# Process a single paper and update target issue
python scripts/paper_processor.py <arxiv_id> <issue_number>

# Example
python scripts/paper_processor.py 2603.08582v1 2
```

---

## 📁 Project Structure / 项目结构

```
RS-PaperClaw/
├── papers/
│   ├── figures/                 # legacy figure outputs
│   └── previews/                # PDF page previews (jpg)
├── scripts/
│   ├── paper_processor.py       # Main single-paper pipeline
│   └── prompts/                 # LLM prompts (translate/tags/summarize)
├── skills/
│   └── rs-paper-pipeline/
│       └── SKILL.md             # Reusable OpenClaw skill
├── processed_papers.txt
└── README.md
```

---

## 📊 Today's Papers / 今日论文

| Issue # | Paper / 论文 | Tags / 标签 | Status / 状态 |
|---------|-------------|-------------|---------------|
| #1 | FedEU: Evidential Uncertainty-Driven Federated Fine-Tuning | `Foundation Model` `Federated Learning` | ✅ Complete |
| #2 | Online Sparse Synthetic Aperture Radar Imaging | `SAR` `Online Learning` | ✅ Complete |
| #3 | BuildMamba: Visual State-Space Model for Building Segmentation | `Segmentation` `Mamba` | ✅ Complete |
| #4 | SIGMAE: Spectral-Index-Guided Foundation Model | `Foundation Model` `Multispectral` | ✅ Complete |

---

## 🔧 Scripts / 脚本说明

| Script / 脚本 | Description / 功能 |
|--------------|-------------------|
| `paper_processor.py` | Main pipeline: abs + PDF + preview + LLM + quality gate + issue update |
| `scripts/prompts/*.md` | Prompt templates for translation/tags/summary |

---

## 📝 Workflow / 工作流程

```mermaid
graph LR
    A[arXiv abs/API] --> B[Fetch Metadata]
    B --> C[Download PDF]
    C --> D[Convert PDF p1-p3 to JPG]
    D --> E[LLM: translate/tags/10Q]
    E --> F[Quality Gate]
    F --> G[Update Target Issue]
```

---

## 🧩 OpenClaw Skill / 技能封装

This repo now includes a reusable skill:

- `skills/rs-paper-pipeline/SKILL.md`
- Trigger: run/update RS paper issue pipeline with consistent output contract

---

## 🎯 Roadmap / 未来计划

- [x] **LLM-powered Analysis** - Auto-generate Chinese abstract + 10-question analysis with quality gate
- [ ] **Daily Cron Job** - Automated daily execution at 10:00/12:00/15:00/17:00
- [ ] **Multi-source Support** - Add IEEE TGRS, IGARSS, CVPR workshops
- [ ] **PDF Export** - Generate PDF reports for archival
- [ ] **Tag Classification** - Auto-classify papers with better taxonomy
- [ ] **Citation Network** - Build citation graph for related papers

---

## 🤝 Contributing / 贡献

Pull requests are welcome! For major changes, please open an issue first.

欢迎提交 PR！如有重大改动，请先创建 Issue 讨论。

---

## 📄 License / 许可证

MIT License

---

## 🙏 Acknowledgments / 致谢

- **OpenClaw** - AI assistant framework powering this project
- **arXiv** - Open access to research papers
- **GitHub** - Hosting and API for automated publishing

---

<p align="center">
  <em>🦞 Powered by OpenClaw | Made with ❤️ for Remote Sensing Community</em>
</p>
