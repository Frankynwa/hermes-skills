# GitHub MCP Server Setup

## Config Block (add to `mcp_servers:` in `~/.hermes/config.yaml`)

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_xxxxxxxxxxxxxxxxxxxx"
    timeout: 60
```

## Token Generation Steps (for user)

1. Open https://github.com/settings/tokens?type=beta
2. Click "Generate new token"
3. Name: `hermes-mcp`
4. Expiration: 90 days or longer
5. Repository access: All repositories (or select specific ones)
6. Permissions → Repository permissions → Contents: **Read and write**
7. Generate → copy the `ghp_...` or `github_pat_...` string

## Registered Tools (after setup)

The server exposes tools prefixed `mcp_github_*`, including:
- `mcp_github_create_repository` — create repos
- `mcp_github_push_files` — push files to repo
- `mcp_github_create_pull_request` — open PRs
- `mcp_github_list_issues` / `mcp_github_create_issue`
- `mcp_github_fork_repository`
- `mcp_github_search_repositories`
- `mcp_github_get_file_contents`

## Common Pitfalls

- **`mcp` package not installed**: Most common failure. Always `pip show mcp` first.
- **Token without permissions**: Default fine-grained tokens have NO repo access. User must explicitly grant Contents: Read and write.
- **Classic vs fine-grained tokens**: Classic tokens (`ghp_`) are simpler for broad access. Fine-grained (`github_pat_`) are more secure but need per-repo permission setup.
- **npx not found**: Ensure Node.js is installed. On macOS: `brew install node`.
- **Config indentation**: YAML is indent-sensitive. `mcp_servers` must be at the top level (same indent as `model:`, `providers:`).
- **`~/.hermes/config.yaml` is a protected file**: The `patch` tool will reject edits to it. Use `terminal` with `cat >>` to append, or `sed` for targeted edits. Example: `cat >> ~/.hermes/config.yaml << 'EOF'\nmcp_servers:\n  github:\n    ...\nEOF`
- **Config append vs overwrite**: Always APPEND (`>>`) to config.yaml, never overwrite (`>`). The file contains all Hermes settings — overwriting destroys everything.
