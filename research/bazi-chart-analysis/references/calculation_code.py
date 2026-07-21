"""
BaZi (八字) Calculation Reference Code
Use this as a starting template for chart calculation.
Includes: pillars, ten gods, changsheng (十二长生), nayin (纳音).
"""

from datetime import date

# Constants
TIANGAN = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
DIZHI = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
TG_WUXING = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土","己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}
DZ_WUXING = {"子":"水","丑":"土","寅":"木","卯":"木","辰":"土","巳":"火","午":"火","未":"土","申":"金","酉":"金","戌":"土","亥":"水"}
DZ_CANGGAN = {
    "子":["癸"],"丑":["己","癸","辛"],"寅":["甲","丙","戊"],"卯":["乙"],
    "辰":["戊","乙","癸"],"巳":["丙","庚","戊"],"午":["丁","己"],"未":["己","丁","乙"],
    "申":["庚","壬","戊"],"酉":["辛"],"戌":["戊","辛","丁"],"亥":["壬","甲"]
}

BASE_DATE = date(2000, 1, 7)  # 甲子日 (verified: 2000-01-01 = 戊午日, index 54)

# ==================== Pillar Calculation ====================

def get_day_pillar(birth_date: date) -> str:
    """Calculate day pillar from Gregorian date."""
    diff = (birth_date - BASE_DATE).days
    idx = diff % 60
    if idx < 0: idx += 60
    return TIANGAN[idx % 10] + DIZHI[idx % 12]

def get_day_pillar_index(birth_date: date) -> int:
    """Get sexagenary index (0-59) of day pillar."""
    diff = (birth_date - BASE_DATE).days
    idx = diff % 60
    if idx < 0: idx += 60
    return idx

def get_year_pillar(year: int) -> str:
    """Calculate year pillar. 1984 = 甲子年."""
    offset = (year - 1984) % 60
    return TIANGAN[offset % 10] + DIZHI[offset % 12]

def get_month_pillar(year_tg: str, solar_month: int, solar_day: int) -> str:
    """Calculate month pillar from year stem and solar date.
    Uses 节气 boundaries for accurate month assignment."""
    # 节气 approximate boundaries (solar month, day)
    jieqi = [
        (2, 4),   # 立春 → 寅月
        (3, 6),   # 惊蛰 → 卯月
        (4, 5),   # 清明 → 辰月
        (5, 6),   # 立夏 → 巳月
        (6, 6),   # 芒种 → 午月
        (7, 7),   # 小暑 → 未月
        (8, 7),   # 立秋 → 申月
        (9, 8),   # 白露 → 酉月
        (10, 8),  # 寒露 → 戌月
        (11, 7),  # 立冬 → 亥月
        (12, 7),  # 大雪 → 子月
        (1, 6),   # 小寒 → 丑月 (next year)
    ]
    # Determine month branch index (寅=2, 卯=3, ..., 丑=1)
    month_branch_idx = 1  # default 丑月
    for i, (m, d) in enumerate(jieqi):
        if (solar_month, solar_day) < (m, d):
            month_branch_idx = (i + 1) % 12  # 寅=2 is month 1
            break
    else:
        month_branch_idx = 1  # 丑月 (小寒后)

    # 五虎遁: year stem determines month stem start
    starts = {"甲":2, "己":2, "乙":4, "庚":4, "丙":6, "辛":6, "丁":8, "壬":8, "戊":0, "癸":0}
    start = starts[year_tg]
    # Count from 寅(2) to target branch
    offset = (month_branch_idx - 2) % 12
    tg_idx = (start + offset) % 10
    return TIANGAN[tg_idx] + DIZHI[month_branch_idx]

def get_hour_pillar(day_tg: str, hour_24: int) -> str:
    """Calculate hour pillar from day stem and 24h hour.
    hour_24: 23-1=子, 1-3=丑, 3-5=寅, 5-7=卯, 7-9=辰, 9-11=巳,
             11-13=午, 13-15=未, 15-17=申, 17-19=酉, 19-21=戌, 21-23=亥"""
    # Map 24h to branch index
    if hour_24 == 23 or hour_24 == 0:
        branch_idx = 0  # 子
    else:
        branch_idx = (hour_24 + 1) // 2  # 1-2→1(丑), 3-4→2(寅), etc.
    
    starts = {"甲":0, "己":0, "乙":2, "庚":2, "丙":4, "辛":4, "丁":6, "壬":6, "戊":8, "癸":8}
    start = starts[day_tg]
    tg_idx = (start + branch_idx) % 10
    return TIANGAN[tg_idx] + DIZHI[branch_idx]

# ==================== Ten Gods ====================

def get_shishen(day_tg: str, other_tg: str) -> str:
    """Determine ten god relationship. Returns full name (e.g. 正财, 七杀)."""
    dm_wx = TG_WUXING[day_tg]
    other_wx = TG_WUXING[other_tg]
    same_yinyang = (TIANGAN.index(day_tg) % 2) == (TIANGAN.index(other_tg) % 2)
    
    rel = {
        ("水","金"):"印", ("水","木"):"食伤", ("水","土"):"官杀", ("水","火"):"财", ("水","水"):"比劫",
        ("木","水"):"印", ("木","火"):"食伤", ("木","金"):"官杀", ("木","土"):"财", ("木","木"):"比劫",
        ("火","木"):"印", ("火","土"):"食伤", ("火","水"):"官杀", ("火","金"):"财", ("火","火"):"比劫",
        ("土","火"):"印", ("土","金"):"食伤", ("土","木"):"官杀", ("土","水"):"财", ("土","土"):"比劫",
        ("金","土"):"印", ("金","水"):"食伤", ("金","火"):"官杀", ("金","木"):"财", ("金","金"):"比劫",
    }
    
    base = rel.get((dm_wx, other_wx), "?")
    prefix = {"印":"正印" if same_yinyang else "偏印", "食伤":"食神" if same_yinyang else "伤官",
              "官杀":"正官" if same_yinyang else "七杀", "财":"正财" if same_yinyang else "偏财",
              "比劫":"比肩" if same_yinyang else "劫财"}
    return prefix.get(base, base)

# ==================== 十二长生 (Twelve Growth Stages) ====================

# Lookup table: day_master → branch → stage
# 长生=100, 沐浴=80, 冠带=70, 临官=90, 帝旺=95, 衰=60, 病=40, 死=20, 墓=30, 绝=10, 胎=50, 养=60
CHANGSHENG_TABLE = {
    #        子    丑    寅    卯    辰    巳    午    未    申    酉    戌    亥
    "甲": ["沐浴","冠带","临官","帝旺","衰","病","死","墓","绝","胎","养","长生"],
    "乙": ["病","衰","帝旺","临官","冠带","沐浴","长生","养","胎","绝","墓","死"],
    "丙": ["胎","养","长生","沐浴","冠带","临官","帝旺","衰","病","死","墓","绝"],
    "丁": ["绝","墓","死","病","衰","帝旺","临官","冠带","沐浴","长生","养","胎"],
    "戊": ["胎","养","长生","沐浴","冠带","临官","帝旺","衰","病","死","墓","绝"],
    "己": ["绝","墓","死","病","衰","帝旺","临官","冠带","沐浴","长生","养","胎"],
    "庚": ["死","墓","绝","胎","养","长生","沐浴","冠带","临官","帝旺","衰","病"],
    "辛": ["长生","养","胎","绝","墓","死","病","衰","帝旺","临官","冠带","沐浴"],
    "壬": ["帝旺","衰","病","死","墓","绝","胎","养","长生","沐浴","冠带","临官"],
    "癸": ["临官","冠带","沐浴","长生","养","胎","绝","墓","死","病","衰","帝旺"],
}

CHANGSHENG_SCORE = {
    "长生":70, "沐浴":55, "冠带":65, "临官":85, "帝旺":95,
    "衰":50, "病":30, "死":15, "墓":25, "绝":10, "胎":45, "养":55
}

def get_changsheng(day_master: str, branch: str) -> tuple:
    """Returns (stage_name, strength_score) for day master in given branch."""
    stage = CHANGSHENG_TABLE[day_master][DIZHI.index(branch)]
    score = CHANGSHENG_SCORE[stage]
    return stage, score

# ==================== 纳音 (Nayin) ====================

NAYIN_TABLE = [
    "海中金","海中金","炉中火","炉中火","大林木","大林木","路旁土","路旁土",
    "剑锋金","剑锋金","山头火","山头火","涧下水","涧下水","城头土","城头土",
    "白蜡金","白蜡金","杨柳木","杨柳木","泉中水","泉中水","屋上土","屋上土",
    "霹雳火","霹雳火","松柏木","松柏木","长流水","长流水","砂石金","砂石金",
    "山下火","山下火","平地木","平地木","壁上土","壁上土","金箔金","金箔金",
    "覆灯火","覆灯火","天河水","天河水","大驿土","大驿土","钗环金","钗环金",
    "桑拓木","桑拓木","大溪水","大溪水","沙中土","沙中土","天上火","天上火",
    "石榴木","石榴木","大海水","大海水"
]

def get_nayin(pillar: str) -> str:
    """Get 纳音 for a pillar (e.g. '甲子')."""
    tg_idx = TIANGAN.index(pillar[0])
    dz_idx = DIZHI.index(pillar[1])
    # Find sexagenary index
    sex_idx = None
    for i in range(60):
        if i % 10 == tg_idx and i % 12 == dz_idx:
            sex_idx = i
            break
    if sex_idx is None:
        return "未知"
    return NAYIN_TABLE[sex_idx]

# ==================== 大运 (Major Luck Periods) ====================

def get_dayun_direction(year_tg: str, gender: str) -> str:
    """Determine 大运 direction. Returns 'forward' or 'backward'."""
    is_yang_year = TIANGAN.index(year_tg) % 2 == 0  # 甲丙戊庚壬 = yang
    if (is_yang_year and gender == "男") or (not is_yang_year and gender == "女"):
        return "forward"
    return "backward"

def get_dayun_list(month_pillar: str, direction: str, count: int = 8) -> list:
    """Generate 大运 list from month pillar."""
    tg_idx = TIANGAN.index(month_pillar[0])
    dz_idx = DIZHI.index(month_pillar[1])
    result = []
    for i in range(1, count + 1):
        if direction == "forward":
            t = (tg_idx + i) % 10
            d = (dz_idx + i) % 12
        else:
            t = (tg_idx - i) % 10
            d = (dz_idx - i) % 12
        result.append(TIANGAN[t] + DIZHI[d])
    return result

# ==================== Full Calculation ====================

def calculate_bazi(year, month, day, hour_24, gender="男"):
    """Full BaZi calculation.
    year, month, day: Gregorian calendar
    hour_24: 0-23 (24h format)
    gender: "男" or "女"
    """
    birth_date = date(year, month, day)
    year_p = get_year_pillar(year)
    month_p = get_month_pillar(year_p[0], month, day)
    day_p = get_day_pillar(birth_date)
    hour_p = get_hour_pillar(day_p[0], hour_24)
    day_master = day_p[0]
    
    # Ten gods for heavenly stems
    ten_gods = {
        "年干": get_shishen(day_master, year_p[0]),
        "月干": get_shishen(day_master, month_p[0]),
        "时干": get_shishen(day_master, hour_p[0]),
    }
    
    # 地支藏干 ten gods
    canggan_gods = {}
    for label, branch in [("年支", year_p[1]), ("月支", month_p[1]), ("日支", day_p[1]), ("时支", hour_p[1])]:
        cg = DZ_CANGGAN[branch]
        canggan_gods[label] = [(g, get_shishen(day_master, g)) for g in cg]
    
    # 十二长生
    changsheng = {}
    for label, branch in [("年支", year_p[1]), ("月支", month_p[1]), ("日支", day_p[1]), ("时支", hour_p[1])]:
        stage, score = get_changsheng(day_master, branch)
        changsheng[label] = {"branch": branch, "stage": stage, "score": score}
    
    # 纳音
    nayin = {
        "年柱": get_nayin(year_p),
        "月柱": get_nayin(month_p),
        "日柱": get_nayin(day_p),
        "时柱": get_nayin(hour_p),
    }
    
    # 大运
    direction = get_dayun_direction(year_p[0], gender)
    dayun = get_dayun_list(month_p, direction)
    
    # 五行统计 (weighted)
    wuxing = {"金":0, "木":0, "水":0, "火":0, "土":0}
    # Heavenly stems: 1.0 each
    for tg in [year_p[0], month_p[0], day_p[0], hour_p[0]]:
        wuxing[TG_WUXING[tg]] += 1.0
    # Earth branches: 本气1.0, 中气0.3, 余气0.1
    branch_weights = {
        "子":[("癸",1.0)], "丑":[("己",1.0),("癸",0.3),("辛",0.1)],
        "寅":[("甲",1.0),("丙",0.3),("戊",0.1)], "卯":[("乙",1.0)],
        "辰":[("戊",1.0),("乙",0.3),("癸",0.1)], "巳":[("丙",1.0),("庚",0.3),("戊",0.1)],
        "午":[("丁",1.0),("己",0.3)], "未":[("己",1.0),("丁",0.3),("乙",0.1)],
        "申":[("庚",1.0),("壬",0.3),("戊",0.1)], "酉":[("辛",1.0)],
        "戌":[("戊",1.0),("辛",0.3),("丁",0.1)], "亥":[("壬",1.0),("甲",0.3)]
    }
    for branch in [year_p[1], month_p[1], day_p[1], hour_p[1]]:
        for element_stem, weight in branch_weights[branch]:
            wuxing[TG_WUXING[element_stem]] += weight
    
    total = sum(wuxing.values())
    wuxing_pct = {k: round(v/total*100, 1) for k, v in wuxing.items()}
    
    return {
        "year": year_p, "month": month_p, "day": day_p, "hour": hour_p,
        "day_master": day_master,
        "day_master_wx": TG_WUXING[day_master],
        "ten_gods": ten_gods,
        "canggan_gods": canggan_gods,
        "changsheng": changsheng,
        "nayin": nayin,
        "dayun": dayun,
        "dayun_direction": direction,
        "wuxing": wuxing,
        "wuxing_pct": wuxing_pct,
        "gender": gender,
    }

# Example usage:
# result = calculate_bazi(2005, 11, 15, 5, "女")
# print(f"{result['year']} · {result['month']} · {result['day']} · {result['hour']}")
# print(f"日主: {result['day_master']}({result['day_master_wx']})")
# print(f"五行: {result['wuxing_pct']}")
# print(f"纳音: {result['nayin']}")
# print(f"大运: {result['dayun']}")
# for label, info in result['changsheng'].items():
#     print(f"  {label} {info['branch']}: {info['stage']}({info['score']})")
