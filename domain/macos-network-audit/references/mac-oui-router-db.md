# Common Router MAC OUI Database

Use to identify router manufacturer from the first 3 octets of the gateway MAC.

## Major Manufacturers

| OUI Prefix | Vendor | Notes |
|---|---|---|
| 10:47:E7 | Huawei (华为) | Common in China Mobile bundles |
| 20:6B:E7 | Huawei | |
| C4:07:2F | Huawei | |
| 48:46:FB | Huawei | |
| 00:E0:FC | Huawei | Older models |
| AC:84:C6 | TP-Link | |
| 5C:E9:31 | TP-Link | |
| E8:48:B8 | TP-Link | |
| 54:A0:50 | ASUS | |
| 04:D4:C4 | ASUS | |
| EC:F4:BB | D-Link | |
| 14:91:82 | Belkin | |
| CC:40:D0 | Netgear | |
| 9C:3D:CF | Netgear | |
| 60:A4:4C | Netgear | |
| 00:1A:2B | Ruijie (锐捷) | China ISP bundles |
| 88:66:A5 | Xiaomi (小米) | |
| 78:11:DC | Xiaomi | |
| 58:41:20 | Tenda (腾达) | |
| 50:BD:5F | ZTE (中兴) | China ISP bundles |

## Red Flags

- Gateway MAC OUI doesn't match the visible router brand → possible firmware replacement or rogue AP
- Locally-administered MAC on gateway (2nd hex digit is 2/6/A/E) → MAC spoofed, investigate
- Multiple different MACs responding to gateway IP → ARP spoofing / MITM

## Locally Administered Addresses (LAA)

A MAC address is "Locally Administered" (not hardware-burned) if bit 1 of the first octet is set. Quick check: if the **second hex character** of the first octet is **2, 6, A, or E**, it's a LAA.

| First Octet | LAA? | Example |
|---|---|---|
| 00, 08, 10, 20, 30, 40, 50, 60, 70, 80, 90, A0, B0, C0, D0, E0, F0 | No | 10:47:E7 (Huawei) |
| 02, 06, 0A, 0E, 12, 16, ... | Yes | 7a:a3:7d (unknown), 4a:ea:04 (unknown) |

**Common LAA sources:**
- **macOS/iOS**: Private WiFi Address feature (Settings → Wi-Fi → tap network → Private Address). On by default since iOS 14 / macOS Sequoia.
- **Android**: MAC randomization (on by default since Android 10).
- **Virtual machines**: VMware, UTM, Docker generate LAA MACs.
- **Hotspot tethering**: Phone hotspots often use LAA MACs.

**Why it matters for device identification:** LAA devices cannot be identified by OUI lookup. The only way to identify them is through the router's DHCP client list (hostname), or by checking which device in the house is currently on WiFi.

## Default Router Credentials (for checking if unchanged)

| Brand | Default IP | Username | Password |
|---|---|---|---|
| Huawei | 192.168.1.1 / 192.168.3.1 | admin | admin / printed on label |
| TP-Link | 192.168.1.1 / tplinkwifi.net | admin | admin / user-set |
| ASUS | 192.168.1.1 / router.asus.com | admin | admin |
| Xiaomi | 192.168.31.1 | (none) | (printed on label) |
| Netgear | 192.168.1.1 / routerlogin.net | admin | password |
| Tenda | 192.168.0.1 | admin | admin |

⚠️ If default credentials still work on a rental network → previous tenant could still access router admin.
