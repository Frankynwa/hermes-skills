# Hermes Skills

> Personal skill collection for [Hermes Agent](https://github.com/NousResearch/hermes-agent) — **9 skills** across **6 categories**.

## 📋 Overview

- **🔧 DevOps** — 1 skill
- **⚙️ Hermes Operations** — 3 skills
- **🖨️ HTML to PDF** — 1 skill
- **📦 lark-cli-pitfalls** — 1 skill
- **⚡ Productivity** — 1 skill
- **💻 Software Development** — 2 skills

---

## 🔧 DevOps

- **`embedded-hw-sw-gap-analysis`** — Use when integrating embedded Linux software with custom hardware — systematically cross-reference schematics, SoC datasheets, UI design PDFs, and codebase to extract hardware information gaps that block deployment.
  `devops/embedded-hw-sw-gap-analysis/`


## ⚙️ Hermes Operations

- **`hermes-operations`** — Operate, configure, and maintain Hermes Agent — model benchmarking, web UI integration, skill library management (sync, audit, cleanup), and memory optimization. Use when choosing models, connecting web frontends, syncing skills across devices, au...
  `hermes/hermes-operations/`

- **`hermes-session-lifecycle-debugging`** — Debug Hermes Agent session context loss, lifecycle issues, and gateway restart problems by correlating session files, agent logs, gateway code, and the sessions registry.
  `hermes/hermes-session-lifecycle-debugging/`

- **`smart-model-switch`** — Smart model switching between MiMo (daily), Qwen (complex agent tasks), and DeepSeek (coding/budget) based on task complexity. Uses the agent's own judgment to suggest switching models via /model command.
  `hermes/smart-model-switch/`


## 🖨️ HTML to PDF

- **`html-to-pdf-macos`** — Convert HTML or Markdown documents to PDF on macOS. Use xhtml2pdf as the primary method — weasyprint fails due to missing pango system libraries.
  `html-to-pdf-macos/`


## 📦 lark-cli-pitfalls

- **`lark-cli-pitfalls`** — Session-discovered pitfalls, workflows, capability map, and evolution directions for lark-cli. Supplements hub-installed lark-shared with real-world gotchas, official capability reference, and doc-access techniques.
  `lark-cli-pitfalls/`


## ⚡ Productivity

- **`cron-skill-recommendation`** — Automated cron job for Hermes Agent skill discovery, research, and reporting to Feishu multi-dimensional tables. Use when setting up or running scheduled skill curation/recommendation workflows.
  `productivity/cron-skill-recommendation/`


## 💻 Software Development

- **`embedded-lvgl-arm`** — Use when developing LVGL v9 UIs for ARM Linux embedded systems (RK3568, Buildroot, DRM/KMS). Covers cross-compilation, GUI Guider designer workflow, device tree, backlight, and init scripts.
  `software-development/embedded-lvgl-arm/`

- **`lvgl-embedded-linux`** — Develop LVGL v9 UI apps for embedded Linux (RK3568/Buildroot) with macOS SDL2 simulator. Use when building LVGL UI, porting to ARM boards, setting up cross-compilation, fixing SDL2 rendering issues on macOS, or configuring LVGL drivers (DRM/fbdev/...
  `software-development/lvgl-embedded-linux/`


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
