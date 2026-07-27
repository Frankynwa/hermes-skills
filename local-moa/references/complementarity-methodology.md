# 模型互补性分析——完整方法论

## 理论依据

CORE 论文 (Mishra et al. 2026.01) 的四象限矩阵：

| | 模型 B 好 | 模型 B 差 |
|---|---|---|
| 模型 A 好 | 双好 | A 独好 |
| 模型 A 差 | B 独好 | 双差 |

互补性 = (A 独好 + B 独好) / 总题数

判决标准：
- >20%：强互补，MoA 物有所值
- 5-20%：弱互补，偶尔有用
- <5%：冗余，单模型即可

## 为什么需要交叉验证裁判

单裁判存在自偏好效应，已在实测中证实：

- DeepSeek 裁判给自己 -1 净胜（自我批评）
- Qwen 裁判给自己 +4 净胜（明显偏袒）
- MiniMax 裁判给自己 +1 净胜（轻微偏好）

结论：必须用 2+ 裁判交叉验证。取不同裁判间的最大公约数——两位裁判给出的互补率偏差 <15% 且均 >20% = 稳定互补。

## 实测脚本

```bash
# 1. 重新生成测试题（可选）
python3 ~/scripts/model_complementarity.py --prepare

# 2. 所有模型答题（耗时 2-5 分钟，并行）
python3 ~/scripts/model_complementarity.py --run

# 3. 自动评判（默认 DeepSeek 做裁判，也支持 --judge qwen）
python3 ~/scripts/model_complementarity.py --judge

# 4. 输出报告
python3 ~/scripts/model_complementarity.py --report
```

## 已知问题

- 裁判匿名化不完美：BERTScore 等工具可以识别模型"指纹"
- 长答案可能被截断，Q1 因答案过长被 MiniMax 返回 both_bad
- 15 题样本量对统计学显著来说偏小，但对工程决策足够
