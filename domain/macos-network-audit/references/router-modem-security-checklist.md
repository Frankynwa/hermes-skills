# Router & Optical Modem Security Audit

Deep security checks for the network gateway, beyond basic port scanning.

## Quick Checklist

```bash
# 1. DNS hijack test (non-existent domain)
nslookup thisdomainshouldnotexist12345abc.com 192.168.2.1
# Should return NXDOMAIN. If it returns an IP → DNS hijacked!

# 2. ARP spoof check
arp -a | grep "192.168.2.1"  # Should be exactly one MAC

# 3. Router port scan
for port in 22 23 80 8080 3389 5555; do
  nc -z -w1 192.168.2.1 $port 2>/dev/null && echo "Port $port: OPEN"
done

# 4. HTTP injection test
curl -s -D- --connect-timeout 3 http://www.qq.com/ | head -10
```

## DNS Hijack Detection

### Non-Existent Domain Test
```bash
nslookup thisdomainshouldnotexist12345abc.com 192.168.2.1
nslookup thisdomainshouldnotexist12345abc.com 223.5.5.5
```
If router returns an IP for nonexistent domain → DNS hijacking confirmed.

### Cross-Resolver Comparison
```bash
for domain in www.baidu.com www.alipay.com www.icbc.com.cn; do
  echo "Router: $(nslookup $domain 192.168.2.1 2>/dev/null | grep 'Address:' | tail -1)"
  echo "AliDNS: $(nslookup $domain 223.5.5.5 2>/dev/null | grep 'Address:' | tail -1)"
done
```

**PITFALL**: Different IPs for same domain = normal CDN behavior. Only flag if ALL domains resolve to same suspicious IP.

## HTTP Injection Detection

```bash
curl -s -D- --connect-timeout 3 http://www.qq.com/ | head -20
```
Look for: injected JavaScript, unexpected 302 redirects to ad pages, modified Content-Length.

## Optical Modem (光猫) Checks

### TR-069 Remote Management
```bash
nc -z -w1 192.168.1.1 8080 && echo "TR-069 EXPOSED"
curl -s --connect-timeout 3 http://192.168.1.1:8080/ | head -10
# Typical: "Powered by Jetty" 404 = TR-069 service
```

### Modem Port Scan
```bash
for port in 80 443 8080 22 23; do
  nc -z -w1 192.168.1.1 $port 2>/dev/null && echo "Port $port: OPEN"
done
```

Red flags: SSH/Telnet open (debug interface), no HTTPS (plaintext credentials).

## Router Port Interpretation

| Port | Risk if Open |
|---|---|
| 22 (SSH) | HIGH - possible backdoor |
| 23 (Telnet) | HIGH - unencrypted |
| 8080 | MEDIUM - alt management |
| 3389 (RDP) | HIGH - remote desktop |
| 5555 (ADB) | HIGH - Android debug |

## Router API Probing

```bash
for path in "/api/system/deviceinfo" "/api/system/routerstatus" \
  "/api/xqsystem/router_info" "/cgi-bin/luci"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 2 "http://192.168.2.1${path}")
  echo "${path} -> HTTP ${code}"
done
```

See `references/router-api-and-identification.md` for response parsing.
