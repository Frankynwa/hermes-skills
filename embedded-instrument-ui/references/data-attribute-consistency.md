# Data-* Attribute Consistency for Chinese-Localized UIs

## The Pattern

When localizing a UI that uses `data-*` attributes for DOM lookup,
keep `data-*` values in English but translate display text via a
lookup map.

## Why This Matters

If you translate `data-*` values to Chinese, the event listeners that
use `document.getElementById()` or DOM querying will break because
DOM IDs are in English.

## Correct Pattern (All Tab Systems)

### 1. Overview Tabs
```javascript
var T = ['Realtime','Record','Trend','Table','Verify'];  // English IDs
// Button rendering:
'.map(function(t){return `<button data-tab="${t}">` +
  ({'Realtime':'实时','Record':'记录','Trend':'趋势','Table':'表格','Verify':'验证'})[t] +
  '</button>'})'
// Event listener:
T.forEach(function(t) {
  var el = document.getElementById('ov-'+t); // ov-Realtime, ov-Record, etc.
  // ...
});
```

### 2. Settings Tabs
```javascript
var TT = ['Instrument','Communication','Tools','Info','Memory'];
// Display: {'Instrument':'仪器','Communication':'通信','Tools':'工具','Info':'信息','Memory':'存储'}
// DOM IDs: s-Instrument, s-Communication, s-Tools, s-Info, s-Memory
```

### 3. Info Subtabs
```javascript
['Overview','License','Comm','Sensor','OSS','RadioCert']
// Display: {'Overview':'概览','License':'许可','Comm':'通信','Sensor':'传感器','OSS':'开源','RadioCert':'无线电认证'}
// DOM IDs: si-Overview, si-License, si-Comm, si-Sensor, si-OSS, si-RadioCert
```

### 4. Trends Tabs
```javascript
var tabs = ['Flicker','Unbalance','Current'];
// Display: {'Flicker':'闪变','Unbalance':'不平衡','Current':'电流'}
// DOM IDs: tr-Flicker, tr-Unbalance, tr-Current
```

### 5. Config Panels
```javascript
var panels = ['连接','标称电压','电压比','电流比','闪变','K系数','星形限值','骤降','骤升','中断','波形偏差','瞬变','标称频率','快速电压变化','浪涌'];
// Same array used for both data-cftab AND DOM getElementById('cf-'+p)
// OK because DOM IDs are dynamically set to match: <div id="cf-连接">
```

## Events Filter — Special Case
Events filter uses Chinese for both `data-filter` AND the comparison because
the event data rows also use Chinese type values:
```javascript
data-filter="全部" / data-filter="骤降" / etc.
f === '全部'    // comparison uses Chinese
data-type="骤降" // data rows use Chinese
```

## Verification Checklist
After translation, verify each tab system:
```bash
grep -n "data-tab\|data-stab\|data-sitab\|data-trtab\|data-cftab" ui_prototype.js
grep -n "getElementById.*ov-\|getElementById.*s-\|getElementById.*si-\|getElementById.*tr-\|getElementById.*cf-" ui_prototype.js
```
The `data-*` values must match the suffix after `getElementById('...-...')`.
