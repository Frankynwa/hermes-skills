# Installing Community Skills from Recommendation Table

Workflow for filtering the Feishu recommendation table and installing valuable community skills/plugins.

## Step 1: Cross-Reference with Existing Skills

Before installing anything, check what's already installed:

```bash
# List all existing SKILL.md files
search_files(pattern="SKILL.md", target="files", path="~/.hermes/skills")
```

Compare the recommendation table entries against existing skills by name. Skills already present locally should be skipped (even if the table has newer dates — the table repeats entries across daily runs).

## Step 2: Filter for Genuine Value

Not every recommended skill is worth installing. Filter criteria:

1. **Not already installed** (name match against local skills)
2. **Not overlapping** with existing skills (e.g. don't install `hermes-dojo` if `post-task-reflection` already covers self-improvement)
3. **Matches user's actual workflows** (coding, Feishu, quantitative analysis, PDF generation, homework)
4. **Production quality** — prefer skills with SKILL.md, clear description, active maintenance
5. **Practical over flashy** — token compression > novelty AI demos

Categories that consistently add value for this user:
- Developer productivity (code review, git workflows, planning)
- Token/cost optimization (rtk-hermes)
- Writing quality (avoid-ai-writing, humanizer)
- Workflow automation (planning-with-files, workflow-runner)
- Finance/quantitative (longbridge, quant-factor-investing)

Categories that are usually noise for this user:
- Security/pentest (not relevant)
- Blockchain/Web3 (not relevant)
- Marketing/SDR (not relevant)
- Social media automation (not relevant)

## Step 3: Check Repo Structure

GitHub repos have inconsistent structures. Before downloading, determine where the SKILL.md lives:

```bash
curl -sL "https://api.github.com/repos/<owner>/<repo>/git/trees/main?recursive=1" | python3 -c "
import sys,json
data=json.load(sys.stdin)
for item in data.get('tree',[]):
    if 'SKILL' in item['path'] or 'hermes' in item['path'].lower():
        print(item['path'])
"
```

Common patterns:
- `SKILL.md` at root — simple skill (e.g. avoid-ai-writing, 21-day-self-interview)
- `skills/<name>/SKILL.md` — multi-skill repo (e.g. longbridge/skills has 13 sub-skills)
- `AGENT_SKILL.md` — renamed variant (e.g. hermes-arxiv-agent) — rename to SKILL.md on install
- No SKILL.md — might be a plugin, not a skill (e.g. rtk-hermes)

**Pitfall: branch names vary.** Some repos use `main`, others `master`. If download returns 404, try the other.

## Step 4: Download and Install

**Critical: each skill needs its own directory with SKILL.md inside.** `skills_list` only discovers `SKILL.md` files inside named subdirectories.

```bash
mkdir -p ~/.hermes/skills/<category>/<skill-name>
curl -sL --connect-timeout 15 --max-time 45 \
  https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<path-to-SKILL.md> \
  -o ~/.hermes/skills/<category>/<skill-name>/SKILL.md
```

**For multi-skill repos** (e.g. longbridge has 13 sub-skills): pick the sub-skills relevant to the user. Install each as its own directory:
```bash
for skill in longbridge longbridge-quant longbridge-market-data; do
  mkdir -p ~/.hermes/skills/finance/$skill
  curl -sL "https://raw.githubusercontent.com/longbridge/skills/main/skills/$skill/SKILL.md" \
    -o ~/.hermes/skills/finance/$skill/SKILL.md
done
```

Category placement:
- `finance/` — stocks, quant, market data
- `software-development/` — code review, debugging, git workflows
- `productivity/` — planning, writing, automation
- `research/` — arxiv, paper monitoring
- `autonomous-ai-agents/` — parallel agents, delegation
- `communication/` — multi-agent debate, messaging
- `hermes/` — memory, config, self-improvement

**Verify download:** Check file size (>100 bytes). Empty or "404: Not Found" means wrong path/branch.

## Step 5: Install Plugins (Different from Skills)

Some "skills" are actually **plugins** — they register via Python entry_points and may need separate binary dependencies.

Example: **rtk-hermes**
- `pip install rtk-hermes` — plugin code
- `brew install rtk` — the rtk binary (NOT `pip install rtk` which is different)
- Registers via `hermes_agent.plugins` entry_points
- Requires Gateway restart to activate

How to identify a plugin:
```bash
python3 -c "
from importlib.metadata import distribution
dist = distribution('<package-name>')
for ep in dist.entry_points:
    print(f'group={ep.group} name={ep.name} value={ep.value}')
"
```

## Step 6: Install CLI Tools (Non-Python Dependencies)

Some skills require CLI tools installed via brew or direct download.

**Pattern: brew tap + cask (e.g. Longbridge CLI)**
```bash
# 1. Add tap
brew tap longportapp/tap
# 2. Trust the tap (REQUIRED for casks from untrusted taps)
brew trust longportapp/tap
# 3. Install
brew install --cask longportapp/tap/longport-terminal
```

**Pitfall: brew cask names may differ from repo names.** The brew tap `longportapp/tap` had cask `longport-terminal`, but the actual GitHub repo was `longbridge/longbridge-terminal`. When brew fails 404, search GitHub for the correct repo.

**Fallback: direct binary download from GitHub releases:**
```bash
curl -L --max-time 300 \
  "https://github.com/<owner>/<repo>/releases/download/<tag>/<binary>-darwin-arm64.tar.gz" \
  -o /tmp/binary.tar.gz
cd /tmp && tar xzf binary.tar.gz
mkdir -p ~/.local/bin
cp <binary> ~/.local/bin/
chmod +x ~/.local/bin/<binary>
```

Install to `~/.local/bin/` (not `/usr/local/bin/` which needs sudo). Ensure `~/.local/bin` is in PATH (check `~/.zshrc`).

## Step 7: Device-Code OAuth Auth Flow

Some CLI tools (e.g. Longbridge) use device-code OAuth. Key pitfalls:

1. **The CLI process must stay alive while the user authorizes in the browser.** If the terminal command times out, the token exchange fails silently.
2. **DO NOT use `pty=true` with timeout** — the pty timeout kills the process.
3. **Use `terminal(timeout=300)`** — generous timeout, no pty. The CLI prints a URL and waits.
4. **If that fails, use `terminal(background=true)`** — run the auth in background, then poll for completion.
5. **If the user has already authorized in the browser but the CLI was killed**, just re-run the auth command — it will generate a new code but the server may already have the token cached from the previous attempt.

**User frustration signal:** If auth fails 3+ times, STOP retrying the same approach. Diagnose WHY it fails (timeout? network? wrong repo?) before trying again. The user will get angry if you keep doing the same thing that doesn't work.

## Step 8: Verify Installation

For skills: check file exists and appears in `skills_list`:
```bash
ls -la ~/.hermes/skills/<category>/<skill-name>/SKILL.md
# skills_list will pick it up on next session
```

For plugins: verify entry_points and binary:
```bash
python3 -c "from importlib.metadata import distribution; [print(ep) for ep in distribution('<pkg>').entry_points]"
which <binary>
```

For CLI tools: run `--version` or `--help`.

## Pitfalls

1. **`pip install rtk` ≠ rtk binary.** The `rtk` pip package is a different tool. rtk-hermes needs `brew install rtk`.

2. **Branch name mismatch.** Try `main` first, fall back to `master`.

3. **superpowers-zh is a multi-skill repo.** Don't install as one skill. Cherry-pick relevant sub-skills.

4. **Some repos are 404 or private.** Don't spend time retrying — skip and move on.

5. **Large SKILL.md files are normal.** `avoid-ai-writing` is 62KB. Hermes loads skills on-demand.

6. **Flat file installation DOES NOT work.** Each skill needs `~/.hermes/skills/<category>/<name>/SKILL.md`. Dumping `.md` files in a flat directory won't be detected.

7. **Non-standard SKILL.md names.** Some repos use `AGENT_SKILL.md`. Rename to `SKILL.md` on install.

8. **Don't install overlapping skills.** `hermes-dojo` ≈ `post-task-reflection`, `SkillClaw` ≈ built-in Curator.

9. **Don't clean up before verifying.** When reorganizing (flat → directory), verify new structure works BEFORE deleting old. Lost a longbridge main SKILL.md by cleaning up too early.

10. **GitHub raw downloads can timeout.** Use `--connect-timeout 15 --max-time 45` and retry.

11. **Brew lock files.** If `brew install` says "Another brew update process is running", remove the stale lock: `rm -f /opt/homebrew/var/homebrew/locks/update`.

12. **macOS kills unsigned/corrupted binaries.** If a downloaded binary gets `Killed: 9`, it's either corrupted (truncated download) or unsigned. Re-download completely. `xattr -d com.apple.quarantine` only works if the file is intact.

13. **Brew tap ≠ trusted.** New taps need `brew trust <tap>` before cask install works. Error: "Refusing to load cask from untrusted tap".

14. **Brew cask name ≠ repo name.** The tap may rename the cask. Check `ls <tap-path>/Casks/` to find the actual cask name.

15. **Plugins need Gateway restart.** Skills load per-session, plugins register at startup.
