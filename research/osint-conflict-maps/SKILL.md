---
name: osint-conflict-maps
description: >
  Find and evaluate real-time conflict/war tracking maps (OSINT). Covers major
  Russia-Ukraine front-line maps, their bias/accuracy, update frequency, and
  how to cross-reference for neutrality. Also applies to other conflicts.
triggers:
  - "war map"
  - "frontline map"
  - "conflict tracking"
  - "OSINT map"
  - "battle map"
  - "俄乌地图"
  - "战线地图"
  - "战况地图"
---

# OSINT Conflict Maps

## Major Russia-Ukraine Front-Line Maps

| Map | URL | Bias | Update Speed | Strengths |
|-----|-----|------|--------------|-----------|
| DeepState Map | deepstatemap.live | Pro-Ukraine | Daily (fastest) | Time slider for historical playback, rich detail |
| Suriyak Maps | suriyakmaps.com | Most neutral | Daily (one-person op, occasional delays) | Covers both sides' advances honestly |
| ISW Map Room | understandingwar.org | Pro-West/Ukraine | Daily with analysis | Rigorous methodology, transparent sources |
| Liveuamap | liveuamap.com | Moderate | Continuous event stream | Global coverage, event-level granularity (shelling, strikes, advances) |

## Neutrality Assessment

- **Best neutrality**: Suriyak Maps — community consensus is this is the most balanced; marks both Russian and Ukrainian advances without selective omission.
- **Fastest updates**: DeepState Map — but will delay marking Russian territorial gains.
- **Best analysis overlay**: ISW — daily reports with maps, strong analytical framework, openly pro-Ukraine but doesn't fabricate.
- **Cross-referencing strategy**: Compare Suriyak vs DeepState. Where one shows an advance the other doesn't, that gap reveals bias on that specific event.

## Stopped/Inactive Sources (DO NOT recommend)

- Andrew Perpetua — stopped updating as of ~2025. Do not recommend.
- Rybar — Russian MoD affiliated, unreliable.

## OSINT Community Figures (verify activity before recommending)

Always check if an OSINT mapper is still active before recommending. This space has high turnover — mappers burn out, get drafted, or shift focus. The map platforms above are more stable than individual analysts.

## How to Find Latest Sources

When user asks for up-to-date conflict maps:
1. Recommend the table above as starting point
2. Note that individual OSINT mappers on X/Twitter frequently start and stop — verify recency
3. For the Russia-Ukraine war specifically: @Deepstate_UA, @suriyakmaps, @War_Mapper on X are primary aggregators

## Limitations of Terminal-Based News Fetching

Most conflict tracking sites (ISW, BBC, Liveuamap, etc.) are JavaScript-rendered SPAs. `curl` will return empty or useless HTML. Do NOT attempt curl-based scraping of these sites — go directly to the map URLs in a browser or recommend the user visit them.
