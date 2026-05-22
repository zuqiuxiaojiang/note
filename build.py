import frontmatter
import glob
import os
import sys
from collections import defaultdict

print("=== 开始运行 ===")
print("当前目录:", os.getcwd())
print("目录内容:", os.listdir("."))

# 先检查生产数据文件夹是否存在
target_dir = "生产数据"
print(f"检查文件夹 '{target_dir}':", os.path.exists(target_dir))
if os.path.exists(target_dir):
    print("子目录:", os.listdir(target_dir))

# 查找所有 md 文件
md_files = glob.glob(f"{target_dir}/**/*.md", recursive=True)
print("找到的 md 文件:", md_files)

if not md_files:
    print("错误：没有找到任何 md 文件，请检查文件夹名是否为 '生产数据'")
    sys.exit(1)

pages = []
for path in md_files:
    try:
        post = frontmatter.load(path)
        data = post.metadata
        print(f"读取 {path}: {data}")
        if data.get("班组"):
            pages.append(data)
    except Exception as e:
        print(f"读取 {path} 失败: {e}")

print(f"成功读取 {len(pages)} 条记录")

if not pages:
    print("错误：没有读取到任何有效记录，请检查 frontmatter 格式")
    sys.exit(1)

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
        has_data = False
        try:
            sd = p.get("蒸汽消耗")
            has_data = isinstance(sd, (int, float)) and not (sd != sd)  # 排除 NaN
        except:
            has_data = False
        
        if has_data:
            蒸汽合计 += float(p.get("蒸汽消耗", 0) or 0)
            糖浆合计 += float(p.get("糖浆加量", 0) or 0)
            水合计 += float(p.get("水消耗", 0) or 0)
            电合计 += float(p.get("电消耗", 0) or 0)
            正常班数 += 1
        
        m = p.get("水分")
        if isinstance(m, (int, float)):
            if m < 2: 水分扣分 -= 5
            if m > 2: 水分扣分 -= 10
            if m < 10.5: 水分扣分 -= 5
            if m > 11.5: 水分扣分 -= 10
        
        明细.append({
            "日期": str(p.get("日期", "-")),
            "类型": str(p.get("类型", "正常")),
            "蒸汽": p.get("蒸汽消耗") if has_data else "-",
            "糖浆": p.get("糖浆加量") if has_data else "-",
            "水": p.get("水消耗") if has_data else "-",
            "电": p.get("电消耗") if has_data else "-",
            "水分": str(p.get("水分", "-"))
        })
    
    比 = round(蒸汽合计 / 糖浆合计, 4) if 糖浆合计 else "-"
    水均 = round(水合计 / 正常班数, 2) if 正常班数 else "-"
    电均 = round(电合计 / 正常班数, 1) if 正常班数 else "-"
    
    team_stats[team] = {
        "蒸汽": 蒸汽合计, "糖浆": 糖浆合计, "水": round(水合计, 1), "电": 电合计,
        "扣分": 水分扣分, "班数": 正常班数, "比": 比, "水均": 水均, "电均": 电均,
        "明细": 明细
    }

stats_list = [(t, team_stats[t]) for t in teams if t in team_stats]

def rank(arr, key, asc=True):
    s = sorted(arr, key=lambda x: x[1][key] if isinstance(x[1][key], (int, float)) else float('inf'))
    if not asc: s.reverse()
    vals = [x[1][key] for x in s if isinstance(x[1][key], (int, float))]
    unique = sorted(set(vals), reverse=not asc)
    return {v: i+1 for i, v in enumerate(unique)}

r_ratio = rank(stats_list, "比", True)
r_water = rank(stats_list, "水均", True)
r_elec = rank(stats_list, "电均", True)

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

print("=== 成功生成 README.md ===")