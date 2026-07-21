# Network Fallback for Skill Installation

When `npx skills add <owner/repo@skill> -g -y` fails with "Couldn't connect to server" or "Error in the HTTP2 framing layer" (GitHub blocked from the terminal), follow this priority order.

## Priority 1: Route Through System Proxy (macOS)

The user likely has a VPN with system-level proxy configured. The terminal doesn't inherit it automatically.

### Discover the proxy

```bash
networksetup -getwebproxy Wi-Fi        # HTTP proxy
networksetup -getsecurewebproxy Wi-Fi   # HTTPS proxy
networksetup -getsocksfirewallproxy Wi-Fi  # SOCKS proxy
```

Look for `Enabled: Yes` and the `Server: 127.0.0.1` / `Port: XXXX` values.

### Set env vars and retry

```bash
export HTTPS_PROXY=http://127.0.0.1:<PORT> HTTP_PROXY=http://127.0.0.1:<PORT>
npx skills add <owner/repo@skill> -g -y
```

Common proxy ports: 7890 (Clash default), 7897 (Clash Verge), 1087 (SOCKS).

## Priority 2: Check SSH Access

If HTTPS+proxy still fails:

```bash
git ls-remote git@github.com:<owner>/<repo>.git 2>&1 | head -3
```

If SSH works (returns commit refs), configure git to use SSH:

```bash
git config --global url."git@github.com:".insteadOf "https://github.com/"
```

Then retry `npx skills add`.

## Priority 3: Manual Construction (LAST RESORT)

**Only use this when Priority 1 and 2 both fail after thorough attempts.**

**Warning**: Manual construction is inherently unreliable — the user will rightfully question whether the result matches the source. Always tell the user you're falling back to manual and give them the option to wait until network is available.

### Download from raw.githubusercontent.com

```bash
BASE="https://raw.githubusercontent.com/<owner>/<repo>/main/skills"
curl -sL "$BASE/<category>/<name>/SKILL.md"
```

### Identify all dependencies

Skills often delegate to others (e.g. `grill-me` → `grilling`). Read each SKILL.md first — if it references another skill name (via `/skill-name` syntax), download that too. Dependencies are co-located in the same repo.

### Write to Hermes skills directory

Each skill in its own directory: `~/.hermes/skills/<category>/<name>/SKILL.md`.

```python
from hermes_tools import write_file
import os

SKILLS_DIR = os.path.expanduser("~/.hermes/skills")
write_file(os.path.join(SKILLS_DIR, "<category>/<name>/SKILL.md"), content)
```

### Verify

Run `skills_list()` and confirm all new skills appear with correct descriptions.

## Limitations of Manual Installation

- Skills are NOT tracked by `npx skills` for updates
- Complex file dependencies (templates, scripts, multi-file references) are easy to miss
- YAML frontmatter may need adaptation for the target agent platform
- No security audit (Gen/Snyk scans are skipped)
- The user has every right to be skeptical of the result
