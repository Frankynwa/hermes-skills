# Bitable Permission API Scope Requirements

## permission.members.create (Add Collaborators)

API: `POST /open-apis/drive/v1/permissions/{token}/members?type=bitable`

Required scopes (ALL must be enabled):
- `docs:permission.member:create`
- `drive:drive`
- `drive:file`
- `bitable:bitable`

Enable URL template:
```
https://open.feishu.cn/page/scope-apply?clientID=<app_id>&scopes=drive%3Adrive%2Cdrive%3Afile%2Cbitable%3Abitable%2Cdocs%3Apermission.member%3Acreate
```

Error when scopes missing: `1063001` (misleading "Invalid parameter" - actually scope issue)

## permission.public (Link Share Settings)

API: `PATCH /open-apis/drive/v1/permissions/{token}/public?type=bitable`

Required scopes:
- `docs:permission.setting:write_only`
- `drive:drive`
- `drive:file`
- `bitable:bitable`
- (plus `docs:permission.setting:read` for GET)

Error when scopes missing: `99991672` (correctly reports missing scopes with `permission_violations`)

## permission.members.transfer_owner (Transfer Ownership)

API: `POST /open-apis/drive/v1/permissions/{token}/members/transfer_owner?type=bitable`

Not tested yet. Likely needs similar scopes plus owner-transfer specific ones.

## Diagnosing Scope Errors

1. Use `--dry-run` to check parameter formatting
2. If params look correct but error is 1063001 → missing scope (not parameter issue)
3. If error is 99991672 → check `permission_violations` in response for exact missing scopes
4. Update lark-cli before troubleshooting: `lark-cli update`
