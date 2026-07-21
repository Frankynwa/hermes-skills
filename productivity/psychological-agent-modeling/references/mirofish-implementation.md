# MiroFish Implementation Reference

## Architecture (v2)

Single-file Python script (`~/projects/mirofish/mirofish.py`) with OpenAI SDK connecting to MiMo V2.5 Pro.
GitHub: `Frankynwa/mirofish` (private).

### Two Simulation Modes

1. **Single-round** (`run_single_round`): Each agent reacts independently. Self then integrates. Quick snapshots.
2. **Dialogue mode** (`run_dialogue --rounds N`): Agents see each other's responses over multiple rounds. Reveals inter-part conflicts. More revealing than single-round.

### Agent Roles

| Agent | IFS Role | Core Belief | Behavior |
|-------|----------|-------------|----------|
| 🛡️ Protector | Manager | "Only control is safe" | Analysis, planning, delay action |
| 🚒 Firefighter | Firefighter | "Pain is intolerable" | Impulse, fantasy, distraction |
| 🏚️ Exile | Exile | "I'm not worthy of love" | Carries abandonment fear, shame |
| 👁️ Self | Orchestrator | 8 C's (calm, curious, etc.) | Observes all parts, no judgment |

### Preset Scenarios (8)

| Category | Key | Title |
|----------|-----|-------|
| 关系 | breakup | 分手后 |
| 关系 | new_relationship | 新的可能 |
| 关系 | friend_vulnerability | 朋友的关心 |
| 方向 | career_choice | 选择困境 |
| 方向 | meaning_crisis | 意义危机 |
| 日常 | procrastination | 拖延 |
| 日常 | perfectionism | 完美主义 |
| 日常 | comparison | 比较 |

### Output

Reports auto-save to `~/projects/mirofish/reports/sim_YYYYMMDD_HHMMSS.md`.

## MiMo API Pitfalls (Confirmed 2026-06)

1. **Empty responses with system+user split**: MiMo V2.5 Pro frequently returns empty with `role: "system"` + `role: "user"`. Fix: combine into single `role: "user"` message. Add fallback retry.
2. **API key not in config.yaml**: Config masks keys as "***". Read from `~/.hermes/.env`: `XIAOMI_API_KEY=tp-crv...` (51 chars).
3. **Random empty responses**: Even with fix, some agents occasionally return empty. Model-level issue. Guard with `if content and content.strip()`.
4. **temperature=0.85, max_tokens=400**: Best balance. 0.8/300 too constrained.

## Known Real Outputs (Breakup Scenario)

**消防者**: "（抓起手机划屏幕）独处时那些情绪涌上来真是烦人，我们不如去打两把游戏？"

**被流放者**: "他们说你像一堵墙，可他们不知道——这堵墙是我帮你建的，很早很早以前。我只是不想再证明自己了。有时候我希望有人能看穿这堵墙，看到后面那个不知所措的我。"

**保护者 (Round 2)**: "我统计过，情绪波动的平均时长是7分23秒。墙必须存在，这是保护机制。但...或许我们可以为情绪安装一个计时器的阀门。"

The "但..." is the key moment — defense starting to soften.

## No Persistent Memory

Each simulation run is independent. No memory between runs. This is intentional — the user observes patterns across runs manually.
