# Router API Endpoints & Identification

Identify router brand/model via HTTP API when physical access isn't available.

## Huawei / Honor (荣耀)

**Device Info**: `GET http://192.168.x.1/api/system/deviceinfo`
```json
{
  "DeviceName": "Honor",
  "custinfo": {
    "CustDeviceName": "XD21-10",
    "CustDeviceBand": 2,
    "CustZHFriendlyName": "荣耀路由XD21"
  },
  "devcap": {
    "Vendor": "HUAWEI",
    "RebootTime": 48
  },
  "UpTime": 514145
}
```

- `devcap.isSupport80211AX`: 1 = WiFi 6 capable
- `devcap.isSupportWpa3`: 1 = WPA3 capable
- `UpTime`: seconds since last reboot
- `RouterType`: "router_4" etc. — identifies product line

**Router Status**: `GET /api/system/routerstatus`
```json
{"isrepeater": false, "issupportsmartapp": false, "guide": true}
```

**OUI Fingerprint**: `30:AA:E4` = Huawei router MAC prefix

## Xiaomi

**Device Info**: `GET http://192.168.31.1/api/xqsystem/router_info`
- Default subnet: 192.168.31.x
- Returns model, ROM version, hardware version

## TP-Link

**Default**: `192.168.0.1`
- Web UI at `/` — no standard API
- Some models use `/cgi-bin/luci` (OpenWrt-based)

## Common Chinese ISP Optical Modems (光猫)

| ISP | Default IP | Brand |
|-----|-----------|-------|
| China Telecom | 192.168.1.1 | Huawei HG8245 / ZTE F673 |
| China Mobile | 192.168.1.1 | Huawei / FiberHome |
| China Unicom | 192.168.1.1 | ZTE / Huawei |

**Dual-NAT Detection**:
```bash
# Check if optical modem is reachable at common IPs
for ip in 192.168.0.1 192.168.1.1 192.168.2.1 10.0.0.1 10.0.0.138; do
  ping -c 1 -W 1 $ip 2>/dev/null | grep "bytes from" && echo "$ip REACHABLE"
done
```

Multiple reachable gateways = double NAT. Traceroute confirms:
```
1  192.168.2.1   (your router)
2  192.168.1.1   (optical modem) ← double NAT indicator
3  10.x.x.x      (ISP internal)
```

## Identifying Unknown Routers

1. **OUI lookup**: First 3 octets of MAC → https://macvendors.com
2. **HTTP fingerprint**: `curl -s http://192.168.x.1/ | grep -i "title\|vendor\|model"`
3. **TTL heuristic**: Ping the gateway, check TTL
   - TTL 64 = Linux-based (OpenWrt, most Chinese routers)
   - TTL 128 = Windows/embedded
   - TTL 255 = Cisco/networking equipment
