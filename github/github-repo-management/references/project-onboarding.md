# Project Onboarding & Cross-Device GitHub Sync

When the user has a project with a generic name (e.g., "app", "my-project", "test") or wants to back up a local project to GitHub for cross-device collaboration.

## Step 1: Inspect & Name

Before renaming, identify what the project actually does:

```bash
# Check package.json for name, deps, scripts
cat project/package.json

# Check README or docs
ls project/*.md project/README*

# Check source structure (language, framework)
ls project/src/ project/api/ project/lib/

# Check git status
cd project && git log --oneline -3 && git status --short
```

Naming rules:
- **kebab-case**: `must-prof-eval`, `focuspaw-pet`, `quant-stock-picker`
- **Descriptive but concise**: 2-4 words, no generic suffixes like `-app` or `-tool`
- **Match the domain**: professor evaluation → `must-prof-eval`, not `my-web-app`

## Step 2: Rename & Clean Up

```bash
# Rename folder
mv /path/to/old-name /path/to/new-name

# Update package.json name field
# Update any internal project references

# Clean .gitignore — ensure it covers the project's ecosystem:
# - Python: __pycache__/, *.py[cod], .venv/, venv/
# - Node: node_modules/, dist/, .next/
# - IDE: .vscode/, .idea/
# - OS: .DS_Store, Thumbs.db
# - Secrets: .env, .env.local
```

## Step 3: Commit & Push

```bash
cd /path/to/new-name

# Stage everything
git add -A

# Commit with descriptive message covering what was added/changed
git commit -m "feat: <description of what the project does>

- Key feature 1
- Key feature 2
- Updated project metadata and .gitignore"

# Create GitHub repo and push (if gh is authenticated)
gh repo create new-name --source . --private --push

# OR if repo needs to be created manually:
gh repo create new-name --private
git remote add origin https://github.com/$GH_USER/new-name.git
git push -u origin main
```

## Step 4: Verify Two-Device Readiness

After pushing, confirm:
1. `.gitignore` covers all generated files (node_modules, __pycache__, dist, .env)
2. `main` branch is the default
3. No secrets or large binaries in the commit
4. README exists with basic project description

## Common Pitfalls

- **Forgetting Python cache**: Always add `__pycache__/`, `*.py[cod]` to .gitignore for mixed JS+Python projects
- **Committing .env**: Check `git status` carefully before committing — .env files with API keys are the #1 accident
- **Generic names**: "app" is meaningless in `gh repo list` — always rename before pushing
- **node_modules in commit**: Verify node_modules is in .gitignore; if accidentally tracked, `git rm -r --cached node_modules` first
- **`git push` hangs forever**: Some network environments (especially in China/Macau) have HTTP/2 negotiation issues with GitHub. Fix: `GIT_HTTP_VERSION=1.1 git push -u origin main`. If this works, set globally: `git config --global http.version HTTP/1.1`
- **`gh auth login --with-token` fails with "missing required scope 'read:org'"**: Fine-grained tokens may lack org scopes. Bypass `gh` entirely: store the token in `~/.git-credentials` via `git config --global credential.helper store` and embed token in remote URL or credentials file
- **Files locked with `Resource deadlock avoided` (errno 11) on macOS**: This is usually NOT Cursor — it's iCloud \"Optimize Mac Storage\" evicting files. Check with `ls -laO <file>` — if flags include `dataless`, the file is an iCloud stub. Fix: `brctl download <file>` to pull the content back. To prevent recurrence: avoid storing active projects on Desktop (iCloud-synced); use `~/projects/` or `~/dev/` instead. If `brctl download` doesn't work, `touch` the file and wait ~10s for iCloud to sync.
