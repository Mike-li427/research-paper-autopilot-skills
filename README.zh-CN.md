# Research Paper Autopilot 科研论文技能包

[English](README.md)

Research Paper Autopilot 是一个面向 Codex 的科研论文 skills bundle。它的目标不是“凭空代写论文”，而是把真实文献、真实数据、真实实验代码、真实日志、真实结果和可审计材料组织成一个完整的论文项目包。

主 skill 是 `research-paper-autopilot`。它负责总控调度，按项目需要调用或借鉴已打包的专业 skill：文献检索、gap 分析、实验设计、实验代码、结果分析、论文写作、审稿模拟、引用核查、图表/数据支持、完整性审计和投稿材料整理。

如果证据不足，它不能假装已经完成。正确行为是回到补文献、补数据、补实验、补分析、降级表述，或者把项目标记为 `BLOCKED` / `PROVISIONAL`。

## 这个仓库包含什么

当前仓库在 `skills/` 下打包了 58 个可安装 Codex skill。

核心组成：

- `research-paper-autopilot`：从 idea 到论文项目包的总控编排 skill。
- 通用科研流程：`academic-pipeline`、`deep-research`、`academic-paper`、`academic-paper-reviewer`、`academic-research-suite`、`automated-research-paper`。
- 文献与选题：`literature-review`、`literature-survey-skill`、`research-gap-analysis`、`scientific-brainstorming`。
- CCF/AI 论文流程：idea 优化、文献检索、实验设计、论文写作、审稿模拟、完整性审计、投稿检查和 rebuttal 支持。
- Nature/SCI 流程：学术检索、引用支持、图表规划、数据可用性、正文写作、语言润色、审稿模拟和回复信。
- 论文写作栈：`paper-spine` 及其 build、citation、LaTeX、research、rewrite、translation、audit、update 等内部 helper。
- 证据与核查工具：`citation-check-skill`、`statistical-analysis`、`papi-*` 文献库/RAG helper、`papi-verify` 论文实现核查。
- 科研产物工具：`pdf`、`scientific-visualization`、`PaperBanana`。

完整 skill 清单在 `skills_manifest.json`。第三方来源和再分发提醒在 `THIRD_PARTY_SKILLS.md`。

## 适合谁用

适合这些场景：

- 你有一个粗略研究想法，想把它推进成可执行论文项目。
- 你需要基于文献找 gap、贡献点和相关工作结构。
- 你需要设计实验、baseline、metric、ablation 和分析计划。
- 你希望生成贴合项目的实验代码骨架，而不是空泛模板。
- 你想检查代码、结果、图表、引用和正文 claim 是否互相支撑。
- 你想得到一个人类研究者可以继续运行、检查、修改和提交的项目目录。

不适合这些用途：

- 编造文献、DOI、数据、实验结果、p 值、审稿意见或投稿状态。
- 把没有运行过的代码包装成已完成实验。
- 在缺少证据时生成“可投稿成稿”。
- 替代导师、合作者、领域专家、伦理审查或目标 venue 的正式规则。

## 环境要求

- 支持本地 skills 的 Codex。
- Python 3.9 或更高版本。
- 可以运行 Python 命令的终端。

安装脚本本身不需要额外依赖。由 skill 生成的具体论文项目，可能根据领域需要 Python、R、LaTeX 或其他科研依赖。

## 安装

克隆仓库：

```bash
git clone https://github.com/<your-name>/<your-repo>.git
cd <your-repo>
```

安装前先校验：

```bash
python scripts/validate_bundle.py
```

预览会安装哪些 skill：

```bash
python scripts/install.py --dry-run
```

安装全部 skill 到默认 Codex skills 目录：

```bash
python scripts/install.py
```

默认安装目录是：

```text
~/.codex/skills
```

Windows 上通常是：

```text
C:\Users\<你的用户名>\.codex\skills
```

### 安装选项

安装到自定义 Codex home：

```bash
python scripts/install.py --codex-home /path/to/.codex
```

直接指定 skills 目录：

```bash
python scripts/install.py --skills-dir /path/to/.codex/skills
```

只安装主 autopilot skill：

```bash
python scripts/install.py --only research-paper-autopilot
```

只安装几个指定 skill：

```bash
python scripts/install.py --only research-paper-autopilot deep-research academic-paper citation-check-skill
```

覆盖已安装的同名 skill：

```bash
python scripts/install.py --force
```

预览覆盖安装：

```bash
python scripts/install.py --dry-run --force
```

安装后如果 Codex 没立刻识别，新开一个 Codex 会话即可。

## 快速使用

安装完成后，可以直接对 Codex 说：

```text
Use $research-paper-autopilot to turn my research idea into an evidence-grounded paper project package.
```

也可以用中文：

```text
从 idea 到投稿，帮我做一个基于真实文献和真实实验结果的论文项目包。
```

```text
帮我做 CCF/SCI 论文全流程，包含文献、实验、审稿模拟和复现材料。
```

```text
审核我的论文项目：检查引用、实验结果、代码、图表和正文 claim 是否互相支撑。
```

默认交互语言跟随用户。除非目标 venue 或用户明确要求中文，论文正文和面向投稿的材料默认输出英文。

## 推荐输入

给得越具体，产物越可用。建议提供：

- 研究想法或暂定标题。
- 目标领域、期刊、会议或论文类型。
- 已有材料路径：笔记、PDF、BibTeX、数据、代码、日志、旧稿。
- 是否已有数据，实验是否已经跑过。
- 预期方法、baseline、metric 或约束条件。
- 截止日期和算力预算。
- 哪些 claim 必须证明、必须弱化或必须避免。

最少只给一个 idea 也可以启动，但 skill 会把证据缺口记录下来，不会把未完成部分伪装成已完成。

## 默认项目产物

`research-paper-autopilot` 目标是创建或维护这样的论文项目目录：

```text
paper-project/
  PROGRESS.md
  RESTRICTS.yaml
  literature/
  plans/
  code/
    README.md
    config.yaml
    run_experiments.py
    analyze_results.py
  results/
  figures/
  paper/
  submission/
  audit/
    audit_report.json
    claim_evidence_map.json
    code_review_packet.md
    code_review_ledger.md
```

常见产物包括：

- 分阶段计划和进度日志。
- 文献检索记录和引用支撑。
- gap 分析和贡献点设计。
- 方法与实验设计。
- 带 config、seed、日志和结果 schema 的实验代码骨架。
- raw result、summary、图表和 claim-evidence 映射。
- 论文初稿或分节草稿。
- 模拟审稿意见和修订记录。
- 完整性审计报告。
- 复现清单和投稿检查清单。

## 工作流

主流程是一个状态机：

```text
Intake
-> Track Detect
-> Literature
-> Gap
-> Method / Experiment
-> Execution / Analysis
-> Multi-Agent Code Review
-> Writing
-> Review
-> Revision
-> Integrity Audit
-> Submission Package
```

每个阶段都要记录：

- `stage`：当前阶段。
- `inputs`：使用了哪些文件、笔记、数据和用户要求。
- `actions`：做了什么。
- `artifacts`：创建或修改了哪些产物。
- `evidence`：支撑该阶段的引用、日志、结果文件或审查记录。
- `decision`：`PROCEED`、`REFINE`、`PIVOT` 或 `BLOCKED`。
- `next`：下一步动作或修复路线。

## 赛道识别

总控会自动判断论文赛道，并启用对应 specialist skill 和质量门。

常见赛道：

- `CCF_AI`：AI、机器学习、系统、数据挖掘、安全、NLP、CV 等会议型项目。
- `NATURE_SCI`：高影响力科学期刊或跨学科期刊型项目。
- `REVIEW_SURVEY`：综述、survey、taxonomy、perspective 类文章。
- `GENERIC_RESEARCH`：不明显属于专门赛道的一般科研论文或报告。

路由结果应包含：

- `primary_track`：主赛道。
- `secondary_tracks`：混合项目需要启用的额外赛道。
- `active_gate_sets`：必须通过的质量门集合。

混合项目可以同时启用多个 gate。例如生物医学 AI 项目，可能同时启用 CCF/AI 实验 gate 和 Nature/SCI 的图表、数据可用性 gate。

## 证据与反伪造规则

skill 禁止伪造：

- 文献、引用、DOI、论文标题、作者列表、原文摘录。
- 数据、数据集、样本量、标签、采集流程。
- 实验结果、metric、p 值、置信区间、日志。
- 审稿意见、录用状态、投稿状态或 venue 决策。
- 没有真实观察到的仓库、环境或算力信息。

证据不足时，应该：

- 继续检索文献。
- 请求或定位真实数据。
- 生成实验/分析计划，而不是声称已有结果。
- 在环境允许时运行代码并归档日志和结果。
- 把确定性结果表述降级为假设、计划或待验证方向。
- 把项目标记为 `BLOCKED` 或 `PROVISIONAL`。

只要硬证据门没有通过，就不能把项目标成 submission-ready。

## 实验代码标准

autopilot 内置了实验代码规范。生成或修改代码时，要像认真维护的研究项目代码，而不是泛泛 AI 模板。

必须具备：

- 文件名、函数名、配置字段、日志字段、metric 和结果 schema 都贴合具体研究问题。
- 明确读取 config，并保存 config snapshot。
- 合法随机初始化、数据划分、bootstrap 或仿真时记录 seed。
- 结构化日志包含 command line、TIME_ESTIMATE、run status 和 output path。
- raw output 和 summary output 都要落盘。
- 检查 NaN/Inf，并识别 failed/crashed run。
- 相关时预留 baseline、ablation 和 metric 接口。
- `code/README.md` 中写清楚运行命令。

会被阻断的模式：

- 把 mock result 当作实验结果。
- 硬编码 accuracy、F1、p 值或论文结论数字。
- 用随机数生成趋势线、曲线或指标来支撑论文。
- 大量与研究任务无关的万能 helper。
- 全项目到处都是 `process_data`、`run_model`、`calculate_metric` 这类机械命名。
- 注释解释显而易见代码，却不解释研究选择、边界条件和实验假设。
- 在需要复现性的任务里塞进一个一次性巨型脚本。

优先级是：正确性第一，复现性第二，自然可维护性第三。代码风格不能压过证据真实性。

## 强制多智能体代码审查

只要项目包含实验代码、分析代码、结果文件、统计结论或指标型正文 claim，就必须在结果入稿前通过六角色多智能体代码审查。

这不是可选项，也不能用单个 agent 的自查代替。

六个必需角色：

- Algorithm Reviewer：检查实现是否符合方法、公式、伪代码和正文描述。
- Experiment Design Reviewer：检查数据集、baseline、ablation、预算和比较公平性。
- Data Leakage Reviewer：检查 split、标签、预处理、缓存、调参集和测试污染风险。
- Metrics & Statistics Reviewer：检查 metric 定义、聚合方式、统计检验、置信区间和 p 值。
- Reproducibility Reviewer：检查 seed、config、日志、环境、输出路径和运行命令。
- Code Quality Reviewer：检查代码结构、命名、错误处理、项目贴合度和非模板化质量。

审查流程：

1. 冻结当前代码和结果。
2. 运行静态审计。
3. 用 `prepare_code_review_packet.py` 生成 `audit/code_review_packet.md`。
4. 启动六个独立 reviewer agent 或独立 session。
5. 把每个审查结果写入 `audit/code_review_ledger.md` 或 `.json`。
6. 修复所有未解决的 `BLOCK`。
7. 代码或结果变化后重新生成 packet、重新审查或更新 ledger。

ledger 必须包含：

- reviewer role。
- `PASS`、`WARN` 或 `BLOCK`。
- evidence location。
- findings。
- required fixes。
- reviewer run/session ID。
- 与当前 packet 对应的 `packet_sha256`。

硬阻断条件：

- 缺少 ledger。
- 少于六个必需角色。
- 重复角色或角色冲突。
- 空洞 `PASS`。
- evidence 写成 `TBD`、`none` 或其他占位符。
- 存在未解决的 `BLOCK`。
- `WARN` 没有接受理由或后续补测计划。
- 代码/结果变化后 packet hash 过期。

如果当前环境不能启动多个独立 reviewer，状态必须记为 `BLOCKED`，不能降级成单 agent 自查通过。

## 结果产物 schema

实验或分析结果不能只写在正文里，必须有可审计 artifact。

一个合格的结果包应包含：

- raw run output。
- summary table 或 metrics file。
- config snapshot。
- seed。
- command line。
- log path。
- code hash。
- result hash。
- environment metadata。
- 可用时记录 git metadata。
- `completed`、`failed` 或 `crashed` 等 run status。

审计会阻断损坏的 JSON/CSV、NaN/Inf、把 failed run 当证据、手写 summary 冒充实验结果、以及没有 result/code/log/audit artifact 支撑的 p 值或统计 claim。

## 完整性审计

审计会检查论文项目内部是否互相支撑。

重点检查：

- 正文 claim 是否缺少引用或结果支撑。
- 引用是否缺失、格式错误或无法支撑对应表述。
- 数字 claim 是否和 result artifact 一致。
- 图表是否缺少源数据或生成脚本。
- 实验段落是否早于代码、结果和审查完成。
- 代码质量问题和可疑模板化模式。
- 是否缺少 multi-agent code review packet 或 ledger。
- 投稿清单是否有硬缺口。

可能结果：

- `PROCEED`：证据足够进入下一阶段。
- `REFINE`：已有基础，但需要修改。
- `PIVOT`：当前 idea 或方法需要调整。
- `BLOCKED`：不能继续包装成完成论文项目。

## 常用命令

校验 bundle：

```bash
python scripts/validate_bundle.py
```

预览安装：

```bash
python scripts/install.py --dry-run
```

只安装 autopilot：

```bash
python scripts/install.py --only research-paper-autopilot
```

直接编译 autopilot 的三个核心脚本：

```bash
python -m py_compile \
  skills/research-paper-autopilot/scripts/scaffold_autopilot_project.py \
  skills/research-paper-autopilot/scripts/prepare_code_review_packet.py \
  skills/research-paper-autopilot/scripts/audit_autopilot_project.py
```

Windows PowerShell 可用：

```powershell
python -m py_compile `
  skills\research-paper-autopilot\scripts\scaffold_autopilot_project.py `
  skills\research-paper-autopilot\scripts\prepare_code_review_packet.py `
  skills\research-paper-autopilot\scripts\audit_autopilot_project.py
```

## 仓库结构

```text
.
├─ .codex-plugin/
│  └─ plugin.json
├─ scripts/
│  ├─ install.py
│  └─ validate_bundle.py
├─ skills/
│  ├─ research-paper-autopilot/
│  └─ ...
├─ skills_manifest.json
├─ THIRD_PARTY_SKILLS.md
├─ README.md
├─ README.zh-CN.md
└─ LICENSE
```

主 skill 内部结构：

```text
skills/research-paper-autopilot/
├─ SKILL.md
├─ agents/
├─ references/
│  ├─ anti-fabrication.md
│  ├─ artifact-contract.md
│  ├─ experiment-code-standard.md
│  ├─ multi-agent-code-review.md
│  ├─ orchestration.md
│  ├─ quality-gates.md
│  └─ track-routing.md
└─ scripts/
   ├─ scaffold_autopilot_project.py
   ├─ prepare_code_review_packet.py
   └─ audit_autopilot_project.py
```

## 更新

拉取最新代码：

```bash
git pull
```

校验：

```bash
python scripts/validate_bundle.py
```

重新安装：

```bash
python scripts/install.py --force
```

如果你本地改过某些 skill，不建议直接 `--force` 覆盖。可以用 `--only` 只安装指定 skill。

## 开源前检查

发布到 GitHub 前建议检查：

- 阅读 `THIRD_PARTY_SKILLS.md`。
- 确认每个 vendored skill 都允许再分发。
- 删除私有笔记、token、credentials、本地数据和未公开敏感材料。
- 运行 `python scripts/validate_bundle.py`。
- 运行 `python scripts/install.py --dry-run`。
- 尽量在干净的 Codex home 中测试安装。
- 新开 Codex 会话，确认能看到 `research-paper-autopilot`。

## 常见问题

### Codex 没识别到 skill

先看 `scripts/install.py` 输出的 destination，应该指向 `.codex/skills`。安装后新开 Codex 会话。

### installer 显示 skipped

说明目标目录已经有同名 skill。要覆盖用 `--force`，或者用 `--skills-dir` 安装到其他目录。

### 我只想装主 skill

运行：

```bash
python scripts/install.py --only research-paper-autopilot
```

主 skill 单独也能查看和开发，但完整体验建议安装 supporting skills。

### autopilot 把我的项目 BLOCK 了

通常说明某个硬证据门没过。看 `audit/audit_report.json`、`PROGRESS.md` 和各阶段 plan。缺少文献、代码、结果、引用、日志或多智能体代码审查记录时，BLOCK 是正常结果。

### 代码审查门过不了

先生成 packet，再让六个必需角色独立审查。修复所有未解决 `BLOCK` 后，如果代码或结果变了，需要重新生成 packet 并更新 ledger。

### 终端里中文乱码

Markdown 文件是 UTF-8。若终端显示乱码，切换终端编码到 UTF-8，或用支持 UTF-8 的编辑器查看。

## 许可证和第三方说明

顶层 `LICENSE` 只覆盖本 bundle 中新写的文件。打包进来的 vendored skills 可能有各自的上游许可证或再分发条款。

公开发布前，请检查 `THIRD_PARTY_SKILLS.md`，确认你有权发布每个 bundled skill。
