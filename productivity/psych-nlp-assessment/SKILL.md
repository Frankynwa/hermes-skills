---
name: psych-nlp-assessment
description: 中文心理语言学特征提取 — 从对话文本中评估依恋维度、图式激活、IFS部分活跃度。用于心理自我觉察和纵向追踪。
version: 0.1.0
tags: [psychology, nlp, assessment, ifs, schema-therapy, attachment, chinese]
---

# psych-nlp-assessment

从中文自然语言中提取心理特征，支持依恋维度、图式激活、IFS部分活跃度三个维度的评估。

## 项目位置

- 代码: `~/projects/psych-nlp/src/psych_nlp/`
- 基线数据: `~/projects/psych-nlp/data/baseline.py`
- 追踪数据: `~/projects/psych-nlp/data/tracking/assessment_history.json`
- MiroFish: `~/projects/mirofish/mirofish.py` (v3 整合版)

## 快速使用

### 1. 词典匹配评估（快速，无需API）

```python
import sys
sys.path.insert(0, "/Users/wangruifan/projects/psych-nlp/src")
from psych_nlp import PsychAnalyzer

analyzer = PsychAnalyzer()
result = analyzer.analyze("用户的文本")
print(result.format_report())
```

### 2. LLM评估（精细，需要API）

```python
from psych_nlp.llm_assessor import LLMPsychAssessor

assessor = LLMPsychAssessor()
result = assessor.assess("用户的文本", context="额外背景信息")
print(result.insight)
```

### 3. 纵向追踪

```python
from psych_nlp.tracking import LongitudinalTracker

tracker = LongitudinalTracker()
tracker.add_assessment(profile)  # 保存一次评估
print(tracker.generate_report(days=7))  # 生成趋势报告
```

### 4. MiroFish pipeline（评估+模拟）

```bash
cd ~/projects/mirofish
python3 mirofish.py --pipeline "用户的一段话" --dialogue --rounds 2
```

## 评估维度

### 依恋维度 (ECR-R标准)
- **焦虑**: 第一人称单数↑、绝对化词↑、负面情感↑、躯体化↑
- **回避**: 认知加工词↑、情感词↓、模糊限定词↑、第三人称↑
- **恐惧-回避型**: 焦虑高 + 回避高

### 图式激活 (YSQ-S3标准, 8个图式)
- 情感抑制: 情感词少、模糊限定多、抽象化
- 苛刻标准: 认知词多、"应该/必须"多
- 情感剥夺: "没人理解"、情感需求未满足
- 被遗弃: 孤独、被抛弃恐惧
- 缺陷/羞耻: 自我贬低、不配感
- 过度警惕: 负面预期、焦虑
- 依赖/能力不足: "做不到"
- 易受伤害: 害怕灾难

### IFS部分活跃度
- **保护者**: 控制、分析、延迟行动
- **消防者**: 逃避、转移注意力、新目标
- **被流放者**: 情感词汇、脆弱表达、过去指向
- **Self**: 觉察、好奇、接纳、平衡

## 学术依据

- Pennebaker (2015): LIWC2015
- Slatcher & Pennebaker (2006): 依恋语言标记
- Wahle et al. (2022): 治疗文本中不安全依恋标记
- Newell et al. (2021): EMS与语言模式
- Brockmeyer et al. (2015): 图式治疗语言分析
- Binz & Schulz (2023): LLM are effective psychologists
- Ghandeharioun et al. (2024): Google Research, LLM心理评估

## 用户基线

用户基线数据在 `~/projects/psych-nlp/data/baseline.py`:
- 依恋类型: 恐惧-混乱型 (焦虑3.5/回避4.5)
- 最高图式: 情感抑制(5.33) > 苛刻标准(4.67) > 过度警惕(4.00)
- 核心冲突: 情感抑制×情感剥夺, 苛刻标准×被遗弃

## 飞书集成

评估结果自动写入飞书多维表格：
- Base Token: `ZwMYbYAUzaXA0lslFq3cpWX1n7d`
- Table ID: `tbltofj0u15tyzQ2`
- 链接: https://my.feishu.cn/base/ZwMYbYAUzaXA0lslFq3cpWX1n7d
- 16个字段：焦虑/回避/情感抑制/苛刻标准/情感剥夺/被遗弃/保护者/消防者/被流放者/Self/内部冲突/主导部分/综合洞察/来源/日期/文本

写入方式：
```python
from psych_nlp.feishu_writer import FeishuWriter
writer = FeishuWriter()
writer.write_assessment(profile, text_preview="...", source="词典匹配")
```

## 每日脚本

两个日常分析脚本位于 `~/projects/psych-nlp/scripts/`：

### analyze_daily_reflection.py — 每日反思分析
```bash
cd ~/projects/psych-nlp && PYTHONPATH=src python3 scripts/analyze_daily_reflection.py
```
分析当日回复数据。无数据时输出"暂无回复数据。"

### daily_summary.py — 每日汇总报告
```bash
cd ~/projects/psych-nlp && PYTHONPATH=src python3 scripts/daily_summary.py
```
生成心理追踪周报（最近7天趋势）。输出格式：
```
## 📈 心理追踪周报
⚠️ 最近7天只有N条记录，至少需要2条。
📊 本周共 N 次评估
```

### 依赖
- `jieba` — `basic.py` 导入时需要。项目无 requirements.txt / setup.py，需手动安装：
  ```bash
  python3 -m ensurepip --upgrade && python3 -m pip install jieba
  ```

## 定时任务

每天 22:00 自动汇总趋势推送到飞书（cron job ID: 587d70de93d9）。
汇总内容：依恋维度趋势、IFS活跃度、主导部分统计、高频图式、显著变化预警。

## MiroFish v3 整合

MiroFish v3 位于 `~/projects/mirofish/mirofish.py`，已整合 psych-nlp：
- `--pipeline "文本"` — 一键完成 评估→模拟→报告
- `--analyze` — 模拟前先做心理评估
- Agent prompt 根据评估结果动态调整（依恋分数、图式激活、IFS活跃度注入 prompt）

## Pitfall: lark-cli 字段创建

lark-cli 1.0.39 不支持 `property` key 创建 select 字段的选项。
解决方案：先创建不带选项的 select 字段，后续再通过 UI 添加选项。
```bash
# 正确方式
lark-cli base +field-create --base-token TOKEN --table-id TID --as bot --json '{"name":"主导部分","type":"select"}'
# 错误方式（会报 Unrecognized key 'property'）
lark-cli base +field-create ... --json '{"name":"主导部分","type":"select","property":{"options":[...]}}'
```

## Pitfall: SQLite json 操作超时

在 `execute_code` 中用长 SQLite 命令操作 JSON 可能超时。
解决方案：用 `terminal()` 直接调用，或在 Python 中用 `subprocess.run()` 代替。

## 注意事项

1. 这不是诊断工具，是自我觉察工具
2. 词典匹配是粗粒度，LLM评估更精细但需要API
3. 恐惧-回避型用户可能系统性低估自己的痛苦程度
4. 建议每3个月做一次问卷校准
5. 评估数据属于敏感个人信息，本地存储不上传
