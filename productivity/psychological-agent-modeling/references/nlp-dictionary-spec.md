# Chinese Psychological Dictionary Specification

## Implementation: `~/projects/psych-nlp/src/psych_nlp/dictionaries/__init__.py`

## Category Design & Rationale

### 1. Positive Emotion (~80 words)
Source: LIWC-CN + HowNet + Chinese emotion research
Subcategories: basic positive (开心/快乐), deep positive (意义/成就/领悟), relational (感恩/连接)
Used for: emotion_valence calculation, attachment scoring

### 2. Negative Emotion (~100 words)
Subcategories: basic negative (难过/痛苦), deep negative (空心/虚无/异化), somatic-mapped (心痛/窒息)
Used for: anxiety scoring, schema activation detection

### 3. Cognitive Processing Words (~50 words)
Source: LIWC Cognitive Processes CN
Includes: causal (因为/所以), insight (意识到/明白), conditional (如果/假如), obligation (应该/必须)
Used for: avoidance scoring (high cognitive = avoidance marker), harsh standards detection

### 4. Absolutist Words (~30 words)
Source: Al-Mosaiwi (2018) — anxiety/depression specificity marker
Includes: always/never words (总是/从不/永远), extreme quantifiers (完全/绝对/百分之百)
Used for: anxiety scoring, harsh standards detection

### 5-6. Pronouns (4 categories)
1sg "我" → anxiety marker (Slatcher: r=0.31)
1pl "我们/咱们" → security marker (Slatcher: associated with secure attachment)
2nd "你/您" → relationship engagement
3rd "他/她/别人" → distancing (Brockmeyer: emotional deprivation)

### 7. Somatic Expressions (~40 entries)
**Chinese-specific.** Source: Qiu (2019), clinical observation
Subcategories: cardiac (心堵/胸闷/心慌), head (头疼/脑子乱), gastric (没胃口/恶心), general (浑身无力/失眠)
Used for: anxiety scoring (Chinese users express psychological distress as physical symptoms)

### 8. Internet Slang Emotion (~30 entries)
**Age-specific.** Source: Chinese social media observation
Negative: emo了/破防/裂开/绷不住了/心态崩了/人麻了/摆烂/躺平
Positive: yyds/起飞/上头
Used for: firefighter detection (slang = emotional eruption), general emotion scoring

### 9. Emotional Inhibition Markers (~30 entries)
Source: Brockmeyer (2015), Newell (2021), clinical observation
Subcategories: emotion denial (还好/没什么/没事), abstraction (怎么说呢/说不清楚), passivity (没办法/只能/算了), rationalization (客观来说/理性地看)
Used for: emotional inhibition schema scoring (primary indicator)

### 10. Harsh Standards Markers (~25 entries)
Source: Brockmeyer (2015)
Subcategories: self-demand (应该/必须/完美/不够好), self-criticism (太差了/废物/浪费), other-expectations (不应该/太低了)
Used for: harsh standards schema scoring

### 11. Emotional Deprivation Markers (~25 entries)
Source: Brockmeyer (2015)
Subcategories: not-understood (没人理解/没人懂), unmet-needs (渴望/得不到/没有回应), relational-disappointment (心寒/不指望)
Used for: emotional deprivation schema scoring

### 12. Topic Shift Markers (~25 entries)
**IFS-specific.** Source: IFS clinical patterns
Protector shifts: (换个角度/冷静想想/先不要想)
Firefighter shifts: (不想了/算了/先做别的/打游戏)
Used for: IFS part activation detection

### 13. Time Markers (~40 entries, 3 categories)
Past (曾经/那时候/小时候) → exile marker (exile carries childhood memories)
Present (现在/目前/最近) → grounding
Future (以后/将来/等我) → firefighter marker (future = avoidance of present)

### 14. Hedging Words (~20 entries)
Source: LIWC tentative category CN
Includes: (可能/也许/好像/某种程度/怎么说)
Used for: emotional inhibition marker (hedging = distancing from feelings), avoidance scoring

## Dictionary Maintenance

- Add new internet slang quarterly (language evolves fast)
- Cross-validate with LIWC-CN when available
- Log unknown words during analysis for dictionary expansion
- Weight adjustments based on correlation with questionnaire baselines
