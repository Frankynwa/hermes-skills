# Hermes Skills

> Personal, curated skill collection for [Hermes Agent](https://github.com/NousResearch/hermes-agent) — **9 skills** across **6 categories**, each born from real-world usage.

**What this is:** A hand-picked set of Hermes skills that were actually built and battle-tested in production — not a comprehensive marketplace. Every skill here solved a real problem: debugging session lifecycle issues, cross-compiling LVGL for ARM boards, syncing skills across devices, working around lark-cli limitations, etc.

**What this is not:** A 100+ skill dump. Those existed briefly in the initial commit, then got aggressively pruned down to what actually matters.

---

## Skills by Category

| Category | Skills | Description |
|---|---|---|
| Hermes Operations | 3 | hermes-operations, session-lifecycle-debugging, smart-model-switch |
| Software Development | 2 | embedded-lvgl-arm, lvgl-embedded-linux |
| DevOps | 1 | embedded-hw-sw-gap-analysis |
| Productivity | 1 | cron-skill-recommendation |
| lark-cli | 1 | lark-cli-pitfalls |
| HTML to PDF | 1 | html-to-pdf-macos |

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
