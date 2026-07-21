#!/usr/bin/env python3
"""Batch text replacement for UI localization. 
Runs standalone to avoid execute_code's read_file line-prefix corruption.
"""
import sys

if len(sys.argv) < 2:
    print("Usage: python3 translate.py <file.js>")
    sys.exit(1)

filepath = sys.argv[1]

with open(filepath, 'r') as f:
    content = f.read()

# ===== TRANSLATION MAP =====
# Format: ("old_string", "new_string")
# Order: put longer/more-specific matches first to avoid partial replacements

tr = [
    # === SIDEBAR ===
    ("{id:'overview',label:'Overview'}", "{id:'overview',label:'概览'}"),
    ("{id:'power',label:'Power'}", "{id:'power',label:'功率'}"),
    ("{id:'dipswell',label:'Dip/Swell'}", "{id:'dipswell',label:'骤降/骤升'}"),
    ("{id:'harmonics',label:'Harmonics'}", "{id:'harmonics',label:'谐波'}"),
    ("{id:'transient',label:'Transient'}", "{id:'transient',label:'瞬变'}"),
    ("{id:'events',label:'Events'}", "{id:'events',label:'事件'}"),
    ("{id:'settings',label:'Settings'}", "{id:'settings',label:'设置'}"),
    ("{id:'simplemeas',label:'SimpleMeas'}", "{id:'simplemeas',label:'简易测量'}"),
    ("{id:'config',label:'Config'}", "{id:'config',label:'配置'}"),
    ("{id:'trends',label:'Trends'}", "{id:'trends',label:'趋势'}"),

    # Add more translations here...
]

# Apply translations
missed = []
for old, new in tr:
    if old in content:
        content = content.replace(old, new)
    else:
        missed.append(old[:70])

print(f"Applied: {len(tr) - len(missed)} / {len(tr)}")
for m in missed:
    print(f"  MISS: {m}")

with open(filepath, 'w') as f:
    f.write(content)

print(f"\nWritten {len(content)} chars to {filepath}")
