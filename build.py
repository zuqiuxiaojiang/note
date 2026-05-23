import frontmatter
import glob
import os
import re
from collections import defaultdict

# ========== 数字清洗：兼容引号、空格、单位、中文符号 ==========
def clean_number(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if not isinstance(v, str):
        return None
    s = v.strip().strip('"').strip('"').strip("'").strip("'").strip("‘").strip("’")
    s = s.replace(",", "").replace("，", "")
    m = re.match(r'^-?\d+(\.\d+)?', s)
    if m:
        try:
            return float(m.group())
        except ValueError:
            return None
    return None

def has_valid_data(p):
    return clean_number(p.get("蒸汽消耗")) is not None

def safe_num(p, key):
    v = clean_number(p.get(key))
    return v if v is not None else 0

# ========== 水分状态：两种标准同时显示 ==========
def format_water(m):
    if m is None or m == "" or m == "-":
        return "-"
    try:
        val = float(m)
        
        # 简化输入标准（1,2,3）
        if val == 2:
            simple = f"🟢{val}"
        elif val < 2:
            simple = f"🔵{val}"
        else:
            simple = f"🔴{val}"
        
        # 标准考核（10.5~11.5）
        if 10.5 <= val <= 11.5:
            standard = f"✅{val}"
        elif val < 10.5:
            standard = f"🔵{val}"
        else:
            standard = f"🔴{val}"
        
        # 同时显示两种判定
        return f"{simple}/{standard}"
    except (ValueError, TypeError):
        return str(m)

# ========== 扫描所有笔记 ==========
pages = []
for path in glob.glob("生产数据/**/*.md", recursive=True):
    try:
        post = frontmatter.load(path)
        data = post.metadata
        if data.get("班组"):
            pages.append(data)
    except Exception as e:
        print(f"读取失败 {path}: {e}")

# ========== 按班组分组统计 ==========
teams = ["甲班", "乙班", "丙班", "丁班"]
team_stats = {}
all_repairs = []

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
        本条扣分 = 0
        if isinstance(m, (int, float)) and not (m != m):
            if m < 2:  本条扣分 -= 5
            if m > 2:  本条扣分 -= 10
            if m < 10.5: 本条扣分 -= 5
            if m > 11.5: 本条扣分 -= 10
            水分扣分 += 本条扣分
        
        if p.get("类型") == "检维修":
            all_repairs.append({
                "班组": team,
                "日期": p.get("日期", "-")
            })
        
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

# ========== 排名 ==========
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

# ========== 生成 README.md ==========
md = [
    "# 生产数据报表\n\n",
    f"🌐 [在线报表]({report_url})\n\n",
    "## 📊 消耗统计汇总\n\n"
]
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

if all_repairs:
    md.append("\n## 🔧 检维修记录\n\n")
    md.append("| 班组 | 日期 |\n")
    md.append("|:---:|:---:|\n")
    for r in all_repairs:
        md.append(f"| {r['班组']} | {r['日期']} |\n")

md.append("\n---\n\n## 📋 各班明细\n\n")
for t in teams:
    if t not in team_stats: continue
    s = team_stats[t]
    md.append(f"### {t}\n\n")
    md.append("| 日期 | 类型 | 蒸汽消耗 | 糖浆加量 | 水消耗 | 电消耗 | 水分(简/标) |\n")
    md.append("|:---:|:---:|:---:|:---:|:---:|:---:|:---:|\n")
    for d in s["明细"]:
        md.append(f"| {d['日期']} | {d['类型']} | {d['蒸汽']} | {d['糖浆']} | {d['水']} | {d['电']} | {format_water(d['水分'])} |\n")
    md.append(f"| **小计** | 正常班: {s['班数']} | {s['蒸汽']} | {s['糖浆']} | {s['水']} | {s['电']} | {s['扣分']} |\n")
    md.append(f"| **平均** | | 比值: {s['比']} | | 水均: {s['水均']} | 电均: {s['电均']} | |\n")
    md.append("\n")

with open("README.md", "w", encoding="utf-8") as f:
    f.writelines(md)