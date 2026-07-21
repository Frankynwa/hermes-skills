# Cursor Jitter / 光标抖动 排查指南

用户报告光标在原地抖动/震颤、光标自己乱跑/跳位时，按以下顺序排查。

## 排查流程

### Step 1: 检查 CGEvent 状态污染（Hermes 侧）

上次的 CGEvent 脚本 mouseUp 没发出去，macOS 以为左键一直按着。
检查方法：
```bash
# 查找残留 Swift 编译产物
find /tmp -maxdepth 1 -type f \( -name '*.swift' -o -name 'click*' -o -name 'mouse*' -o -name 'cgevent*' \) 2>/dev/null

# 查找残留 CGEvent 进程
ps aux | grep -iE 'swift.*event|cliclick|osascript.*mouse|osascript.*click' | grep -v grep
```

如果找到：重启 Hermes 清理。CGEvent 状态不跨重启持久化。

### Step 2: 检查第三方输入拦截工具

**关键洞察：** 这类工具 hook 系统 HID 事件层，不仅影响外接鼠标，**也影响触控板**。
即使用户说"我没连鼠标"，这些工具仍然会导致触控板光标抖动。

```bash
ps aux | grep -iE 'mos|karabiner|bettertouch|steermouse|linearmouse|macmousefix|scroll|loop' | grep -v grep
```

已知案例：
- **Mos.app** — 平滑滚动工具，hook HID 事件层。即使只用触控板也会导致光标抖动+跳位。
  - Mos 位于 `/Applications/Mos.app`，但在 App Translocation 下路径可能是 `/private/var/folders/.../d/Mos.app`
  - 杀进程后如果在 Login Items 里，**重启电脑会自动恢复**

### Step 3: 检查 Login Items（重启后复发的关键）

如果 kill 了进程但重启后问题复发，说明它在 Login Items 里：
```bash
osascript -e 'tell application "System Events" to get the name of every login item'
```

移除方法：
```bash
osascript -e 'tell application "System Events" to delete login item "Mos"'
```

### Step 4: 检查充电干扰（硬件层面）

MacBook 充电时触控板抖动是经典问题（充电器电流干扰电容传感器）。
- 验证：拔掉充电线，用电池供电试试
- 根治：换有接地的三孔插座、用原装充电器

### Step 5: 检查 LaunchAgent/Daemon

```bash
# 第三方 LaunchAgent
ls ~/Library/LaunchAgents/ | grep -v 'apple\|com.apple'
ls /Library/LaunchAgents/ 2>/dev/null
ls /Library/LaunchDaemons/ 2>/dev/null
```

## Mos.app 详细案例（2026-05-27）

### 现象
- 光标在原地抖动/震颤 + 自己乱跑/跳位
- 用户使用触控板，未连接外接鼠标
- 重启电脑后问题依旧

### 排查过程
1. 检查 CGEvent 残留 → 无
2. 检查 cua-driver 进程 → 无
3. 发现 Mos.app (PID 1471) 在运行 → kill
4. 用户反馈"还是"→ 深入排查
5. 发现 ToDesk 驱动已加载 → 建议删除（用户自行处理）
6. 用户重启电脑 → 问题依旧
7. 检查 Login Items → **Mos 在登录项里，重启后自动恢复**
8. kill + 从 Login Items 移除 → 解决

### 根因
Mos.app 通过 hook 系统 HID 事件层实现平滑滚动，这会干扰触控板的原始事件处理。
关键点：
- Mos 不只是"外接鼠标工具"——它 hook 底层 HID，触控板也受影响
- Mos 在 Login Items 里会开机自启，kill 后重启又回来
- App Translocation 导致路径在 `/private/var/folders/...` 下

### 解决
```bash
# 1. 杀进程
kill <mos_pid>

# 2. 从 Login Items 移除
osascript -e 'tell application "System Events" to delete login item "Mos"'
```

### 用户纠正记录
- 用户说"我都没连鼠标啊"→ 重要：Mos 影响触控板，不只是外接鼠标
- 用户说"不是硬件问题吧，就是软件的问题"→ 不要默认硬件原因，先彻底排查软件
- 用户说"电脑都重启了还在晃，绝对是你的锅"→ 重启后复发 = 检查 Login Items
