---
name: resume-verification-workflow
category: productivity
description: Build, verify, and iteratively refine resumes against actual project code. Use when creating resumes, verifying resume claims, or editing resume content for accuracy.
---

# Resume Building & Code Verification Workflow

## Trigger
User asks to create, verify, edit, or optimize a resume/CV. Also triggers when user asks "is this accurate" about project descriptions.

## Workflow

### Phase 1: Gather Context
1. Ask for or read the existing resume
2. Ask what projects/experiences to include
3. Ask for specific details the user wants emphasized

### Phase 2: Verify Against Code (CRITICAL)
**When the user says "I built this with you" or "you did this":**

1. **Search COMPREHENSIVELY** — use `find ~ -maxdepth 6 -name "*.py" -exec grep -l "keyword" {} \;` across the ENTIRE home directory
2. **Check ALL possible locations:**
   - `~/projects/`
   - `~/Desktop/`
   - `~/Documents/`
   - `~/course-project-*/` (course projects often live at home root)
   - `~/.trae-cn/worktrees/` (Trae IDE worktrees)
   - `~/Downloads/`
3. **NEVER stop at the first location found** — the user may have multiple versions/branches
4. **Read the actual code** — don't trust session memory or previous descriptions

**PITFALL: Do NOT search Trae worktrees when user explicitly says "不用找trae了". Respect location exclusions.**

### Phase 3: Write Accurate Descriptions
For each project, map claims to actual code:

| Claim | Evidence Required |
|-------|-------------------|
| N-layer system | Count actual layers in code |
| N-level signals | Count actual levels |
| Specific data sources | grep for API endpoints/imports |
| Caching architecture | grep for cache/TTL patterns |
| Performance numbers | Find backtest output files |
| Frontend tech | Check package.json / actual framework |

**PITFALL: Do NOT write aspirational descriptions. If the code shows 5 levels but you wrote "six-level", fix it. If there's no stop-loss code, don't claim stop-loss functionality.**

### Phase 4: Iterate
- Generate PDF (Chrome headless for Chinese: `--headless --print-to-pdf --no-margins --no-pdf-header-footer`)
- Send via `lark-cli im +messages-send --user-id <id> --as bot --file ./resume.pdf`
- User reviews → corrections → regenerate

## Key Corrections from User
- **"回测成果就不要讲了，容易露出破绽"** — Don't include specific performance numbers that could be questioned in interviews unless 100% verifiable
- **User names their own role descriptions** — Use their exact wording for internship duties, don't invent
- **"正在进行中"** — Mark in-progress projects clearly
- **Course curriculum** — Add relevant coursework that connects to project experience (creates logical coherence)

## PDF Generation (macOS)
```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu \
  --print-to-pdf="/path/to/output.pdf" \
  --no-margins --no-pdf-header-footer \
  "file:///path/to/input.html"
```

## Feishu Delivery
```bash
cd /path/to/dir && lark-cli im +messages-send \
  --user-id <open_id> --as bot --file ./resume.pdf
```
Note: `--file` requires relative path, so `cd` to the directory first.

## Pitfalls
1. **Code may be in unexpected locations** — `~/course-project-X/` not `~/Documents/`
2. **Multiple versions exist** — Trae worktree, Documents, Desktop may all have different versions
3. **"Resource deadlock avoided"** on macOS — files with `@` extended attributes can't be read with `cat`. Use `perl -pe ''` as workaround, or find the GitHub repo
4. **Don't over-package** — resume descriptions should match what code actually does, not what was planned
5. **Respect user corrections immediately** — when user says "不是这个" about a description, fix it without arguing
