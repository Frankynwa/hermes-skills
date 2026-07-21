#!/usr/bin/env python3
"""Generate README.md for a hermes-skills git repo from YAML frontmatter.

Usage: python3 skills-readme-generator.py [skills_dir]

Scans all SKILL.md files (excluding .archive, .hub, .curator, .git),
extracts `name` and `description` from YAML frontmatter, groups by
category directory, and writes a README.md with overview + detailed listing.
"""

import os, re, sys
from collections import OrderedDict

SKILLS_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/.hermes/skills")


def parse_frontmatter(path):
    try:
        with open(path) as f:
            content = f.read()
    except Exception:
        return None, None
    m = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not m:
        return None, None
    fm = m.group(1)
    name = re.search(r'^name:\s*(.+)', fm, re.MULTILINE)
    desc = re.search(r'^description:\s*["\']?(.+?)["\']?\s*$', fm, re.MULTILINE)
    return (
        name.group(1).strip() if name else None,
        desc.group(1).strip() if desc else None,
    )


def collect_skills(skills_dir):
    skills = []
    for root, dirs, files in os.walk(skills_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        if 'SKILL.md' in files:
            rel = os.path.relpath(root, skills_dir)
            if any(rel.startswith(x) for x in ['.archive', '.hub', '.curator']):
                continue
            name, desc = parse_frontmatter(os.path.join(root, 'SKILL.md'))
            if name:
                category = rel.split('/')[0]
                skills.append((category, name, rel, desc or ''))
    return skills


def generate_readme(skills_dir, output_path=None):
    skills = sorted(collect_skills(skills_dir))
    cats = OrderedDict()
    for cat, name, d, desc in skills:
        cats.setdefault(cat, []).append((name, d, desc))

    total = sum(len(v) for v in cats.values())
    out = [
        "# Hermes Skills\n",
        f"> Personal skill collection for [Hermes Agent](https://github.com/NousResearch/hermes-agent) — **{total} skills** across **{len(cats)} categories**.\n",
        "## 📋 Overview\n",
    ]
    for cat in cats:
        count = len(cats[cat])
        out.append(f"- **{cat}** — {count} skill{'s' if count > 1 else ''}")
    out.append("\n---\n")

    for cat in cats:
        out.append(f"## {cat}\n")
        for name, d, desc in cats[cat]:
            clean = desc.strip()
            if len(clean) > 250:
                clean = clean[:247] + "..."
            if not clean:
                clean = "*(no description)*"
            out.append(f"- **`{name}`** — {clean}")
            out.append(f"  `{d}/`\n")
        out.append("")

    out.append("---\n## 🔄 Sync to Another Device\n")
    out.append("```bash")
    out.append("git clone <repo-url> ~/.hermes/skills")
    out.append("```\n")

    result = '\n'.join(out)
    if output_path:
        with open(output_path, 'w') as f:
            f.write(result)
    return result


if __name__ == '__main__':
    output = os.path.join(SKILLS_DIR, 'README.md')
    result = generate_readme(SKILLS_DIR, output)
    print(f"Written {len(result)} chars to {output}")
    cats = len(set(c for c, _, _, _ in collect_skills(SKILLS_DIR)))
    total = len(collect_skills(SKILLS_DIR))
    print(f"Categories: {cats}, Skills: {total}")
