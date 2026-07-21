# Iterative Resume Editing Workflow

## Pattern: Edit → PDF → Send (repeat)
When user asks to modify a resume and send it back:

1. **Edit**: Use `patch` tool to modify the HTML file (never overwrite with write_file for iterative edits)
2. **Convert**: Chrome headless `--print-to-pdf --no-margins --no-pdf-header-footer`
3. **Send**: `cd /path/to/dir && lark-cli im +messages-send --user-id <id> --as bot --file ./resume.pdf`
   - lark-cli requires relative paths — always `cd` to the file's directory first

## Single command for steps 2+3:
```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu \
  --print-to-pdf="/path/to/output.pdf" \
  --no-margins --no-pdf-header-footer \
  "file:///path/to/input.html" && \
cd /path/to/dir && lark-cli im +messages-send --user-id <user_id> --as bot --file ./output.pdf
```

## Resume content guidelines
- Keep descriptions honest and verifiable against actual code/projects
- Use `highlight` boxes with left border for project bullet points
- Skills grid: 2-column layout with colored labels
- A4 page: `max-width: 210mm`, padding ~28px 50px
- Font: PingFang SC / Microsoft YaHei for Chinese

## Pitfalls
- Chrome headless prints harmless stderr errors (`task_policy_set`) — ignore them
- PDF size ~600-700KB for a single-page resume is normal
- If resume overflows to 2 pages, reduce font-size or padding, or trim content
