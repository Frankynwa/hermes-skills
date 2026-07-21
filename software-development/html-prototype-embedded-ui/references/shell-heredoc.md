# Shell Heredoc for File Generation

## Problem

Python `write_file` tool corrupts backslashes when writing content with nested quotes. Three levels of escaping (Python string → file on disk → JS/HTML/C string interpretation) inevitably break.

## Solution

Use shell heredoc directly with the `terminal` tool:

```bash
cat > output_file.ext << 'ENDOFFILE'
Content here — NO escaping needed.
Single quotes ' work. Double quotes " work.
Backslashes \ work. Template literals ` work.
Everything is literal until the delimiter.
ENDOFFILE
```

Key: the delimiter in single quotes (`'ENDOFFILE'`) prevents ALL shell expansion — variables, backslashes, everything is literal.

## When To Use

- Writing HTML with inline JavaScript (nested quotes)
- Writing JavaScript files with template strings
- Any file where `write_file` introduces backslash corruption

## Verification

After writing, always validate:
```bash
# JS syntax
node --check file.js

# HTML/JS combo
node --check <(sed -n '/<script>/,/<\/script>/p' file.html | sed '1d;$d')
```
