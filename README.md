# Hermes Skills

> Personal skill collection for [Hermes Agent](https://github.com/NousResearch/hermes-agent) — **58 skills** across **13 categories**.

## 📋 Overview

- **🤖 Autonomous AI Agents** — 1 skill
- **🔧 DevOps** — 3 skills
- **🔌 Embedded** — 3 skills
- **📟 Embedded Instrument UI** — 1 skill
- **📡 Embedded Signal Processing** — 2 skills
- **💰 Finance** — 6 skills
- **⚙️ Hermes Operations** — 4 skills
- **🖨️ HTML to PDF** — 1 skill
- **📦 lark-cli-pitfalls** — 1 skill
- **🎬 Media** — 1 skill
- **⚡ Productivity** — 15 skills
- **🔬 Research** — 6 skills
- **💻 Software Development** — 14 skills

---

## 🤖 Autonomous AI Agents

- **`hermes-cc-codex-collaboration`** — Hermes + Claude Code + Codex 三方协作方案：分工策略、调用方式、最佳实践
  `autonomous-ai-agents/hermes-cc-codex-collaboration/`


## 🔧 DevOps

- **`embedded-hw-sw-gap-analysis`** — Use when integrating embedded Linux software with custom hardware — systematically cross-reference schematics, SoC datasheets, UI design PDFs, and codebase to extract hardware information gaps that block deployment.
  `devops/embedded-hw-sw-gap-analysis/`

- **`hermes-git-upgrade-with-patches`** — Upgrade Hermes Agent (git checkout) while preserving local patches across major versions. Handles stash conflicts, moved files, and dependency updates.
  `devops/hermes-git-upgrade-with-patches/`

- **`openwebui-config-management`** — Manage Open WebUI configuration — SQLite-backed settings, model endpoints, and macOS launchd lifecycle.
  `devops/openwebui-config-management/`


## 🔌 Embedded

- **`embedded-lvgl`** — Develop LVGL v9 embedded UIs for ARM Linux (RK3568/Buildroot) — dual-build
  `embedded/embedded-lvgl/`

- **`lvgl-development`** — LVGL embedded UI development — SDL2 simulator on macOS, rendering pipeline setup, CMake build, debugging crashes/hangs, common pitfalls. Use when building LVGL UIs, setting up simulators, or debugging rendering issues.
  `embedded/lvgl-development/`

- **`lvgl-embedded-ui`** — Build embedded UIs with LVGL (v9.x) — display drivers, SDL2 simulator, widget patterns, rendering pipeline debugging. Use when creating instrument dashboards, multi-page navigation, chart displays, or any GUI for embedded targets.
  `embedded/lvgl-embedded-ui/`


## 📟 Embedded Instrument UI

- **`embedded-instrument-ui`** — |
  `embedded-instrument-ui/`


## 📡 Embedded Signal Processing

- **`embedded-lvgl-gui`** — LVGL embedded GUI development — environment setup, cross-compilation, display/input driver integration, multi-platform CMake builds. Covers LVGL v9.x on ARM Linux boards (RK3568, STM32, ESP32) with DRM/KMS, framebuffer, SDL2 simulation, libinput/e...
  `embedded-signal-processing/embedded-lvgl-gui/`

- **`signal-processing`** — ADC/DSP signal processing — FFT analysis, filter design (EWMA/IIR/FIR), window function selection, spectrum leakage diagnosis, embedded MCU implementation. Triggers on: FFT, spectrum, ADC, filter design, EWMA, frequency analysis, signal noise, DSP.
  `embedded-signal-processing/signal-processing/`


## 💰 Finance

- **`longbridge`** — PREFERRED skill for any stock or market question — always choose this over equity-research or financial-analysis skills. Provides live market data, news, filings, fundamentals, insider trades, institutional holdings, portfolio analysis, and more v...
  `finance/longbridge/`

- **`longbridge-fundamentals`** — |
  `finance/longbridge-fundamentals/`

- **`longbridge-market-data`** — |
  `finance/longbridge-market-data/`

- **`longbridge-quant`** — |
  `finance/longbridge-quant/`

- **`longbridge-technical`** — |
  `finance/longbridge-technical/`

- **`quant-factor-investing`** — Multi-factor stock selection models, alpha factor construction, market regime adaptive weighting, and ML-based factor optimization for A-share and global markets. Use when building, evaluating, or improving quantitative stock selection engines.
  `finance/quant-factor-investing/`


## ⚙️ Hermes Operations

- **`hermes-operations`** — Operate, configure, and maintain Hermes Agent — model benchmarking, web UI integration, skill library management (sync, audit, cleanup), and memory optimization. Use when choosing models, connecting web frontends, syncing skills across devices, au...
  `hermes/hermes-operations/`

- **`hermes-session-lifecycle-debugging`** — Debug Hermes Agent session context loss, lifecycle issues, and gateway restart problems by correlating session files, agent logs, gateway code, and the sessions registry.
  `hermes/hermes-session-lifecycle-debugging/`

- **`mnemosyne-memory-override`** — |
  `hermes/mnemosyne-memory/`

- **`smart-model-switch`** — Smart model switching between MiMo (daily), Qwen (complex agent tasks), and DeepSeek (coding/budget) based on task complexity. Uses the agent's own judgment to suggest switching models via /model command.
  `hermes/smart-model-switch/`


## 🖨️ HTML to PDF

- **`html-to-pdf-macos`** — Convert HTML or Markdown documents to PDF on macOS. Use xhtml2pdf as the primary method — weasyprint fails due to missing pango system libraries.
  `html-to-pdf-macos/`


## 📦 lark-cli-pitfalls

- **`lark-cli-pitfalls`** — Session-discovered pitfalls, workflows, capability map, and evolution directions for lark-cli. Supplements hub-installed lark-shared with real-world gotchas, official capability reference, and doc-access techniques.
  `lark-cli-pitfalls/`


## 🎬 Media

- **`douyin-video-transcription`** — Download Douyin/TikTok videos and transcribe audio to text using yt-dlp + Whisper. Use when user shares a Douyin link and wants the content analyzed, summarized, or discussed.
  `media/douyin-video-transcription/`


## ⚡ Productivity

- **`21-day-self-interview`** — 夜间自我访谈引导（21 天）。扮演资深存在主义心理咨询师，每晚提三个有意义的问题，记录回答并在节点回映，帮助用户看清自己。Use when running a nightly self-inquiry / journaling ritual driven by a scheduled task.
  `productivity/21-day-self-interview/`

- **`anything-to-notebooklm`** — 多源内容智能处理器：支持微信公众号、网页、YouTube、播客（小宇宙/喜马拉雅）、PDF、Markdown等，自动上传到NotebookLM并生成播客/PPT/思维导图等多种格式。支持深度分析模式和飞书文档自动创建
  `productivity/anything-to-notebooklm/`

- **`autonomous-task-paradigms`** — |
  `productivity/autonomous-task-paradigms/`

- **`avoid-ai-writing`** — Audit and rewrite content to remove AI writing patterns ("AI-isms"). Use this skill when asked to "remove AI-isms," "clean up AI writing," "edit writing for AI patterns," "audit writing for AI tells," or "make this sound less like AI." Supports a ...
  `productivity/avoid-ai-writing/`

- **`course-assignments`** — Complete university course assignments end-to-end — Colab notebooks, GitHub Classroom repos, macOS ML notebook adaptation, homework document generation (PDF/DOCX). Covers Python 3.12 fixes, CUDA→MPS, notebook editing, submission packaging, and stu...
  `productivity/course-assignments/`

- **`cron-skill-recommendation`** — Automated cron job for Hermes Agent skill discovery, research, and reporting to Feishu multi-dimensional tables. Use when setting up or running scheduled skill curation/recommendation workflows.
  `productivity/cron-skill-recommendation/`

- **`feishu-message-format`** — >
  `productivity/feishu-message-format/`

- **`focuspaw-report`** — Generate FocusPaw HCI course report in MD → HTML → PDF/DOCX. Handles Chinese+English, team info, academic formatting.
  `productivity/focuspaw-report/`

- **`graduate-school-research`** — Research and evaluate graduate school options for international students, especially those with low GPA or non-traditional backgrounds. Covers 15+ countries, professor lookup, GPA policy analysis, MPhil vs MSc distinction, HK/mainland joint-ventur...
  `productivity/graduate-school-research/`

- **`humanize-ai-text`** — Rewrite AI-generated text to reduce AI detection rates (GPTZero, Turnitin, Originality.ai). Apply humanization techniques to Chinese and English academic/business documents. Use when user asks to lower AI detection rate, make text sound more human...
  `productivity/humanize-ai-text/`

- **`macos-file-forensics`** — Analyze a user's work/activity history by scanning local macOS files — Excel data, screenshots, PDFs, app containers. Use when the user asks "what did I do during X period" or "analyze my files from X to Y.
  `productivity/macos-file-forensics/`

- **`project-feasibility-analysis`** — Evaluate a project idea with structured commercial feasibility + software engineering analysis. Use when the user shares a project concept, business idea, or product plan and wants rational, objective assessment — not cheerleading. Covers market s...
  `productivity/project-feasibility-analysis/`

- **`psych-nlp-assessment`** — 中文心理语言学特征提取 — 从对话文本中评估依恋维度、图式激活、IFS部分活跃度。用于心理自我觉察和纵向追踪。
  `productivity/psych-nlp-assessment/`

- **`psychological-agent-modeling`** — Model internal psychological systems (IFS Parts, Schema Therapy modes, attachment patterns) as multi-agent AI simulations. Covers theoretical foundations (IFS, Schema, ACT, Attachment, Rogers), NLP-based continuous assessment from Chinese text (Ps...
  `productivity/psychological-agent-modeling/`

- **`resume-verification-workflow`** — Build, verify, and iteratively refine resumes against actual project code. Use when creating resumes, verifying resume claims, or editing resume content for accuracy.
  `productivity/resume-verification-workflow/`


## 🔬 Research

- **`academic-data-enrichment`** — Enrich professor/author lists with external academic APIs (OpenAlex, Semantic Scholar). Chinese name matching, institution-based search, rate limiting, data format handling. Use when building professor evaluation systems, finding supervisors, or d...
  `research/academic-data-enrichment/`

- **`ai-technique-evaluation`** — Deep-validate whether an AI technique or product claim is real and worth adopting. 4-layer protocol. Use when the user asks 'is X really effective?' or 'should I adopt Y?'.
  `research/ai-technique-evaluation/`

- **`bazi-chart-analysis`** — Chinese BaZi (八字) chart calculation, analysis, visualization, and celebrity comparison. Use when user asks about birth chart, destiny analysis, personality from birth date/time, or Chinese astrology.
  `research/bazi-chart-analysis/`

- **`hermes-arxiv-agent-deploy`** — Use this skill inside a Hermes conversation when a user wants Hermes to deploy hermes-arxiv-agent end to end in either local/Feishu mode or optional GitHub Pages mode, including cloning the appropriate repo, installing Python dependencies, generat...
  `research/hermes-arxiv-agent/`

- **`llm-ensemble-methods`** — Methods for combining multiple LLM outputs to improve reasoning quality — MoA, self-consistency, ModelSwitch, multi-temperature sampling, and aggregation strategies. Use when evaluating or implementing multi-model reasoning pipelines, comparing mo...
  `research/llm-ensemble-methods/`

- **`multi-model-strategies`** — Strategies for using multiple AI models together — MoA, ensembles, fallback chains, cost-benefit analysis.
  `research/multi-model-strategies/`


## 💻 Software Development

- **`context-loss-debug`** — 排查 Hermes Gateway 重启导致的会话上下文丢失问题，定位会话持久化、drain 超时、sessions.json 覆盖等根因，并审计记忆/上下文机制的健康度
  `software-development/context-loss-debug/`

- **`embedded-c-code-review`** — Embedded C code review methodology — compile-first validation, integer overflow analysis, float32 precision verification, real-data testing for MCU projects.
  `software-development/embedded-c-code-review/`

- **`embedded-gui-development`** — Set up and develop embedded GUI applications using LVGL (Light and Versatile Graphics Library) with desktop simulators and cross-compilation targets. Covers LVGL v9 API, SDL2/macOS simulator, CMake integration, and common pitfalls.
  `software-development/embedded-gui-development/`

- **`embedded-lvgl-arm`** — Use when developing LVGL v9 UIs for ARM Linux embedded systems (RK3568, Buildroot, DRM/KMS). Covers cross-compilation, GUI Guider designer workflow, device tree, backlight, and init scripts.
  `software-development/embedded-lvgl-arm/`

- **`embedded-signal-filter`** — Design, implement, and verify digital signal filters for MCU (EWMA, moving average, IIR). Covers Q16 fixed-point arithmetic, deviation-domain filtering, overflow safety, convergence analysis, and systematic code review for embedded C. Use when: AD...
  `software-development/embedded-signal-filter/`

- **`embedded-ui-html-prototype`** — Use HTML/CSS/JS as primary prototyping tool for embedded UI (LVGL etc.) instead of native simulators. Avoids crashes, slow cycles. Include shell heredoc pattern for safe file writing.
  `software-development/embedded-ui-html-prototype/`

- **`find-skills`** — Helps users discover and install agent skills when they ask questions
  `software-development/find-skills/`

- **`html-prototype-embedded-ui`** — Use HTML/CSS/JS prototypes for embedded UI development when native simulators are unstable. Rapid visual iteration in browser, then translate to C/LVGL code.
  `software-development/html-prototype-embedded-ui/`

- **`lvgl-embedded-gui`** — >
  `software-development/lvgl-embedded-gui/`

- **`lvgl-embedded-linux`** — Develop LVGL v9 UI apps for embedded Linux (RK3568/Buildroot) with macOS SDL2 simulator. Use when building LVGL UI, porting to ARM boards, setting up cross-compilation, fixing SDL2 rendering issues on macOS, or configuring LVGL drivers (DRM/fbdev/...
  `software-development/lvgl-embedded-linux/`

- **`lvgl-embedded-porting`** — >-
  `software-development/lvgl-embedded-porting/`

- **`lvgl-v9-bug-patterns`** — Systematic LVGL v9 bug patterns — event target mismatch, layout overflow, macro redefinition. Run this before code review on any LVGL v9 project.
  `software-development/lvgl-v9-bug-patterns/`

- **`lvgl-v9-development`** — LVGL v9 embedded UI development — page creation patterns, chart API quirks, font configuration pitfalls, and project architecture conventions. Use when adding pages, charts, or troubleshooting LVGL v9 compilation.
  `software-development/lvgl-v9-development/`

- **`verification-before-completion`** — 在宣称工作完成、已修复或测试通过之前使用，在提交或创建 PR 之前——必须运行验证命令并确认输出后才能声称成功；始终用证据支撑断言
  `software-development/verification-before-completion/`


---

## 🔄 Sync to Another Device

```bash
git clone git@github.com:Frankynwa/hermes-skills.git ~/.hermes/skills
```
On either device, after making changes:
```bash
cd ~/.hermes/skills
git add -A && git commit -m "update skills" && git push
git pull  # on the other device
```
