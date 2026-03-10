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
- 🖼️ **Visualize**: Extract and embed paper figures (first 2 pages)

**中文:**

RS-PaperClaw 是一个自动化系统，每日追踪、分析并发布 arXiv 遥感领域论文。基于 OpenClaw 实现：

- 🔍 **发现**：通过 arXiv API 自动获取最新遥感论文
- 📊 **分析**：生成结构化阅读报告，包含 10 问题深度分析框架
- 📤 **发布**：自动创建格式化的 GitHub Issues
- 🖼️ **可视化**：提取并嵌入论文图表（前 2 页）

---

## 🎯 Features / 核心功能

| Feature / 功能 | Description / 描述 |
|----------------|-------------------|
| **Daily Tracking / 每日追踪** | Automatically fetch papers from arXiv every day / 每日自动获取 arXiv 论文 |
| **Smart Filtering / 智能筛选** | Filter by keywords: remote sensing, satellite, earth observation, etc. / 按关键词筛选 |
| **Duplicate Detection / 去重检测** | Track processed papers to avoid duplicates / 记录已处理论文，避免重复 |
| **Report Generation / 报告生成** | 10-question deep analysis framework / 10 问题深度分析框架 |
| **Auto Publishing / 自动发布** | Create GitHub Issues via API / 通过 API 自动创建 Issues |
| **Figure Extraction / 图表提取** | Extract first 2 pages as preview / 提取前 2 页作为预览 |

---

## 📋 Report Template / 报告模板

Each paper report includes / 每篇论文报告包含：

### 📋 Basic Info / 基础信息
- Title, Authors, Date, arXiv Link
- Abstract Translation (Chinese) / 摘要翻译

### 📸 Paper Preview / 论文概览
- Page 1: Title + Abstract
- Page 2: Introduction + Method

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
# Python 3.8+
# Required packages
pip install PyGithub pymupdf pillow weasyprint
```

### Configuration / 配置

1. **Set GitHub Token / 设置 GitHub Token**
   ```bash
   export GITHUB_TOKEN="your_personal_access_token"
   ```

2. **Create Fine-grained Token / 创建细粒度 Token**
   - Go to: https://github.com/settings/personal-access-tokens
   - Repository access: Select this repo
   - Permissions:
     - `Contents`: Read and write
     - `Issues`: Read and write
     - `Metadata`: Read only

### Run / 运行

```bash
# Track and process today's papers
python scripts/batch_process_papers.py

# Process a single paper
python scripts/process_single_paper.py
```

---

## 📁 Project Structure / 项目结构

```
RS-PaperClaw/
├── papers/                      # Paper reports / 论文报告
│   ├── 20260310_FedEU.md
│   ├── 20260310_SIGMAE.md
│   └── figures/                 # Extracted figures / 提取的图表
│       ├── 20260310_FedEU_page-01.png
│       └── ...
├── scripts/                     # Automation scripts / 自动化脚本
│   ├── arxiv_rs_tracker.py      # Fetch papers from arXiv
│   ├── batch_process_papers.py  # Batch processing with deduplication
│   ├── process_single_paper.py  # Single paper processing
│   ├── upload_images_to_github.py
│   └── create_github_issue.py
├── processed_papers.txt         # Deduplication log / 去重记录
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
| `arxiv_rs_tracker.py` | Fetch and filter papers from arXiv API |
| `batch_process_papers.py` | Batch process with deduplication |
| `process_single_paper.py` | Process a single paper |
| `upload_images_to_github.py` | Upload extracted figures to repo |
| `create_github_issue.py` | Create new GitHub Issue |
| `update_github_issue.py` | Update existing Issue content |

---

## 📝 Workflow / 工作流程

```mermaid
graph LR
    A[arXiv API] --> B[Fetch Papers]
    B --> C[Filter & Deduplicate]
    C --> D[Download PDF]
    D --> E[Extract Figures]
    E --> F[Generate Report]
    F --> G[Upload to GitHub]
    G --> H[Create Issue]
```

---

## 🎯 Roadmap / 未来计划

- [ ] **LLM-powered Analysis** - Auto-generate 10-question analysis with LLM
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
