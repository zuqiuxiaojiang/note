import frontmatter
import glob
import os
from collections import defaultdict

# 扫描所有笔记
pages = []
for path in glob.glob("生产数据/**/*.md", recursive=True):
    post = frontmatter.load(path)
    data = post.metadata
    if data.get("班组"):
        pages.append(data)

# 安全读取数字：None、空字符串、不存在的键，都返回 0
def safe_num(p, key):
    v = p.get(key)
    if v is None or v == "":
        return 0
    try:
        return float(v)
    except (ValueError, TypeError):
        return 0

# 判断是否为正常班（有有效数字）
def has_valid_data(p):
    v = p.get("蒸汽消耗")
    return isinstance(v, (int, float)) and v is not None

# 按班组分组
teams = ["甲班", "乙班", "丙班", "丁班"]
team_stats = {}

for team in teams:
    rows = [p for p in pages if p.get("班组") == team]
    rows.sort(key=lambda x: str(x.get("日期", "")))
    
    蒸汽合计 = 糖浆合计 = 水合计 = 电合计 = 0
    正常班数 = 0
    水分扣分 = 0
    明细 = []
    
    for p in rows:
        has_data = has_valid_data(p)
        
        if has_data:
            蒸汽合计 += safe_num(p, "蒸汽消耗")
            糖浆合计 += safe_num(p, "糖浆加量")
            水合计   += safe_num(p, "水消耗")
            电合计   += safe_num(p, "电消耗")
            正常班数 += 1
        
        m = p.get("水分")
        if isinstance(m, (int, float)):
            if m < 2:  水分扣分 -= 5
            if m > 2:  水分扣分 -= 10
            if m < 10.5: 水分扣分 -= 5
            if m > 11.5: 水分扣分 -= 10
        
        明细.append({
            "日期": p.get("日期", "-"),
            "类型": p.get("类型", "正常"),
            "蒸汽": p.get("蒸汽消耗") if has_data else "-",
            "糖浆": p.get("糖浆加量") if has_data else "-",
            "水": p.get("水消耗") if has_data else "-",
            "电": p.get("电消耗") if has_data else "-",
            "水分": p.get("水分", "-")
        })
    
    蒸汽糖浆比 = round(蒸汽合计 / 糖浆合计, 4) if 糖浆合计 else "-"
    水平均 = round(水合计 / 正常班数, 2) if 正常班数 else "-"
    电平均 = round(电合计 / 正常班数, 1) if 正常班数 else "-"
    
    team_stats[team] = {
        "蒸汽": 蒸汽合计, "糖浆": 糖浆合计, "水": round(水合计, 1), "电": 电合计,
        "扣分": 水分扣分, "班数": 正常班数, "比": 蒸汽糖浆比, "水均": 水平均, "电均": 电平均,
        "明细": 明细
    }

# 排名
stats_list = [(t, team_stats[t]) for t in teams if t in team_stats]

def rank(arr, key, asc=True):
    s = sorted(arr, key=lambda x: x[1][key] if isinstance(x[1][key], (int, float)) else float('inf'))
    if not asc: s.reverse()
    vals = [x[1][key] for x in s if isinstance(x[1][key], (int, float))]
    unique = sorted(set(vals), reverse=not asc)
    return {v: i+1 for i, v in enumerate(unique)}

r_ratio = rank(stats_list, "比", True)
r_water = rank(stats_list, "水均", True)
r_elec  = rank(stats_list, "电均", True)

for t, s in stats_list:
    s["排名比"] = r_ratio.get(s["比"], "-")
    s["排名水"] = r_water.get(s["水均"], "-")
    s["排名电"] = r_elec.get(s["电均"], "-")
    s["积分"] = (s["排名比"] if isinstance(s["排名比"], int) else 0) + \
                (s["排名水"] if isinstance(s["排名水"], int) else 0) + \
                (s["排名电"] if isinstance(s["排名电"], int) else 0)

r_score = rank([(t, s) for t, s in stats_list], "积分", True)
for t, s in stats_list:
    s["总排名"] = r_score.get(s["积分"], "-")

# 生成 README.md
md = ["# 生产数据报表\n\n", "## 📊 消耗统计汇总\n\n"]
md.append("| 班组 | 蒸汽用量 | 糖浆加量 | 水量 | 电量 | 水分扣分 |\n")
md.append("|:---:|:---:|:---:|:---:|:---:|:---:|\n")
for t in teams:
    if t not in team_stats: continue
    s = team_stats[t]
    md.append(f"| {t} | {s['蒸汽']} | {s['糖浆']} | {s['水']} | {s['电']} | {s['扣分']} |\n")

md.append("\n## 📈 平均分\n\n")
md.append("| 班组 | 蒸汽÷糖浆 | 水量÷正常班 | 电量÷正常班 | 工艺分 |\n")
md.append("|:---:|:---:|:---:|:---:|:---:|\n")
for t in teams:
    if t not in team_stats: continue
    s = team_stats[t]
    md.append(f"| {t} | {s['比']} | {s['水均']} | {s['电均']} | 40 |\n")

md.append("\n## 🏆 积分排名\n\n")
md.append("| 班组 | 蒸汽÷糖浆排名 | 水消耗排名 | 电消耗排名 | 各班积分 | 最低消耗排名 |\n")
md.append("|:---:|:---:|:---:|:---:|:---:|:---:|\n")
for t in teams:
    if t not in team_stats: continue
    s = team_stats[t]
    md.append(f"| {t} | {s['排名比']} | {s['排名水']} | {s['排名电']} | {s['积分']} | {s['总排名']} |\n")

md.append("\n---\n\n## 📋 各班明细\n\n")
for t in teams:
    if t not in team_stats: continue
    s = team_stats[t]
    md.append(f"### {t}\n\n")
    md.append("| 日期 | 类型 | 蒸汽消耗 | 糖浆加量 | 水消耗 | 电消耗 | 水分 |\n")
    md.append("|:---:|:---:|:---:|:---:|:---:|:---:|:---:|\n")
    for d in s["明细"]:
        md.append(f"| {d['日期']} | {d['类型']} | {d['蒸汽']} | {d['糖浆']} | {d['水']} | {d['电']} | {d['水分']} |\n")
    md.append(f"| **小计** | 正常班: {s['班数']} | {s['蒸汽']} | {s['糖浆']} | {s['水']} | {s['电']} | {s['扣分']} |\n")
    md.append(f"| **平均** | | 比值: {s['比']} | | 水均: {s['水均']} | 电均: {s['电均']} | |\n")
    md.append("\n")

with open("README.md", "w", encoding="utf-8") as f:
    f.writelines(md)