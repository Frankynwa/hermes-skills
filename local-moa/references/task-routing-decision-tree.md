# Task Routing Decision Tree

When faced with a complex task, choose the right approach:

```
Can the task be decomposed into clear subtasks with boundaries?
├── NO → Use MoA Committee (local-moa)
│        Single question, multi-model cross-validation.
│        Examples: debugging runtime bugs, strategy logic debates,
│        paper methodology critique.
│
└── YES → Do subtasks have strong dependencies on each other?
    ├── NO → Use 20min Mode (autonomous-task-paradigms)
    │        Parallel dispatch, parent agent merges results.
    │        Examples: search 3 papers, lint code, run benchmarks.
    │
    └── YES → Does the merge phase involve heavy patching?
        ├── NO → Use 20min Mode (parent agent merges is enough)
        │        Light dependency, subagent outputs are compatible.
        │
        └── YES → Use Multi Agents (CrewAI/AutoGen pipeline)
                 Agents directly communicate and fix each other's output.
                 Examples: API doc → code → review → fix → re-review.
```

## Key Insight

20min Mode covers 80% of decomposable tasks. Multi Agents only worth it when
the merge/patch phase consistently wastes time fixing incompatible outputs.

MoA is a different category entirely — it's for tasks you CAN'T decompose.
Don't confuse "multiple models" (MoA) with "multiple agents" (Multi Agents).

- MoA: Same question, different models, cross-validate.
- Multi Agents: Different subtasks, different agents, pipeline.
- 20min Mode: Independent subtasks, parallel dispatch, parent merges.
