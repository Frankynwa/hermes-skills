# Hermes Skills

> Personal, curated skill collection for [Hermes Agent](https://github.com/NousResearch/hermes-agent) — **9 skills** across **6 categories**, each born from real-world usage.
>
> Part of the [Hermes Agent Skills ecosystem](https://hermes-agent.nousresearch.com/docs/skills) · Topics: `hermes-agent` `skills` `lvgl` `embedded-systems` `automation`

**What this is:** A hand-picked set of Hermes skills that were actually built and battle-tested — not a comprehensive marketplace. Every skill here solved a real problem: debugging session lifecycle issues, cross-compiling LVGL for ARM boards, syncing skills across devices, working around lark-cli limitations, etc.

**What this is not:** A 100+ skill dump. Those existed briefly in the initial commit, then got aggressively pruned down to what actually matters.

---

## Skills Index

| # | Skill | Category | Tags |
|---|-------|----------|------|
| 1 | hermes-operations | Hermes Ops | benchmarking, web-ui, skills, maintenance |
| 2 | session-lifecycle-debugging | Hermes Ops | debugging, session, gateway, context-loss |
| 3 | smart-model-switch | Hermes Ops | model, cost-optimization, qwen, deepseek |
| 4 | embedded-lvgl-arm | Embedded | lvgl, arm, linux, buildroot, rk3568, gui-guider |
| 5 | lvgl-embedded-linux | Embedded | lvgl, sdl2, drm, cross-compile |
| 6 | embedded-hw-sw-gap-analysis | DevOps | hardware, gap-analysis, device-tree, schematics |
| 7 | cron-skill-recommendation | Productivity | cron, feishu, automation, recommendation |
| 8 | lark-cli-pitfalls | Productivity | lark, feishu, pitfalls, bitable, identity |
| 9 | html-to-pdf-macos | Productivity | pdf, html, macos, xhtml2pdf |

---

## Sync to Another Device

```bash
git clone git@github.com:Frankynwa/hermes-skills.git ~/.hermes/skills
```

On either device, after making changes:

```bash
cd ~/.hermes/skills
git add -A && git commit -m "update skills" && git push
git pull  # on the other device
```

---

## Contributing

These skills are personal and tailored to specific workflows. If you find one useful, feel free to fork or adapt — MIT licensed unless otherwise noted.
