# MiroFish + psych-nlp Integration

## Architecture

```
用户自然语言输入
    ↓
PsychAnalyzer.analyze(text)
    ↓ PsychProfile (attachment + schema + ifs scores)
    ↓
build_dynamic_agent_prompt(agent_id, profile)
    ↓ Inject assessment context into each agent's prompt
    ↓
LLM simulation (4 agents react + interact)
    ↓
Report (assessment + simulation + pattern analysis)
```

## Dynamic Prompt Injection

Each agent's base prompt is augmented with assessment context:

```python
def build_dynamic_agent_prompt(agent_id: str, profile) -> str:
    context_parts = []
    if profile.attachment.anxiety_score >= 2.5:
        context_parts.append(f"【当前状态提示】依恋焦虑较高（{score}/5），可能正在经历不安全感...")
    if profile.schema.top_score >= 2.0:
        context_parts.append(f"【当前状态提示】「{schema}」图式正在被激活...")
    if profile.ifs:
        context_parts.append(f"【当前状态提示】当前主导部分：{part}（{score}/5）...")
    
    return f"{context_text}\n\n{base_prompt}"
```

## CLI Modes

```bash
# Basic simulation (no psych-nlp)
python3 mirofish.py -s "场景描述"

# Assessment + simulation
python3 mirofish.py -s "场景描述" --analyze

# Full pipeline (recommended)
python3 mirofish.py --pipeline "用户的一段话"
python3 mirofish.py --pipeline "用户的一段话" --dialogue --rounds 2
```

## Key Insight: Emergence

The power of this integration is that **agent interactions produce emergent patterns** that neither psych-nlp nor MiroFish alone can generate. Example:

- psych-nlp detects emotional inhibition (3.32/5) and protector dominance (2.81/5)
- These scores are injected into agent prompts
- The exile agent, knowing the protector is strong, finds a different voice
- The resulting dialogue reveals patterns the user couldn't see by introspection alone

## Implementation Files

- psych-nlp engine: `~/projects/psych-nlp/src/psych_nlp/`
- MiroFish v3: `~/projects/mirofish/mirofish.py`
- User baseline: `~/projects/psych-nlp/data/baseline.py`
- Reports: `~/projects/mirofish/reports/`
