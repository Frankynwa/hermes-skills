# LAN Device Fingerprinting

Identify unknown devices on the local network using macOS tools. No special software required.

## Workflow

```
1. Ping sweep → 2. ARP cache refresh → 3. MAC vendor lookup → 4. Port scan → 5. OS fingerprint
```

## Step 1: Ping Sweep + ARP Refresh

ARP cache only shows recently-communicated devices. Ping sweep populates it:

```bash
# Serial sweep (slower but reliable)
for i in $(seq 1 254); do
  ping -c 1 -W 1 192.168.2.$i >/dev/null 2>&1 && echo "192.168.2.$i: ALIVE"
done
# Then refresh ARP
arp -a | grep -v incomplete | grep -v mcast
```

**PITFALL**: `terminal()` does not support `&` backgrounding. Don't try to parallelize with `&` — use serial loops or `execute_code` with `concurrent.futures`.

**PITFALL**: Devices may appear and disappear between scans (sleep, power save, roaming). A device that was alive 2 minutes ago but doesn't respond now is normal — re-sleep is not evidence of malicious behavior. Run the full identification workflow while the device is alive.

## Step 2: MAC Vendor (OUI) Lookup

First 3 octets identify the NIC manufacturer (not necessarily the end device):

```bash
# Via API (rate-limited: ~5 requests total, then returns 429 "Too Many Requests")
curl -s "https://api.macvendors.com/f8:3d:c6:af:6d:f4"
# → "AzureWave Technology Inc."
```

**PITFALL**: macvendors.com rate limit is aggressive — about 5 requests total before getting 429. When identifying many devices, batch the unknown MACs and look up only the most suspicious ones. Fallback: manually check OUI prefix against known tables in `references/mac-oui-router-db.md`.

### Common Device OUIs

| OUI | Vendor | Likely Device |
|---|---|---|
| `30:AA:E4` | Huawei | Router / Honor device |
| `F8:75:88` | Huawei | Phone / tablet / IoT |
| `CC:4D:75` | Xiaomi | Phone / smart home |
| `D4:E8:53` | Hikvision (海康威视) | Camera / NVR |
| `F8:3D:C6` | AzureWave | WiFi module in laptop/TV/console |
| `B0:F1:A3` | Apple | iPhone / iPad (real MAC) |
| `5E:28:61` | Apple (LAA) | macOS private WiFi address |

### Locally Administered Addresses (LAA)

MAC where second hex digit of first octet is **2, 6, A, or E** = software-generated, not hardware. Cannot be identified by OUI. Common in:
- iOS/macOS private WiFi address (default since iOS 14)
- Android MAC randomization (default since Android 10)
- VMs, Docker, phone hotspots

To identify LAA devices, check router DHCP client list via admin page (shows hostname).

## Step 3: Port Scan for OS/Service Fingerprinting

```bash
# Key fingerprinting ports
for port in 22 23 80 135 139 443 445 548 3389 5000 7000 8080 9100; do
  nc -z -w1 <TARGET_IP> $port 2>/dev/null && echo "Port $port: OPEN" || echo "Port $port: closed"
done
```

### Port Signature → Device Type

| Open Ports | OS / Device Type | Confidence |
|---|---|---|
| **445 + 139** | Windows (SMB file sharing) | High |
| 445 + 139 + 3389 | Windows with RDP | High |
| 22 (SSH) | Linux / macOS / NAS | Medium |
| 80 + 443 (web) | IoT / camera / router | Medium |
| 80 only | Router / simple IoT | Medium |
| 5000 + 7000 | macOS (AirPlay receiver) | High |
| 9100 | Network printer | High |
| 62078 | iPhone (iTunes sync) | High |
| 5353 (mDNS) | Smart home device | Medium |

### OS Fingerprinting via TTL

```bash
ping -c 1 -t 3 <TARGET_IP>
# Look at TTL in response
```

| TTL | Likely OS |
|---|---|
| 64 | Linux / macOS / Android |
| 128 | Windows |
| 255 | Cisco / network equipment |

**PITFALL**: TTL is a heuristic, not definitive. Some embedded devices use TTL 128 or 64 arbitrarily. Cross-reference with port scan results.

**PITFALL**: AzureWave (`F8:3D:C6`) is a WiFi module manufacturer, NOT an end-device brand. Their chips are inside laptops, smart TVs, and game consoles. A device with AzureWave MAC + ports 445/139 open + TTL 128 = Windows laptop with AzureWave WiFi card.

## Step 4: Service Banner Grabbing

```bash
# SMB banner (Windows device name)
echo "" | nc -w2 <IP> 445 2>/dev/null | xxd | head -5

# HTTP banner
curl -s -I --connect-timeout 2 http://<IP>/ 2>/dev/null | head -10

# SSH version
nc -w2 <IP> 22 2>/dev/null | head -1
```

## Step 5: mDNS / NetBIOS Name Resolution

```bash
# macOS mDNS discovery
dns-sd -B _services._dns-sd._udp local 2>/dev/null &
# (use terminal(background=true) since terminal() doesn't support &)

# SMB name lookup (macOS built-in)
smbutil lookup <IP>

# NetBIOS name query (if nbtscan installed)
nbtscan <IP>
```

**PITFALL**: `smbutil lookup` returns "No route to host" when the target device is temporarily unreachable (sleeping, disconnected). This is NOT a network routing error — it means the device is offline. Re-check after the device wakes up.

## Putting It All Together: Device Identification Matrix

Example from a real audit:

| IP | MAC | Vendor | Ports | TTL | Identity |
|---|---|---|---|---|---|
| .1 | 30:AA:E4 | Huawei | 80 | 64 | 荣耀路由器 |
| .4 | F8:75:88 | Huawei | — | 64 | 华为手机 |
| .28 | D4:E8:53 | Hikvision | — | — | 海康摄像头 |
| .29 | CC:4D:75 | Xiaomi | — | — | 小米手机/IoT |
| .30 | A2:A4:55 | (LAA/random) | — | — | 手机(隐私MAC) |
| .100 | F8:3D:C6 | AzureWave | 445,139 | 128 | Windows笔记本 |
| .104 | 0E:92:49 | (LAA/random) | — | — | 手机(隐私MAC) |
| .105 | 5E:28:61 | Apple(LAA) | — | 64 | 本机Mac |

## Red Flags During Device Scan

- **Unknown device with open SMB (445/139)** → Could be compromised Windows machine or rogue NAS
- **Unknown device with SSH (22) open** → Could be planted backdoor device
- **Device not matching any known household item** → Neighbor on your WiFi
- **Multiple IPs sharing same MAC** → ARP spoofing attack
- **LAA MAC on a device you don't recognize** → Could be spoofed identity
