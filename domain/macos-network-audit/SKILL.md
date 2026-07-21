---
name: macos-network-audit
description: >
  Audit local WiFi/network security on macOS — detect ARP spoofing, DNS hijacking,
  rogue devices, sniffing tools, remote access backdoors, and router tampering.
  Use when: user asks to check WiFi safety, scan connected devices, verify network
  integrity, or audit a rental/shared/unknown network.
triggers:
  - "检查WiFi是否安全"
  - "scan network devices"
  - "check if WiFi has backdoors"
  - "how many devices on my network"
  - "网络是否被监控"
  - "audit this network"
  - "rental apartment WiFi"
  - "WiFi为什么这么卡"
  - "深度检查网络"
  - "路由器是否被劫持"
  - "光猫安全吗"
  - "局域网里有什么设备"
---

# macOS Local Network Security Audit

Comprehensive checklist for auditing a WiFi network from a macOS client.
Designed for scenarios like: new rental, shared network, unknown router, suspected snooping.

## Quick One-Liner (Run First)

```bash
# 快速概览：WiFi信息 + 局域网设备 + 代理/VPN状态
networksetup -getairportnetwork en0; echo "---"; arp -a | grep -v mcast; echo "---"; networksetup -getwebproxy Wi-Fi; echo "---"; ifconfig | grep -E "utun|tun|ppp" || echo "无VPN"
```

## Step-by-Step Audit

### 1. WiFi Connection Info

```bash
# 首选: system_profiler（macOS 13+ 全版本可用，信息最全）
system_profiler SPAirPortDataType

# 备选: airport -I（macOS 12 及更早版本）
/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I
```

**PITFALL**: `airport` binary was removed in macOS 13+. On macOS 13+/14+/15+/26+, `airport -I` returns "No such file or directory". Always use `system_profiler SPAirPortDataType` as the primary command — it returns WiFi name, PHY mode, channel, country code, and connected status. It does NOT return encryption type directly; check the router admin page or use `airport -s` (if available) to see encryption of nearby networks.

Check: encryption type (WPA3 > WPA2 > WPA/WPA2 mixed > WPA), signal strength, channel congestion.

**Parsing system_profiler SPAirPortDataType output**: The output lists ALL nearby WiFi networks, not just the connected one. To find the current connection, look for the block after "Current Network Information:" that has "Status: Connected" nearby. Key fields:
- `PHY Mode:` — 802.11n = WiFi 4, 802.11ac = WiFi 5, 802.11ax = WiFi 6/6E
- `Channel:` — "(2GHz)" = 2.4GHz band, "(5GHz)" = 5GHz band
- `Security:` — WPA/WPA2 Personal = mixed mode (upgrade recommended), WPA2 Personal = standard, WPA3 Personal = best
- `Signal / Noise:` — -45 dBm signal is excellent, -80 dBm is weak. SNR (signal minus noise) > 25 dB is good.
- `Transmit Rate:` — link speed in Mbps (144 = typical 2.4GHz 802.11n, 866 = typical 5GHz 802.11ac)

### 2. Device Discovery (ARP Table)

```bash
arp -a
```

Active devices have a MAC address; `incomplete` entries are IPs that were queried but didn't respond. Count only non-incomplete, non-mcast entries.

**PITFALL**: ARP cache only shows devices your Mac has recently communicated with. It is NOT a full device list. To get a more complete picture, do a ping sweep first, then re-read ARP:

```python
# Ping sweep to populate ARP cache
import subprocess, concurrent.futures
def ping_host(ip):
    try:
        r = subprocess.run(['ping', '-c', '1', '-W', '1', ip], capture_output=True, timeout=3)
        return ip if r.returncode == 0 else None
    except: return None

with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
    results = list(ex.map(ping_host, [f'192.168.1.{i}' for i in range(1, 255)]))
active = [ip for ip in results if ip]
# Then: arp -a to get full refreshed list
```

**Locally Administered MAC Addresses**: MACs where the second hex digit of the first octet is 2, 6, A, or E (e.g., `7a:a3:7d:...`, `4a:ea:04:...`) are "Locally Administered Addresses" (LAA) — software-generated, not hardware-burned. Common sources:
- macOS/iOS MAC randomization (privacy feature, normal)
- Android MAC randomization
- Virtual machines, Docker containers
- Some IoT devices

LAA devices cannot be identified by OUI vendor lookup. To identify them, check the router's DHCP client list via the admin page.

### 3. ARP Spoofing Detection

```bash
# Check gateway MAC is consistent
arp -a -n | grep "192.168.1.1"
```

If the gateway shows **two different MACs** for the same IP, someone is running ARP spoofing (MITM attack).

### 4. DNS Integrity

```bash
# Current DNS servers
scutil --dns | grep "nameserver" | sort -u

# Manual DNS config check
networksetup -getdnsservers Wi-Fi

# Compare: resolve via system DNS vs public DNS
nslookup baidu.com        # system DNS
nslookup baidu.com 223.5.5.5  # Alibaba public DNS
```

If results differ significantly for the same domain → possible DNS hijacking. CDN-based variance (different IPs) is normal.

### 5. Routing Anomalies

```bash
# Route table — should only have one default gateway
netstat -rn | head -15

# Traceroute — check for unexpected hops
traceroute -m 8 -w 2 8.8.8.8
```

### 6. Proxy & VPN Detection

```bash
# HTTP/HTTPS/SOCKS proxy settings
networksetup -getwebproxy Wi-Fi
networksetup -getsecurewebproxy Wi-Fi
networksetup -getsocksfirewallproxy Wi-Fi

# Active VPN interfaces
ifconfig | grep -E "utun|tun|ppp"
```

A proxy on `127.0.0.1` (like Clash) is the user's own — not a network threat, but can cause latency.

### 7. Sniffing Tools & Remote Access

```bash
# Packet sniffers running?
ps aux | grep -iE 'wireshark|tcpdump|ettercap|mitmproxy|bettercap|arpspoof|nmap|kismet|aircrack' | grep -v grep

# Remote access software (check launchd)
launchctl list | grep -iE 'vnc|ssh|remote|teamviewer|anydesk|todesk|sunlogin|uu.remote'
```

**PITFALL**: `launchctl list | grep` shows ALL registered services, including **unloaded** ones (PID column shows `-` or empty). A service with PID `-` means it's registered but not currently running. Only services with a numeric PID > 0 are actively running. To distinguish:
- `-  78  com.youqu.todesk.desktop` → service is loaded but PID is `-` (exit code 78), may auto-start on next trigger
- `9769  0  com.youqu.todesk.desktop` → PID 9769, actively running
- `-  0  com.youqu.todesk.desktop` → registered but not running

For definitive check on running processes, cross-reference with `ps aux | grep -i todesk` and also check `lsof -i -P -n | grep LISTEN` for network listeners.

**ToDesk/向日葵/TeamViewer/UU远程** on a machine you don't fully control = potential backdoor. Check usage logs and whether launchd plist is set to auto-start.

### 8. SSH & Management Services

```bash
# SSH daemon
launchctl list | grep sshd

# MDM / enterprise management profiles
profiles show
```

### 8b. Firewall Status

```bash
# 检查macOS应用防火墙是否启用
/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
```

If "Firewall is disabled" → all listening services are directly exposed to the LAN. This is a HIGH severity finding.

### 8c. All Listening Ports (Full Inventory)

```bash
# 列出所有监听端口、进程、绑定地址
lsof -i -P -n | grep LISTEN
```

Key patterns to flag:
- `*:PORT` (bound to all interfaces) = LAN-accessible, higher risk
- `127.0.0.1:PORT` (localhost only) = safe, internal use
- Remote access tools (ToDesk, UU远程, TeamViewer) binding to `*` = critical risk
- Dev servers (python, node) binding to `*` = should be restricted to 127.0.0.1

### 9. Gateway Identification (MAC OUI)

```bash
# Extract first 3 octets of gateway MAC
arp -a | grep "192.168.1.1" | awk '{print $4}' | cut -d: -f1-3
```

Common OUIs: `10:47:E7`/`20:6B:E7`/`C4:07:2F` = Huawei, `AC:84:C6`/`5C:E9:31` = TP-Link, `54:A0:50` = ASUS, `EC:F4:BB` = D-Link. Unknown OUIs on a "branded" router = possible firmware replacement.

**Optical Modem (光猫) Detection**: In Chinese ISP setups, the topology is often "光猫 (ONU/ONT) → router → LAN". The optical modem may be:
1. **Integrated** — the Huawei/ZTE/烽火 device at 192.168.1.1 IS the modem+router combo (most common for China Mobile). Look for domain_name `bbrouter` in DHCP options as a Huawei indicator.
2. **Bridge mode** — modem bridges PPPoE to the router, modem is invisible from LAN.
3. **Dual-NAT** — modem at 192.168.0.1 or 10.0.0.1, router at 192.168.1.1.

To detect:
```bash
# Check if any other gateway IPs are reachable
for ip in 192.168.0.1 192.168.2.1 10.0.0.1 10.0.0.138 192.168.100.1; do
  ping -c 1 -W 1 $ip 2>/dev/null | grep "bytes from" && echo "$ip REACHABLE"
done

# Check DHCP domain name (indicates modem vendor)
ipconfig getsummary en0 | grep domain_name
```

If only 192.168.1.1 is reachable → likely integrated modem+router. The report should note this distinction.

### 10. Gateway Stability Test

```bash
ping -c 10 -i 0.5 192.168.1.1 | tail -3
```

0% loss and <10ms avg = healthy. High jitter or loss = channel congestion or hardware issue.

### 11. Port Scan on Router

```bash
# Check common router ports (use no_proxy to bypass local proxy)
nc -z -w 2 192.168.1.1 80   # web management
nc -z -w 2 192.168.1.1 443  # HTTPS management
nc -z -w 2 192.168.1.1 22   # SSH (backdoor risk if open)
nc -z -w 2 192.168.1.1 8080 # alt management
```

### 12. IPv6 Exposure

```bash
ifconfig en0 | grep inet6
```

Global IPv6 (`2409:` or `2001:` prefixes) is normal for Chinese ISPs. But check if IPv6 is leaking past a VPN.

## Performance Diagnostics (Speed/Latency/Stability)

Use when user asks "why is my WiFi slow/laggy" or wants to troubleshoot network performance.
This section is separate from security audit — focus on speed, latency, jitter, and signal quality.

### Diagnostic Workflow

Run ALL checks before concluding. Report findings in sections:
1. WiFi Physical Layer → 2. LAN Stability → 3. Router Info → 4. Bandwidth → 5. International Routing → 6. Software Layer

**User preference**: When user says "deep check" or "深度检查", run the FULL diagnostic sequence across all sections, not a quick summary. Present a structured report with tables, not bullet-point summaries. User gets frustrated with surface-level answers (e.g., "try restarting your router") — always run actual diagnostics first.

**User preference**: When user asks for "software层面" optimizations, they mean macOS-side changes (DNS, proxy, system settings, interference sources) — NOT router admin page settings. Don't suggest hardware/router changes unless explicitly asked.

**User preference**: When an unknown device is found on the network, DON'T immediately flag it as a threat or suggest "someone hacked your WiFi." Identify it first (MAC vendor + ports + TTL), present findings, and ASK if the user knows the device. If they confirm ownership, pivot to security audit mode — the user wants to harden their own devices, not chase ghosts. Example: user found "FRANK-WIN" with SMB ports open → confirmed it was their own Windows laptop → wanted vulnerability assessment, not "someone is on your network."

**User preference**: When user says "who is this device" or suspects a device on their network, they want FULL identification — MAC vendor, port scan, OS fingerprint, not just "it might be a laptop". Run the complete LAN device identification workflow.

### 1. WiFi Physical Layer

```bash
system_profiler SPAirPortDataType
```

Key metrics to extract:
| Metric | Good | Warning | Bad |
|--------|------|---------|-----|
| Signal | < -50 dBm | -50 to -70 dBm | > -70 dBm |
| SNR | > 35 dB | 25-35 dB | < 25 dB |
| MCS Index | 9-11 (WiFi 6) | 5-8 | < 5 |
| Transmit Rate | > 800 Mbps | 400-800 | < 400 |

**MCS Index analysis**: MCS is the modulation level — it determines actual throughput independent of advertised link speed. Common causes of low MCS:
- Signal too weak (distance/walls)
- Co-channel interference (neighbors on same channel)
- Wide channel width (160MHz) is fragile — drops MCS faster with interference
- AWDL/AirDrop competing for 5GHz airtime

**PITFALL**: 160MHz channel width is a double-edged sword. Higher theoretical bandwidth but extremely sensitive to interference. If MCS is low (< 6) on 160MHz, switching to 80MHz often improves actual throughput by raising MCS.

### 2. LAN Stability (Router Ping Test)

```bash
# 30 packets, fast interval, check jitter
ping -c 30 -i 0.2 192.168.2.1 | tail -3
```

- 0% loss + avg < 10ms + stddev < 5ms = healthy
- stddev > 10ms = WiFi layer instability (interference, roaming, power save)

### 3. Router Identification

Many Chinese consumer routers expose a JSON API at `/api/system/deviceinfo`:

```bash
curl -s --connect-timeout 3 http://192.168.2.1/api/system/deviceinfo 2>/dev/null | python3 -m json.tool
```

Known endpoints:
| Brand | Endpoint | Key fields |
|-------|----------|------------|
| Huawei/Honor | `/api/system/deviceinfo` | `custinfo.CustDeviceName`, `devcap.Vendor`, `UpTime` |
| Xiaomi | `/api/xqsystem/router_info` | `model`, `romversion` |
| TP-Link | `/cgi-bin/luci` (OpenWrt) | redirects to web UI |
| Generic | `/api/system/routerstatus` | basic status |

### 4. Bandwidth Test

```bash
# Domestic (China) — Aliyun mirror
curl -o /dev/null -w "Speed: %{speed_download} B/s\nDNS: %{time_namelookup}s\nConnect: %{time_connect}s\nTotal: %{time_total}s\n" \
  --connect-timeout 5 --max-time 10 -s "https://mirrors.aliyun.com/ubuntu/ls-lR.gz"

# International — Google
curl -o /dev/null -w "Speed: %{speed_download} B/s\nDNS: %{time_namelookup}s\nConnect: %{time_connect}s\nTotal: %{time_total}s\n" \
  --connect-timeout 5 --max-time 10 -s "http://dl.google.com/chrome/mac/universal/stable/GGRO/googlechrome.dmg"
```

Compare domestic vs international. If domestic is fast (> 10 MB/s) but international is slow (< 1 MB/s) → ISP international routing issue, not WiFi problem.

### 5. International Routing Analysis

```bash
traceroute -m 20 -w 3 8.8.8.8
```

Look for:
- **Big latency jump** at a specific hop → bottleneck node
- **202.97.x.x** hops = China Telecom backbone
- **ctgnet** hops = China Telecom Global (international gateway)
- Routing through unexpected geography (e.g., Frankfurt before Hong Kong) = ISP routing policy issue

**PITFALL**: Ping/ICMP does NOT go through HTTP proxies (Clash, V2Ray). Traceroute shows the ISP's direct path, not the proxy path. If domestic pings are fine but HTTP browsing is slow → the proxy is the bottleneck, not the ISP.

### 6. Software Layer Check

```bash
# Active connections by process
lsof -i -n -P | grep ESTABLISHED | awk '{print $1}' | sort | uniq -c | sort -rn | head -10

# System proxy settings
scutil --proxy

# Check if proxy is intercepting DNS
lsof -i -n -P | grep ":53 " | head -5

# AWDL (AirDrop) status
ifconfig awdl0 | head -2

# Bluetooth state
system_profiler SPBluetoothDataType | grep "State"
```

**Clash Verge detection**: If `verge-mih` or `clash` appears in lsof and is listening on port 7897 (HTTP proxy) and port 53 (DNS), it's routing ALL traffic through the proxy. This is the #1 cause of "WiFi is slow" complaints that are actually proxy issues.

**Common software-layer findings**:
| Finding | Impact | Fix |
|---------|--------|-----|
| Clash/Verge system proxy active | All HTTP/DNS routed through proxy | Disable proxy or switch to rule mode |
| AWDL/AirDrop UP | Competes for 5GHz airtime | `sudo ifconfig awdl0 down` |
| Bluetooth on (no devices) | Minor 2.4G interference | `blueutil -p 0` |
| No custom DNS | Using slow router DNS | `networksetup -setdnsservers Wi-Fi 223.5.5.5 119.29.29.221` |
| Double NAT detected | Extra latency, port issues | Bridge the optical modem |

## LAN Device Identification

When user asks "what devices are on my network" or "who is this unknown device":

1. **Ping sweep** the subnet to populate ARP cache
2. **ARP table** → get MAC addresses
3. **MAC vendor lookup** → identify manufacturer (see `references/mac-oui-router-db.md`)
4. **Port scan** → fingerprint OS (445+139=Windows, 22=Linux, 5000+7000=macOS)
5. **TTL check** → OS heuristic (128=Windows, 64=Linux/macOS)

Full workflow and port signature table: `references/lan-device-fingerprinting.md`

**Key insight**: AzureWave (`F8:3D:C6`) is a WiFi module manufacturer, NOT an end-device brand. Their chips are inside laptops, smart TVs, and game consoles. Combine with port scan (SMB open → Windows laptop) to identify.

## Router & Optical Modem Security Audit

When user asks "is my router/modem hacked" or "光猫是否被劫持":

1. **DNS hijack test** — resolve nonexistent domain via router DNS, expect NXDOMAIN
2. **ARP spoofing** — check gateway has exactly one MAC
3. **HTTP injection** — fetch http://www.qq.com/ and check for injected content
4. **Port scan router** — 22/23/3389/5555 should be closed
5. **Optical modem TR-069** — port 8080 often open (ISP remote mgmt), low risk if LAN-only

Full checklist: `references/router-modem-security-checklist.md`

### Windows Device SMB Audit

When a Windows device is found on the LAN (ports 135/139/445 open), assess its SMB attack surface.
Full workflow including NetBIOS query, risk matrix, and mitigation commands: `references/windows-smb-vulnerability-audit.md`

## Pitfalls

### Proxy Interference (CRITICAL)
When Clash/V2Ray/proxy is running on `127.0.0.1`, **all local network tools timeout** because traffic gets routed through the proxy instead of directly to LAN IPs. Fix:
```bash
export no_proxy="192.168.1.0/24,10.0.0.0/8"
export NO_PROXY="$no_proxy"
# For curl:
curl --noproxy '*' http://192.168.1.1
```
If still blocked, temporarily disable the proxy in System Preferences → Network → Wi-Fi → Proxies.

### Clash Verge (verge-mih) DNS Hijacking
Clash Verge listens on port 53 (DNS) in addition to port 7897 (HTTP proxy). This means **ALL DNS queries go through Clash**, not just HTTP traffic. When diagnosing "WiFi is slow", check if `verge-mih` or `clash` processes are active:
```bash
lsof -i -n -P | grep -E "verge|clash" | grep LISTEN
```
If port 53 and 7897 both show → Clash is intercepting everything. The "28 active connections" from Clash is normal — they're local proxy pipes (127.0.0.1:7897 ↔ 127.0.0.1:*), not 28 external connections. Actual external connections go through the proxy's upstream nodes.

**Distinguishing proxy slowness from ISP slowness**: ICMP (ping/traceroute) does NOT go through HTTP proxies. If ping to 8.8.8.8 is 190ms+ → ISP routing issue. If domestic ping is fine but HTTP browsing is slow → proxy bottleneck.

### Background Processes in terminal()
`terminal()` does not support `&` backgrounding. For commands that need background processes (like `dns-sd`), use `terminal(background=true, watch_patterns=[...])` or `notify_on_complete=true`.

### airport Binary Removed (macOS 13+)
`/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport` no longer exists on macOS 13 Ventura and later. Always use `system_profiler SPAirPortDataType` as the primary WiFi info source. If you need encryption type, check the router's admin page directly.

### airport -s Permission
`airport -s` (scan nearby networks) may require root or return empty. Use `system_profiler SPAirPortDataType` as fallback.

### nc Port Scan Timeouts
`nc` to local IPs through a proxy will always timeout. Always set `no_proxy` env var first, or use `nc` with the proxy temporarily disabled.

### nc Port Scan Serial Execution
`terminal()` does not support `&` backgrounding. Port scans must run serially:
```bash
for port in 22 23 80 8080; do
  nc -z -w1 192.168.2.1 $port 2>/dev/null && echo "Port $port: OPEN" || echo "Port $port: closed"
done
```
Do NOT use `nc ... &` — it will fail with an error.

### Promiscuous Mode Interfaces
If `ifconfig | grep PROMISC` shows interfaces in promiscuous mode (common with Thunderbolt bridge interfaces `en1`/`en2`), note it in the report. These are typically set by virtualization software (Docker, VMware, UTM) and are normal if such software is installed. Flag as LOW risk if no VM software is present.

### Firewall Rule Persistence
macOS firewall (System Settings → Network → Firewall) keeps historical app rules even after the service is disabled. A process listed in the firewall UI with "允许传入连接" does NOT mean it's currently running or listening. Cross-check with `lsof -i -P -n | grep LISTEN` and `ps aux` to verify actual activity.

**User-facing clarification**: When explaining firewall findings, always distinguish between "the rule exists in the firewall list" (historical) vs "the process is actively listening" (current risk). Users often confuse the two — e.g., "ToDesk is listed in my firewall but I uninstalled it." Check `/Applications/` and `ps aux` before declaring something active.

### Sharing Services ≠ AirDrop
Users commonly confuse macOS file sharing (smbd) with AirDrop. They are completely different:
- **smbd** = SMB file sharing, managed in System Settings → General → Sharing → File Sharing. Uses SMB protocol, exposes folders to LAN.
- **AirDrop** = Apple's AWDL protocol, peer-to-peer, requires acceptance.

When smbd appears in the firewall list but Sharing is off → the firewall rule is historical, the service is not active. Always verify with System Settings → General → Sharing (all toggles).

### 2.4GHz-Only WiFi
If `system_profiler SPAirPortDataType` shows `PHY Mode: 802.11n` and `Channel:` in the 2.4GHz range (1-13), the connection is on 2.4GHz only. This is weaker than 5GHz/6GHz (WiFi 6/6E/7) in both speed and resistance to interference. Note it as a finding but not a security vulnerability per se.

## Report Template

Structure findings as:
1. **Router Info** — brand, model, firmware, encryption
2. **Security Checks** — DNS/ARP/routing/proxy/VPN (✅/⚠️/❌)
3. **Connected Devices** — count + identify unknowns
4. **Local Machine** — remote access tools, sniffers, MDM
5. **Recommendations** — prioritized action items
