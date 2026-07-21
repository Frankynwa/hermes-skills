---
name: systematic-debugging
description: "4-phase root cause debugging: understand bugs before fixing."
version: 1.1.0
author: Hermes Agent (adapted from obra/superpowers)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [debugging, troubleshooting, problem-solving, root-cause, investigation]
    related_skills: [test-driven-development, writing-plans, subagent-driven-development]
---

# Systematic Debugging

## Overview

Random fixes waste time and create new bugs. Quick patches mask underlying issues.

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

**Violating the letter of this process is violating the spirit of debugging.**

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed Phase 1, you cannot propose fixes.

## When to Use

Use for ANY technical issue:
- Test failures
- Bugs in production
- Unexpected behavior
- Performance problems
- Build failures
- Integration issues

**Use this ESPECIALLY when:**
- Under time pressure (emergencies make guessing tempting)
- "Just one quick fix" seems obvious
- You've already tried multiple fixes
- Previous fix didn't work
- You don't fully understand the issue

**Don't skip when:**
- Issue seems simple (simple bugs have root causes too)
- You're in a hurry (rushing guarantees rework)
- Someone wants it fixed NOW (systematic is faster than thrashing)

## The Four Phases

You MUST complete each phase before proceeding to the next.

---

## Phase 1: Root Cause Investigation

**BEFORE attempting ANY fix:**

### 1. Read Error Messages Carefully

- Don't skip past errors or warnings
- They often contain the exact solution
- Read stack traces completely
- Note line numbers, file paths, error codes

**Action:** Use `read_file` on the relevant source files. Use `search_files` to find the error string in the codebase.

### 2. Reproduce Consistently

- Can you trigger it reliably?
- What are the exact steps?
- Does it happen every time?
- If not reproducible → gather more data, don't guess

**Action:** Use the `terminal` tool to run the failing test or trigger the bug:

```bash
# Run specific failing test
pytest tests/test_module.py::test_name -v

# Run with verbose output
pytest tests/test_module.py -v --tb=long
```

### 3. Check Recent Changes

- What changed that could cause this?
- Git diff, recent commits
- New dependencies, config changes

**Action:**

```bash
# Recent commits
git log --oneline -10

# Uncommitted changes
git diff

# Changes in specific file
git log -p --follow src/problematic_file.py | head -100
```

### 3b. VERIFY PRE-EXISTING vs INTRODUCED (CRITICAL)

**When a bug appears after your changes, NEVER assume it's your fault.** The most expensive debugging mistake is fixing pre-existing bugs as if you introduced them.

**Mandatory step:** Revert your changes to the affected component and re-test.

```bash
# Option A: git stash + test
git stash
# run the failing test / trigger the bug
git stash pop

# Option B: manual revert of specific changes
# Edit the file to restore original values, rebuild, test
```

**Decision tree:**
- Bug still reproduces after revert → **PRE-EXISTING.** Document it, don't fix in this session unless asked.
- Bug disappears after revert → **YOUR change introduced it.** Binary-search your diff to isolate.

**Why this matters:** In one session, 2 hours were wasted trying to fix a "Config page freeze" before discovering it was a pre-existing LVGL reentrancy bug. The user's frustrated "你做的很差劲" was correct — the approach was wrong. Reverting first would have taken 5 minutes.

### 4. Gather Evidence in Multi-Component Systems

**WHEN system has multiple components (API → service → database, CI → build → deploy):**

**BEFORE proposing fixes, add diagnostic instrumentation:**

For EACH component boundary:
- Log what data enters the component
- Log what data exits the component
- Verify environment/config propagation
- Check state at each layer

Run once to gather evidence showing WHERE it breaks.
THEN analyze evidence to identify the failing component.
THEN investigate that specific component.

### 5. Trace Data Flow

**WHEN error is deep in the call stack:**

- Where does the bad value originate?
- What called this function with the bad value?
- Keep tracing upstream until you find the source
- Fix at the source, not at the symptom

**Action:** Use `search_files` to trace references:

```python
# Find where the function is called
search_files("function_name(", path="src/", file_glob="*.py")

# Find where the variable is set
search_files("variable_name\\s*=", path="src/", file_glob="*.py")
```

### Phase 1 Completion Checklist

- [ ] Error messages fully read and understood
- [ ] Issue reproduced consistently
- [ ] Recent changes identified and reviewed
- [ ] Evidence gathered (logs, state, data flow)
- [ ] Problem isolated to specific component/code
- [ ] Root cause hypothesis formed

**STOP:** Do not proceed to Phase 2 until you understand WHY it's happening.

---

## Phase 2: Pattern Analysis

**Find the pattern before fixing:**

### 1. Find Working Examples

- Locate similar working code in the same codebase
- What works that's similar to what's broken?

**Action:** Use `search_files` to find comparable patterns:

```python
search_files("similar_pattern", path="src/", file_glob="*.py")
```

### 2. Compare Against References

- If implementing a pattern, read the reference implementation COMPLETELY
- Don't skim — read every line
- Understand the pattern fully before applying

### 3. Identify Differences

- What's different between working and broken?
- List every difference, however small
- Don't assume "that can't matter"

### 4. Understand Dependencies

- What other components does this need?
- What settings, config, environment?
- What assumptions does it make?

---

## Phase 3: Hypothesis and Testing

**Scientific method:**

### 1. Form a Single Hypothesis

- State clearly: "I think X is the root cause because Y"
- Write it down
- Be specific, not vague

### 2. Test Minimally

- Make the SMALLEST possible change to test the hypothesis
- One variable at a time
- Don't fix multiple things at once

### 3. Verify Before Continuing

- Did it work? → Phase 4
- Didn't work? → Form NEW hypothesis
- DON'T add more fixes on top

### 4. When You Don't Know

- Say "I don't understand X"
- Don't pretend to know
- Ask the user for help
- Research more

---

## Phase 4: Implementation

**Fix the root cause, not the symptom:**

### 1. Create Failing Test Case

- Simplest possible reproduction
- Automated test if possible
- MUST have before fixing
- Use the `test-driven-development` skill

### 2. Implement Single Fix

- Address the root cause identified
- ONE change at a time
- No "while I'm here" improvements
- No bundled refactoring

### 3. Verify Fix

```bash
# Run the specific regression test
pytest tests/test_module.py::test_regression -v

# Run full suite — no regressions
pytest tests/ -q
```

### 4. If Fix Doesn't Work — The Rule of Three

- **STOP.**
- Count: How many fixes have you tried?
- If < 3: Return to Phase 1, re-analyze with new information
- **If ≥ 3: STOP and question the architecture (step 5 below)**
- DON'T attempt Fix #4 without architectural discussion

### 5. If 3+ Fixes Failed: Question Architecture

**Pattern indicating an architectural problem:**
- Each fix reveals new shared state/coupling in a different place
- Fixes require "massive refactoring" to implement
- Each fix creates new symptoms elsewhere

**STOP and question fundamentals:**
- Is this pattern fundamentally sound?
- Are we "sticking with it through sheer inertia"?
- Should we refactor the architecture vs. continue fixing symptoms?

**Discuss with the user before attempting more fixes.**

This is NOT a failed hypothesis — this is a wrong architecture.

---

## Phase 5: Numerical Verification (Signal Processing / FFT / Data Analysis)

**CRITICAL PITFALL: NEVER report numerical analysis results without actually computing them.**

Both AI agents and humans are prone to fabricating plausible-sounding numbers for spectral analysis, filter performance, and statistical metrics. This is not a minor issue — it destroys credibility and misleads engineering decisions.

### The Fabrication Pattern

When analyzing signal processing results (FFT, filters, noise analysis), the temptation is to:
- Estimate percentages from visual inspection of plots
- Cite "typical" values from memory rather than computing actual values
- Report numbers that sound reasonable without verification
- Copy numbers from one context and apply to another

**ALL of these are fabrication. The only valid number is one computed from the actual data.**

### Mandatory Verification Steps

For ANY spectral/numerical analysis:

1. **Load actual data** — not from memory, not estimated from plots
2. **Run actual computation** — numpy/scipy, not mental math
3. **Report only computed values** — with exact code that produced them
4. **Cross-verify with pure signal simulation** — generate a known signal and verify your analysis pipeline recovers the expected result
5. **State uncertainty** — if the analysis has assumptions, state them

### Specific Pitfalls Caught in Production

| Claim | Actual | Error |
|-------|--------|-------|
| "Sidelobe ratio 42.8%" | 61.3% | Underestimated by 43% |
| "Pure 7Hz aligned sidelobe 18.1%" | 0.00% | Completely fabricated — aligned signals have ZERO leakage |
| "Energy asymmetry 2.09:1 is fabricated" | 2.09:1 IS real at ±1.5Hz, 1.00:1 at ±3.0Hz | Wrong debunk — both numbers are real, just different observation windows |
| "Hanning window improves sidelobe" | Worsens (61%→76%) | Wrong direction — window actually made it worse |

### Verification Script Template

```python
import numpy as np

# ALWAYS verify with pure signal first
t = np.arange(N) / fs
pure_signal = np.sin(2 * np.pi * target_freq * t)
fft_pure = np.fft.rfft(pure_signal)
psd_pure = np.abs(fft_pure)**2
# Verify: aligned signal should have ~0 sidelobe leakage
sidelobe_pct = (psd_pure.sum() - psd_pure[main_bin]) / psd_pure.sum() * 100
assert sidelobe_pct < 1.0, f"Pure aligned signal sidelobe {sidelobe_pct:.1f}% — check FFT setup"
```

### Cross-Parameter Verification Pitfall

**CRITICAL LESSON**: When comparing numerical results from another analysis, you MUST use identical parameters before claiming a number is "fabricated."

Real example of failure:
- Another analysis reported "energy asymmetry 2.09:1" using ±1.5Hz window
- My verification used ±3.0Hz window and got "1.01:1"
- I concluded the 2.09:1 was "fabricated" — **WRONG**
- Both numbers were correct; the difference was the observation window

**The rule**: When you get a different number, your FIRST question must be "am I using the same parameters?" not "is the other number fake?"

Verification checklist before disputing a numerical claim:
1. Same observation window / frequency range?
2. Same data source and preprocessing (DC removal, normalization)?
3. Same FFT parameters (N, fs, window function)?
4. Same metric definition (amplitude vs power, peak vs RMS)?
5. Same bin inclusion criteria (>5% threshold, >1% threshold)?

If ANY parameter differs, you are comparing different measurements, not catching a fabrication.

### Rule

**If you cannot show the code that produced a number, do not report the number.**
**If you use different parameters than the claim you're disputing, you are wrong — not them.**

---

## Red Flags — STOP and Follow Process

If you catch yourself thinking:
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "Skip the test, I'll manually verify"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- "Pattern says X but I'll adapt it differently"
- "Here are the main problems: [lists fixes without investigation]"
- Proposing solutions before tracing data flow
- **"One more fix attempt" (when already tried 2+)**
- **Each fix reveals a new problem in a different place**

**ALL of these mean: STOP. Return to Phase 1.**

**If 3+ fixes failed:** Question the architecture (Phase 4 step 5).

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Issue is simple, don't need process" | Simple issues have root causes too. Process is fast for simple bugs. |
| "Emergency, no time for process" | Systematic debugging is FASTER than guess-and-check thrashing. |
| "Just try this first, then investigate" | First fix sets the pattern. Do it right from the start. |
| "I'll write test after confirming fix works" | Untested fixes don't stick. Test first proves it. |
| "Multiple fixes at once saves time" | Can't isolate what worked. Causes new bugs. |
| "Reference too long, I'll adapt the pattern" | Partial understanding guarantees bugs. Read it completely. |
| "I see the problem, let me fix it" | Seeing symptoms ≠ understanding root cause. |
| "One more fix attempt" (after 2+ failures) | 3+ failures = architectural problem. Question the pattern, don't fix again. |

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| **1. Root Cause** | Read errors, reproduce, check changes, **verify pre-existing vs introduced**, gather evidence, trace data flow | Understand WHAT and WHY |
| **2. Pattern** | Find working examples, compare, identify differences | Know what's different |
| **3. Hypothesis** | Form theory, test minimally, one variable at a time | Confirmed or new hypothesis |
| **4. Implementation** | Create regression test, fix root cause, verify | Bug resolved, all tests pass |

## Domain-Specific References

- **[LVGL Debugging](references/lvgl-debugging.md)** — Recurring bug patterns in LVGL C projects: `lv_event_get_target` trap, reentrancy deadlocks, memory allocation failures, macro shadowing, layout overflow from SCREEN vs CONTENT dimensions.

## Hermes Agent Integration

### Investigation Tools

Use these Hermes tools during Phase 1:

- **`search_files`** — Find error strings, trace function calls, locate patterns
- **`read_file`** — Read source code with line numbers for precise analysis
- **`terminal`** — Run tests, check git history, reproduce bugs
- **`web_search`/`web_extract`** — Research error messages, library docs

### With delegate_task

For complex multi-component debugging, dispatch investigation subagents:

```python
delegate_task(
    goal="Investigate why [specific test/behavior] fails",
    context="""
    Follow systematic-debugging skill:
    1. Read the error message carefully
    2. Reproduce the issue
    3. Trace the data flow to find root cause
    4. Report findings — do NOT fix yet

    Error: [paste full error]
    File: [path to failing code]
    Test command: [exact command]
    """,
    toolsets=['terminal', 'file']
)
```

### With test-driven-development

When fixing bugs:
1. Write a test that reproduces the bug (RED)
2. Debug systematically to find root cause
3. Fix the root cause (GREEN)
4. The test proves the fix and prevents regression

## Real-World Impact

From debugging sessions:
- Systematic approach: 15-30 minutes to fix
- Random fixes approach: 2-3 hours of thrashing
- First-time fix rate: 95% vs 40%
- New bugs introduced: Near zero vs common

**No shortcuts. No guessing. Systematic always wins.**
