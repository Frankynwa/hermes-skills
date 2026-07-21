---
name: hermes-arxiv-agent-deploy
description: Use this skill inside a Hermes conversation when a user wants Hermes to deploy hermes-arxiv-agent end to end in either local/Feishu mode or optional GitHub Pages mode, including cloning the appropriate repo, installing Python dependencies, generating the correct cron prompt, and creating a daily cron job.
---

# Hermes Arxiv Agent Deploy

This skill is for deployment and maintenance of `hermes-arxiv-agent` in two deployment modes.

This skill is only meant to be used inside Hermes. Do not add Hermes installation checks or Hermes bootstrap guidance here.

Use it when the user wants any of the following:

- install the project from GitHub
- set up or repair the daily arXiv monitoring cron job
- initialize a new machine for this project
- re-create the cron prompt with the correct local path
- choose between local-only usage and GitHub Pages publishing

The repository defaults to monitoring quantization-related papers. If the user wants a different research topic, update `search_keywords.txt` during deployment.

Do not assume the current local folder name matches the remote repository name. Treat the GitHub repository name `hermes-arxiv-agent` as canonical for clone and deployment instructions.

## Deployment Modes

Choose the mode from the user's installation phrase, not from vague interpretation.

Use these rules:

- if the user explicitly says `按本地/飞书模式部署` or `不要配置 GitHub Pages 发布`, use Local / Feishu mode
- if the user explicitly says `按 GitHub Pages publishing 模式部署`, use GitHub Pages mode
- if neither phrase is present, default to Local / Feishu mode

### Mode A: Local / Feishu only

Use this when the user only wants:

- local files and Excel records
- daily Feishu/Lark push
- optional local browser viewing

In this mode:

- cloning the upstream public repository is fine
- fork is not required
- GitHub write access is not required
- the generated cron prompt must come from `cronjob_prompt.txt`
- the cron job must not publish to GitHub Pages

### Mode B: GitHub Pages publishing

Use this only when the user explicitly uses the GitHub Pages publishing installation phrase.

In this mode:

- the user must first fork the repository to their own GitHub account
- the local checkout must point to the user's own fork, not the upstream repository
- SSH is strongly preferred for Git pushes
- the generated cron prompt must come from `cronjob_prompt.pages.txt`
- the cron job must include the static-site publish step

If the user asks for GitHub Pages mode but has not provided or created a fork, stop and tell them to fork first.

When GitHub Pages mode is requested, the skill URL itself should normally come from the user's own fork, for example:

```text
https://github.com/<user-or-org>/hermes-arxiv-agent/blob/main/AGENT_SKILL.md
```

## Deployment Goal

Bring the user to a working state where:

1. Feishu/Lark gateway is configured.
2. The correct repo is cloned locally for the chosen mode.
3. Python dependencies are installed.
4. `cronjob_prompt.generated.txt` exists and points to the real local project directory.
5. A Hermes cron job exists, points to the real local project directory, and delivers back to the Feishu/Lark chat instead of `local`.

Because this skill runs inside Hermes, Hermes itself is already present by assumption.
If Feishu is not configured, that is a deploy-time prerequisite to surface, not a reason to discuss Hermes installation.

## Required Workflow

Follow this order unless the user explicitly asks for a partial action.

### 1. Verify prerequisites

Check:

- Python 3 is available
- `pip` or `pip3` is available

If the user chose GitHub Pages mode, also check:

- GitHub SSH authentication is available for their fork remote
- the fork repository exists and is writable by the user

If Feishu/Lark is not configured, direct the user to run:

```bash
hermes gateway setup
```

The cron job for this repository should be created from a Feishu/Lark Hermes conversation, not from a local CLI-only chat.
For this project, the intended delivery target is Feishu/Lark.

When creating or repairing the cron job, ensure its delivery is set to `feishu` rather than `local`.

### 2. Clone or locate the repository

Preferred defaults:

For local / Feishu mode:

```bash
git clone https://github.com/genggng/hermes-arxiv-agent.git
cd hermes-arxiv-agent
```

For GitHub Pages mode:

```bash
git clone git@github.com:<user-or-org>/hermes-arxiv-agent.git
cd hermes-arxiv-agent
```

If the repository already exists locally, reuse it instead of recloning.

If the user chose GitHub Pages mode, ensure the effective push remote points to the user's own fork, not the upstream repository.

If the existing repository uses HTTPS but should push to the user's fork, change it to:

```bash
git remote set-url origin git@github.com:<user-or-org>/hermes-arxiv-agent.git
```

The effective project directory must be captured as an absolute path and reused in later steps. Refer to it as `PROJECT_DIR`.

### 3. Install runtime dependencies

Run inside `PROJECT_DIR`:

```bash
pip install openpyxl requests pdfplumber
```

If the environment uses `pip3`, use that instead.

Also note the repository default search scope:

- the default query in `search_keywords.txt` targets quantization-related LLM papers
- if the user wants another topic, edit `search_keywords.txt` before the first scheduled run

### 4. Run the deployment preparation script

Run this script inside the checked-out repository:

```bash
bash prepare_deploy.sh
```

For GitHub Pages mode, run:

```bash
DEPLOY_MODE=pages bash prepare_deploy.sh
```

The script uses one deployment variable:

- `PROJECT_DIR`
- `DEPLOY_MODE` with valid values `local` or `pages`

If `PROJECT_DIR` is not supplied, the script uses its own directory as the project root. That is the preferred path, because it avoids manual mistakes after clone.

The script is responsible for:

- reading the correct cron prompt template for the chosen mode
- generating `cronjob_prompt.generated.txt` with placeholder paths replaced
- removing the human-only path reminder from `cronjob_prompt.generated.txt`
- keeping the cron prompt aligned with the requirement to rebuild `viewer/papers_data.json` after Excel is updated
- recording the chosen deployment mode in `.deploy_mode`

If the user wants manual override, run:

```bash
PROJECT_DIR=/absolute/path/to/hermes-arxiv-agent DEPLOY_MODE=pages bash prepare_deploy.sh
```

### 5. Understand the current path constraint

The repository code now resolves its own paths relative to the checked-out project directory, but the Hermes cron prompt still needs the real absolute checkout path.

This means:

- do not leave placeholder paths such as `/path/to/hermes-arxiv-agent`
- always finish cron prompt generation before creating the cron job

### 6. Use the generated cron prompt as the cron payload

After step 4:

- the selected template remains the repository source of truth
- `cronjob_prompt.generated.txt` contains the real project path and no longer contains the human-only path-replacement reminder

Use the full current contents of `cronjob_prompt.generated.txt` as the exact `<prompt>` payload for:

```text
/cron add <prompt>
```

Do not rewrite the prompt from memory. Read it from the patched file and use it directly.
This is a Hermes chat slash command, not a bash command.
Do not try to execute `/cron add` through `bash`, `sh`, or `subprocess`.

Verify the generated file now references paths under `PROJECT_DIR`, for example:

- `PROJECT_DIR/new_papers.json`
- `PROJECT_DIR/papers_record.xlsx`
- `PROJECT_DIR/monitor.py`

### 7. Create the cron job

Create the job inside the Feishu/Lark Hermes conversation using the standard slash-command form with the exact current contents of `cronjob_prompt.generated.txt`.

Delivery must be `feishu`, so the final cron output is pushed to Feishu/Lark rather than being saved only as `local`.

If the current job was previously created with delivery `local`, recreate it or edit it so the effective delivery target becomes `feishu`.

After creation, confirm:

- prompt contains the real absolute path
- the job is listed in `/cron list`
- the business instructions from `cronjob_prompt.txt` were preserved exactly in `cronjob_prompt.generated.txt`
- delivery is not `local`
- delivery is set to `feishu`

## Agent Behavior Rules

- Prefer automation over asking the user to hand-edit prompt text.
- Do not ask the user to rename their local directory.
- Keep the repository name `hermes-arxiv-agent` in clone instructions and user-facing descriptions.
- If local folder names differ, adapt by substituting the actual absolute path rather than forcing a rename.
- When reconfiguring cron, rerun `prepare_deploy.sh` and then reuse `cronjob_prompt.generated.txt`.
- Prefer `prepare_deploy.sh` over ad hoc manual edits, because it centralizes all known path fixes behind one variable.
- Do not paraphrase or simplify the substantive task instructions from `cronjob_prompt.txt`.
- Treat the selected prompt template as the source of truth and `cronjob_prompt.generated.txt` as the deployable cron payload.
- Treat `/cron add` and `/cron list` as Hermes chat commands, not shell commands.
- Treat Feishu/Lark delivery as required for this project; set the cron delivery target to `feishu` and do not leave the job on `local`.
- Keep repository code path handling relative; do not reintroduce machine-specific absolute paths into tracked files.
- In GitHub Pages mode, prefer an SSH Git remote that points to the user's own fork.
- Do not configure scheduled publishing against the upstream public repository unless the user explicitly owns and intends to publish from it.

## Path Handling Guidance

The remaining deployment-specific path lives in the Hermes cron prompt, not in the tracked Python code.

The correct approach is:

1. Determine `PROJECT_DIR` after clone or discovery.
2. Run `prepare_deploy.sh`.
3. Confirm that `cronjob_prompt.generated.txt` was created with the correct absolute project path.
4. Use the generated cron prompt file content directly when creating or updating cron.

If future code changes are allowed, recommend this improvement:

- keep code paths relative to the repository root
- keep deployment-specific absolute paths out of tracked files

## Expected User-Facing Outcome

After successful use of this skill, the user should only need Hermes for normal operations:

- view cron jobs
- rerun the job manually
- update keywords
- inspect generated Excel and viewer output

The user should not need to manually edit repository paths in prompt text.

## Operations & Recovery

### Data File Ownership

| File | Git-tracked? | Losable? | Purpose |
|------|-------------|----------|---------|
| `monitor.py` | ✅ | No | Main entry point |
| `papers_record.xlsx` | ❌ (.gitignored) | **YES** | Source of truth for paper metadata |
| `papers/*.pdf` | ❌ (.gitignored) | **YES** | Downloaded PDFs |
| `new_papers.json` | ❌ | **YES** | Intermediate for LLM processing |
| `pending_llm_ids.txt` | ❌ | **YES** | Papers needing summary/affiliations |
| `viewer/papers_data.json` | ✅ | No | Static viewer data (partial metadata backup) |

`papers_record.xlsx` and `papers/` are gitignored and can be silently lost. The only persistent backup of paper metadata is `viewer/papers_data.json`.

### Disaster Recovery: Full Rebuild

When `papers_record.xlsx` or `papers/` are missing:

**Step 1**: `python3 monitor.py` — re-fetches from arXiv, downloads PDFs, creates fresh Excel. Look for `LLM_SUMMARIZATION_REQUIRED` output.

**Step 2**: Batch LLM summarization. Split papers into sub-batches of ≤15 each:

```python
# execute_code: split into batches
import json
with open('new_papers.json') as f:
    data = json.load(f)
papers = data['papers_to_process'] or data['new_papers']
for i in range(0, len(papers), 15):
    batch = papers[i:i+15]
    with open(f'/tmp/arxiv_batch_{i//15}.json', 'w') as f:
        json.dump(batch, f, ensure_ascii=False)
```

Delegate 2-3 parallel subagents. Each reads its batch JSON, extracts affiliations with `pdfplumber` (first 2 PDF pages), generates `summary_cn` (90-150 Chinese chars) from abstract, saves to `/tmp/arxiv_batch_N_results.json`.

**Step 3**: Backfill Excel via **terminal** (not execute_code — sandbox lacks openpyxl):

```python
import json, openpyxl
all_results = {}
for i in range(N_batches):
    with open(f'/tmp/arxiv_batch_{i}_results.json') as f:
        for r in json.load(f):
            all_results[r['arxiv_id']] = r
wb = openpyxl.load_workbook('papers_record.xlsx')
ws = wb['Papers']
headers = {cell.value: cell.column for cell in ws[1]}
for row in range(2, ws.max_row + 1):
    aid = ws.cell(row=row, column=headers['arxiv_id']).value
    if aid and str(aid).strip() in all_results:
        r = all_results[str(aid).strip()]
        ws.cell(row=row, column=headers['affiliations']).value = r.get('affiliations', '')
        ws.cell(row=row, column=headers['summary_cn']).value = r.get('summary_cn', '')
wb.save('papers_record.xlsx')
```

**Step 4**: Rebuild & sync:
```bash
python3 viewer/build_data.py
python3 monitor.py --sync-pending-state
```

### Operational Pitfalls

1. **delegate_task timeout**: Subagents have 600s timeout. 17 papers per batch is borderline — may timeout. **Partial results ARE saved** before timeout — always check `/tmp/arxiv_batch_*_results.json`. Keep batches ≤15.

2. **execute_code sandbox**: Does NOT have `openpyxl` or other pip packages. Use `terminal` for all Excel operations.

3. **JSON control characters**: `viewer/papers_data.json` may contain control chars in abstracts. Use `json.loads(text, strict=False)`.

4. **viewer/papers_data.json format**: Dict with keys `count`, `papers[]`, date ranges — NOT a flat list. Access via `data['papers']`.

5. **arXiv API timeouts**: `export.arxiv.org:443` can timeout (30s). Transient — next cron run retries. For manual recovery, re-run `monitor.py`.

6. **Feishu report via execute_code**: Use `terminal` to read large JSON files (the papers_data.json can be large), then process in execute_code with `strict=False`.

### Quick Health Check

```bash
cd ~/projects/hermes-arxiv-agent
ls papers_record.xlsx           # exists?
ls papers/ | wc -l              # how many PDFs?
cat pending_llm_ids.txt         # empty = all processed
python3 -c "import json; d=json.load(open('viewer/papers_data.json')); print(d['count'], 'papers')"
```

### Cron Job

- Job ID: `b5f0da8293f1`
- Schedule: daily at 08:00
- Delivery: Feishu (user open_id: `ou_1e6a1b2ebfe154d5b0470b6f003ecd06`)
- Manual run: use `cronjob action=run job_id=b5f0da8293f1`
