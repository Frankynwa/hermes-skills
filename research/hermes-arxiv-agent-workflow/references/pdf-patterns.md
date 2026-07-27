# PDF Affiliation Extraction - Example Patterns

This document contains real examples of how affiliations appear in academic PDFs, based on papers processed by hermes-arxiv-agent.

## Example 1: Structured with Emails (2607.20981)

```
Jay Gor
23bce113@nirmauni.ac.in
Nirma University
Karm Dave
23bce137@nirmauni.ac.in
Nirma University
Akshita Abrol
akshita.abrol@singaporetech.edu.sg
Singapore Institute of Technology, Singapore
Rajesh Gupta
rajesh.gupta@marwadieducation.edu.in
Department of CE-AI and Big Data, Marwadi University
```

**Pattern**: Author → Email → Institution (one per line)

**Extracted**: `Nirma University; Singapore Institute of Technology, Singapore; Marwadi University`

## Example 2: Department + University (2607.21063)

```
Emilio Ferrara
Thomas Lord Department of Computer Science
University of Southern California
emiliofe@usc.edu
```

**Pattern**: Author → Department → University → Email

**Extracted**: `University of Southern California`

**Note**: The department name ("Thomas Lord Department of Computer Science") is part of the university affiliation. We extract the main institution name.

## Example 3: Superscript Numbers (2607.21076)

```
Jiameng Li∗1, Han Zhou2, Matthew B. Blaschko1
1KU Leuven, 2Tiangong University
```

**Pattern**: Author names with superscript numbers → Number-institution mapping

**Extracted**: `KU Leuven; Tiangong University`

**Note**: The `∗` is a footnote marker (often for corresponding author). Numbers `1`, `2` map to institutions.

## Common Pitfalls

1. **Abstract text contamination**: If extraction returns words like "memory", "computational", "quantization", "method", "performance" → it's reading abstract text, not affiliations.

2. **CamelCase merging**: PDFs often render "Department of ComputerScience" as "DepartmentofComputerScience". Apply CamelCase splitting.

3. **Line break issues**: "Republic of" on one line, "Korea" on next line. Handle with context-aware joining.

4. **Multiple institutions per author**: Some authors have joint affiliations. Join with semicolon.

5. **Corresponding author markers**: `*`, `†`, `‡`, `§`, `¶` are footnote markers, not part of institution names. Remove them.

## Institution Keywords

Use these to identify institution lines:

- University, Institute, College, School, Department, Laboratory, Center, Centre
- Company names: Google, Microsoft, Meta, Amazon, NVIDIA, Apple, OpenAI, DeepMind, Alibaba, Tencent, Baidu, ByteDance, Huawei, Samsung
- Top universities: MIT, Stanford, Harvard, Princeton, Berkeley, Yale, Columbia, Cornell, UCLA, KAIST, NUS, NTU, ETH, CMU, KU Leuven, Tsinghua, Peking, Zhejiang, Fudan, SJTU
