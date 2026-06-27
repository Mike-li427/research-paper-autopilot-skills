# 内置 Skill 清单与地址

本文件列出当前仓库打包的 58 个 Codex skill。每个 skill 都可以在 `skills/<skill-directory>/` 下查看源码，也可以通过表格里的 GitHub 地址直接打开。

仓库地址：[https://github.com/Mike-li427/research-paper-autopilot-skills](https://github.com/Mike-li427/research-paper-autopilot-skills)

## 第三方与署名说明

这个清单是 inventory，不是原创归属声明。本仓库把多个已有的本地/community/第三方 Codex skills 打包到一起，方便克隆后直接安装使用。除顶层文档、安装/校验脚本、manifest、plugin metadata 和本地 `research-paper-autopilot` 总控加固文件外，supporting skills 可能有各自的上游作者、许可证和再分发要求。

使用或二次分发前，请同时查看：

- `THIRD_PARTY_SKILLS.md`
- 各 skill 目录内可能存在的 `LICENSE`、`NOTICE`、`README` 或 attribution 文件

## 快速安装

安装全部 skill：

```bash
python scripts/install.py
```

只安装某一个 skill：

```bash
python scripts/install.py --only research-paper-autopilot
```

只安装多个指定 skill：

```bash
python scripts/install.py --only research-paper-autopilot deep-research academic-paper citation-check-skill
```

## Skill 索引

| 类别 | Skill | 作用 | 仓库路径 | GitHub 地址 |
|---|---|---|---|---|
| 总控 | `research-paper-autopilot` | 从研究 idea 到可审计论文项目包的总控编排；负责阶段状态机、赛道路由、证据门、实验代码、审稿模拟、修订、完整性审计和投稿材料。 | `skills/research-paper-autopilot/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/research-paper-autopilot) |
| 通用科研流程 | `academic-pipeline` | 通用科研流水线编排：research -> write -> integrity check -> review -> revise -> finalize。 | `skills/academic-pipeline/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/academic-pipeline) |
| 通用科研流程 | `deep-research` | 多智能体深度研究流程，用于系统调研、快速 brief、事实核查、文献综述和系统综述。 | `skills/deep-research/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/deep-research) |
| 论文写作 | `academic-paper` | 12-agent 学术论文写作 pipeline，覆盖计划、提纲、初稿、修订、摘要、文献综述、引用检查和 disclosure。 | `skills/academic-paper/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/academic-paper) |
| 论文审稿 | `academic-paper-reviewer` | 多视角论文审稿模拟，包含主编、领域审稿人、方法审稿人和反方审稿视角。 | `skills/academic-paper-reviewer/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/academic-paper-reviewer) |
| 通用科研套件 | `academic-research-suite` | 综合型 academic research suite，内含深度研究、论文写作、审稿、引用检查和流程工具。 | `skills/academic-research-suite/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/academic-research-suite) |
| 自动论文项目 | `automated-research-paper` | 证据驱动的自动论文项目 scaffold 和 pipeline，用于从 idea 建立可复现论文工作区。 | `skills/automated-research-paper/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/automated-research-paper) |
| 文献与选题 | `literature-review` | 文献综述、相关工作、survey outline、paper landscape、gap 分析和 citation-backed synthesis。 | `skills/literature-review/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/literature-review) |
| 文献与选题 | `survey` | 文献 survey 助手，覆盖目标澄清、方向 triage、结构化阅读和综述整合。 | `skills/literature-survey-skill/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/literature-survey-skill) |
| 文献与选题 | `research-gap-analysis` | 多篇论文对比、综合和 gap 提炼，用于找未解决问题、研究机会和后续方向。 | `skills/research-gap-analysis/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/research-gap-analysis) |
| 文献与选题 | `scientific-brainstorming` | 科研选题头脑风暴、研究问题生成、假设细化、项目 framing 和 novelty 分析。 | `skills/scientific-brainstorming/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/scientific-brainstorming) |
| 图表与分析 | `scientific-visualization` | 科学图表策略、publication-quality plots、多 panel figure 规划、视觉编码和图表审计。 | `skills/scientific-visualization/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/scientific-visualization) |
| 统计与结果 | `statistical-analysis` | 统计分析规划、检验选择、模型解释、power analysis、可复现分析脚本和数量 claim 检查。 | `skills/statistical-analysis/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/statistical-analysis) |
| 证据核查 | `citation-check-skill` | 通过检索和视觉核查验证引用、PDF、报告、图片、图表和线上权威来源是否一致。 | `skills/citation-check-skill/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/citation-check-skill) |
| CCF/AI | `ccf-common` | CCF/AI 系列 skill 的共享治理层，包含路由、触发、artifact contract、隐私和证据规则。 | `skills/ccf-common/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/ccf-common) |
| CCF/AI | `ccf-experiment-designer` | CCF/AI 论文实验设计：数据集、baseline、metric、ablation、robustness、结果表和图表计划。 | `skills/ccf-experiment-designer/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/ccf-experiment-designer) |
| CCF/AI | `ccf-idea-optimizer` | 把粗糙 CCF/AI 方向优化为具体 problem、gap、insight、method、novelty 和 evidence plan。 | `skills/ccf-idea-optimizer/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/ccf-idea-optimizer) |
| CCF/AI | `ccf-idea-reviewer` | 严格评估、打分、排序和 triage 早期 CCF/AI idea，关注 prior art、venue fit 和风险。 | `skills/ccf-idea-reviewer/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/ccf-idea-reviewer) |
| CCF/AI | `ccf-integrity-auditor` | 审计 CCF/AI 论文完整性：claim-support、result-to-claim、数字一致性、引用和图表一致性。 | `skills/ccf-integrity-auditor/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/ccf-integrity-auditor) |
| CCF/AI | `ccf-literature-monitor` | 监控 arXiv、OpenReview、会议动态、实验室项目和竞争论文，跟踪 idea 重合与趋势变化。 | `skills/ccf-literature-monitor/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/ccf-literature-monitor) |
| CCF/AI | `ccf-literature-searcher` | CCF/AI 文献检索、相关工作、prior art、benchmark、dataset 和 research opportunity map。 | `skills/ccf-literature-searcher/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/ccf-literature-searcher) |
| CCF/AI | `ccf-paper-reviewer` | CCF/AI 论文端到端审稿模拟：novelty、soundness、evidence、AC/meta-review、分数风险和修订建议。 | `skills/ccf-paper-reviewer/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/ccf-paper-reviewer) |
| CCF/AI | `ccf-paper-to-exemplar` | 把给定会议论文 PDF 提炼成写作 exemplar cards，供 CCF paper writer 学习结构和表达模式。 | `skills/ccf-paper-to-exemplar/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/ccf-paper-to-exemplar) |
| CCF/AI | `ccf-paper-writer` | CCF/AI 论文正文规划、起草、修改、润色和压缩，覆盖 abstract、intro、related work、method、experiment。 | `skills/ccf-paper-writer/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/ccf-paper-writer) |
| CCF/AI | `ccf-pipeline-orchestrator` | CCF/AI 项目流程编排：阶段、目标、约束、gate、artifact、handoff 和 ccfa.yaml 状态。 | `skills/ccf-pipeline-orchestrator/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/ccf-pipeline-orchestrator) |
| CCF/AI | `ccf-project-scaffolder` | 创建 CCF/AI 论文项目目录、模板、ccfa.yaml 和 artifact 结构，不生成研究内容。 | `skills/ccf-project-scaffolder/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/ccf-project-scaffolder) |
| CCF/AI | `ccf-rebuttal-writer` | CCF/AI rebuttal、author response、reviewer-comment ledger、revision summary 和 resubmission plan。 | `skills/ccf-rebuttal-writer/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/ccf-rebuttal-writer) |
| CCF/AI | `ccf-submission-checker` | CCF/AI 投稿前检查：模板、匿名、PDF build、metadata、supplementary、artifact、代码/数据发布和 licenses。 | `skills/ccf-submission-checker/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/ccf-submission-checker) |
| Nature/SCI | `nature-academic-search` | Nature/SCI 风格学术检索、文献来源管理、检索策略和引用文件处理。 | `skills/nature-academic-search/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/nature-academic-search) |
| Nature/SCI | `nature-citation` | 为 Nature/CNS 风格正文补充严格 citation support，按 claim 切分并核查引用支撑。 | `skills/nature-citation/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/nature-citation) |
| Nature/SCI | `nature-data` | Nature-ready Data Availability、数据仓库计划、dataset citation、FAIR metadata 和数据可用性审计。 | `skills/nature-data/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/nature-data) |
| Nature/SCI | `nature-figure` | Nature/high-impact journal 图表 workflow：图表设计、代码生成、审计、润色和 submission-grade 输出。 | `skills/nature-figure/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/nature-figure) |
| Nature/SCI | `nature-polishing` | 将学术英文润色、重构或中译英为 Nature/Nature Communications 倾向表达，强调结构和语气。 | `skills/nature-polishing/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/nature-polishing) |
| Nature/SCI | `nature-reader` | 从 PDF、DOI、arXiv、HTML 或粘贴文本生成中英对照、图表感知、source-grounded 的论文阅读材料。 | `skills/nature-reader/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/nature-reader) |
| Nature/SCI | `nature-response` | Nature-family 审稿回复信、point-by-point response、修订说明和 response audit。 | `skills/nature-response/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/nature-response) |
| Nature/SCI | `nature-reviewer` | 模拟 Nature-style reviewer，从审稿人角度评估 novelty、evidence、scope、figure 和缺陷。 | `skills/nature-reviewer/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/nature-reviewer) |
| Nature/SCI | `nature-writing` | Nature-style manuscript sections 起草、重构和规划，覆盖 abstract、intro、related work、method、experiments 等。 | `skills/nature-writing/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/nature-writing) |
| PaperSpine | `paper-spine` | PaperSpine 主入口：端到端写作、重写或组装 paper/report，并输出 LaTeX、PDF 或 Word。 | `skills/paper-spine/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/paper-spine) |
| PaperSpine | `paper-spine-audit` | PaperSpine 内部审计：检查缺失 artifact、浅层修订、逻辑迁移、unsupported claim 和翻译覆盖。 | `skills/paper-spine-audit/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/paper-spine-audit) |
| PaperSpine | `paper-spine-build` | PaperSpine 内部 build 步骤：基于材料、motivation 和 rationale workflow 构建 paper/report。 | `skills/paper-spine-build/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/paper-spine-build) |
| PaperSpine | `paper-spine-citation` | PaperSpine 内部 citation bank：为 intro、discussion 和背景 claim 建立引用支撑库。 | `skills/paper-spine-citation/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/paper-spine-citation) |
| PaperSpine | `paper-spine-intake` | PaperSpine 内部 intake：收集 workflow 选项并写入 flash/pro、scene、language 和 input 配置。 | `skills/paper-spine-intake/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/paper-spine-intake) |
| PaperSpine | `paper-spine-latex` | PaperSpine 内部 LaTeX 组装：图表位置、citation、label 和 compile-safe cleanup。 | `skills/paper-spine-latex/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/paper-spine-latex) |
| PaperSpine | `paper-spine-research` | PaperSpine 内部 research：研究目标要求、下载参考材料、学习优秀范例和准备 motivation options。 | `skills/paper-spine-research/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/paper-spine-research) |
| PaperSpine | `paper-spine-rewrite` | PaperSpine 内部 rewrite：基于已确认 motivation、research、段落 rationale 和证据重写稿件。 | `skills/paper-spine-rewrite/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/paper-spine-rewrite) |
| PaperSpine | `paper-spine-translate` | PaperSpine 内部 translation：生成 `translation_zh/`，包含逐行翻译和全文翻译。 | `skills/paper-spine-translate/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/paper-spine-translate) |
| PaperSpine | `paper-spine-update` | PaperSpine 更新工具：检查并从 GitHub 更新 PaperSpine，同时保留全局配置。 | `skills/paper-spine-update/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/paper-spine-update) |
| 论文写作 | `paper-writing` | 基于 Arpit Gupta 写作原则的论文写作助手，用于 section drafting、revision、clarity 和 voice control。 | `skills/paper-writing-skill/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/paper-writing-skill) |
| 单篇论文讲解 | `paper-beamer-deck` | 针对单篇论文生成 LaTeX Beamer 教学/讲解材料、提纲和质量检查工具。 | `skills/paper-beamer-deck/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/paper-beamer-deck) |
| 图示生成 | `paperbanana` | 根据论文方法描述生成 publication-quality academic diagrams。 | `skills/PaperBanana/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/PaperBanana) |
| 文献库/RAG | `papi` | 与本地 paper database 交互：列论文、搜索内容、查看详情、添加论文和导出上下文。 | `skills/papi/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/papi) |
| 文献库/RAG | `papi-ask` | 基于 paper database/RAG 对论文提问，生成带引用的综合回答。 | `skills/papi-ask/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/papi-ask) |
| 文献库/RAG | `papi-compare` | 比较多篇论文、方法或算法，辅助选择引用、技术路线或实现方案。 | `skills/papi-compare/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/papi-compare) |
| 文献库/RAG | `papi-curate` | 从论文创建项目笔记、实现笔记或研究摘要，便于沉淀到项目文档。 | `skills/papi-curate/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/papi-curate) |
| 文献库/RAG | `papi-ground` | 用论文原文片段和 citation grounding 回答问题，降低对论文内容的幻觉风险。 | `skills/papi-ground/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/papi-ground) |
| 文献库/RAG | `papi-init` | 初始化 paperpipe agent integration，把 papi 支持接入项目 AGENTS/CLAUDE 文档。 | `skills/papi-init/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/papi-init) |
| 文献库/RAG | `papi-verify` | 对照论文检查代码实现，适合验证公式、算法和实验实现是否贴合原文。 | `skills/papi-verify/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/papi-verify) |
| 文件处理 | `pdf` | PDF 阅读、创建、检查、渲染和布局验证，适合科研 PDF 产物处理。 | `skills/pdf/` | [打开](https://github.com/Mike-li427/research-paper-autopilot-skills/tree/main/skills/pdf) |

## 机器可读清单

如果需要脚本读取，请使用：

- `skills_manifest.json`：机器可读 manifest，包含目录名、skill name、简介、文件数和大小。
- `THIRD_PARTY_SKILLS.md`：第三方来源和再分发注意事项。
