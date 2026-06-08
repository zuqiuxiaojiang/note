import frontmatter
import glob
import os
import re

# ═══════════════════════════════════════════════════════
# 第一部分：配置区
# ═══════════════════════════════════════════════════════

report_url = "https://zuqiuxiaojiang.github.io/note/"
teams = ["甲班", "乙班", "丙班", "丁班"]
data_path = "生产数据/**/*.md"
process_base_score = 40

# 自定义导航链接（按需添加）
nav_links = [
    {"text": "首页", "url": "https://zuqiuxiaojiang.github.io"},
    {"text": "个人", "url": "https://zuqiuxiaojiang.github.io/-"},
    {"text": "工作", "url": "https://zuqiuxiaojiang.github.io/_"},
    {"text": "NOTE", "url": "https://zuqiuxiaojiang.github.io/note"},
    # 在这里添加更多链接
    # {"text": "新链接", "url": "https://example.com"},
]

# 页头图片路径（相对于仓库根目录或绝对URL）
header_image = "./翼.png"  # 或 "https://你的图床地址/图片.png"
header_title = "天使之翼"


# ═══════════════════════════════════════════════════════
# 第二部分：工具函数
# ═══════════════════════════════════════════════════════

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


def safe_num(p, key):
    v = clean_number(p.get(key))
    return v if v is not None else 0


def has_any_data(p):
    keys = ["蒸汽消耗", "糖浆加量", "水消耗", "电消耗"]
    return any(clean_number(p.get(k)) is not None for k in keys)


def format_num(v):
    if v is None or v == "" or v == "-":
        return "-"
    try:
        n = float(v)
        if n == int(n):
            return str(int(n))
        return str(n)
    except (ValueError, TypeError):
        return str(v)


# ═══════════════════════════════════════════════════════
# 第三部分：水分处理
# ═══════════════════════════════════════════════════════

def get_water_status(val):
    if val <= 5:
        if val == 2:
            return ("👌", 0)
        elif val < 2:
            return ("🍂", -5)
        else:
            return ("💦", -10)
    else:
        if 10.5 <= val <= 11.5:
            return ("👌", 0)
        elif val < 10.5:
            return ("🍂", -5)
        else:
            return ("💦", -10)


def format_water(m):
    val = clean_number(m)
    if val is None:
        return "-"
    emoji, _ = get_water_status(val)
    return emoji


def calc_water_score(m):
    val = clean_number(m)
    if val is None:
        return 0
    _, score = get_water_status(val)
    return score


# ═══════════════════════════════════════════════════════
# 第四部分：排名算法
# ═══════════════════════════════════════════════════════

def rank(arr, key, asc=True):
    s = sorted(arr, key=lambda x: x[1][key] if isinstance(x[1][key], (int, float)) else float('inf'))
    if not asc:
        s.reverse()
    vals = [x[1][key] for x in s if isinstance(x[1][key], (int, float))]
    unique = sorted(set(vals), reverse=not asc)
    return {v: i+1 for i, v in enumerate(unique)}


# ═══════════════════════════════════════════════════════
# 第五部分：数据读取
# ═══════════════════════════════════════════════════════

def load_pages():
    pages = []
    for path in glob.glob(data_path, recursive=True):
        try:
            post = frontmatter.load(path)
            data = post.metadata
            if data.get("班组"):
                pages.append(data)
        except Exception as e:
            print(f"读取失败 {path}: {e}")
    return pages


# ═══════════════════════════════════════════════════════
# 第六部分：班组统计
# ═══════════════════════════════════════════════════════

def calc_team_stats(pages):
    team_stats = {}
    all_repairs = []
    
    for team in teams:
        rows = [p for p in pages if p.get("班组") == team]
        rows.sort(key=lambda x: str(x.get("日期", "")))
        
        蒸汽合计 = 糖浆合计 = 水合计 = 电合计 = 0
        正常班数 = 0
        检维修数 = 0
        水分扣分 = 0
        合格数 = 0
        明细 = []
        
        for p in rows:
            is_repair = p.get("类型") == "检维修"
            has_data = has_any_data(p) and not is_repair
            
            if has_data:
                蒸汽合计 += safe_num(p, "蒸汽消耗")
                糖浆合计 += safe_num(p, "糖浆加量")
                水合计   += safe_num(p, "水消耗")
                电合计   += safe_num(p, "电消耗")
                正常班数 += 1
            
            if is_repair:
                检维修数 += 1
            
            m = p.get("水分")
            本条扣分 = calc_water_score(m)
            水分扣分 += 本条扣分
            
            if has_data and 本条扣分 == 0:
                合格数 += 1
            
            if is_repair:
                all_repairs.append({"班组": team, "日期": p.get("日期", "-")})
            
            if is_repair:
                明细.append({
                    "日期": p.get("日期", "-"), "类型": "检维修",
                    "蒸汽": "-", "糖浆": "-", "水": "-", "电": "-",
                    "水分": format_water(p.get("水分"))
                })
            else:
                明细.append({
                    "日期": p.get("日期", "-"), "类型": "正常",
                    "蒸汽": format_num(p.get("蒸汽消耗")),
                    "糖浆": format_num(p.get("糖浆加量")),
                    "水": format_num(p.get("水消耗")),
                    "电": format_num(p.get("电消耗")),
                    "水分": format_water(p.get("水分"))
                })
        
        蒸汽糖浆比 = round(蒸汽合计 / 糖浆合计, 4) if 糖浆合计 else "-"
        水平均 = round(水合计 / 正常班数, 2) if 正常班数 else "-"
        电平均 = round(电合计 / 正常班数, 1) if 正常班数 else "-"
        工艺分 = round(process_base_score / 正常班数 * 合格数, 2) if 正常班数 > 0 else 0
        
        team_stats[team] = {
            "蒸汽": 蒸汽合计, "糖浆": 糖浆合计, "水": 水合计, "电": 电合计,
            "扣分": 水分扣分, "班数": 正常班数, "检维修数": 检维修数,
            "合格数": 合格数, "工艺分": 工艺分,
            "比": 蒸汽糖浆比, "水均": 水平均, "电均": 电平均,
            "明细": 明细
        }
    
    return team_stats, all_repairs


def calc_rankings(team_stats):
    stats_list = [(t, team_stats[t]) for t in teams if t in team_stats]
    
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
    
    return stats_list


# ═══════════════════════════════════════════════════════
# 第七部分：页头生成（新增）
# ═══════════════════════════════════════════════════════

def generate_header(md):
    """生成自定义 HTML 页头"""
    # 导航链接拼接
    nav_items = " | ".join([f'<a href="{link["url"]}">{link["text"]}</a>' for link in nav_links])
    
    header = f'''<!-- 引入外部CSS文件 -->
<link rel="stylesheet" href="styles.css">

<h1>
<img src="{header_image}" alt="图片" class="inline-image" />
<span class="inline-title">{header_title}</span>
</h1>

## NOTE：

<h3>
<p>
	{nav_items}
</p>
</h3>

'''
    md.append(header)
    return md


# ═══════════════════════════════════════════════════════
# 第八部分：报表生成
# ═══════════════════════════════════════════════════════

def generate_summary_table(md, team_stats):
    md.append("## 📊 消耗统计汇总\n\n")
    md.append("| 班组 | 蒸汽用量 | 糖浆加量 | 水量 | 电量 | 水分扣分 |\n")
    md.append("|:---:|:---:|:---:|:---:|:---:|:---:|\n")
    for t in teams:
        if t not in team_stats:
            continue
        s = team_stats[t]
        md.append(f"| {t} | {format_num(s['蒸汽'])} | {format_num(s['糖浆'])} | {format_num(s['水'])} | {format_num(s['电'])} | {s['扣分']} |\n")
    return md


def generate_average_table(md, team_stats):
    md.append("\n## 📈 平均分\n\n")
    md.append("| 班组 | 蒸汽÷糖浆 | 水量÷正常班 | 电量÷正常班 | 工艺分 |\n")
    md.append("|:---:|:---:|:---:|:---:|:---:|\n")
    for t in teams:
        if t not in team_stats:
            continue
        s = team_stats[t]
        md.append(f"| {t} | {s['比']} | {format_num(s['水均'])} | {format_num(s['电均'])} | {s['工艺分']} |\n")
    return md


def generate_ranking_table(md, team_stats):
    stats_list = calc_rankings(team_stats)
    md.append("\n## 🏆 积分排名\n\n")
    md.append("| 班组 | 蒸汽÷糖浆排名 | 水消耗排名 | 电消耗排名 | 各班积分 | 最低消耗排名 |\n")
    md.append("|:---:|:---:|:---:|:---:|:---:|:---:|\n")
    for t, s in stats_list:
        md.append(f"| {t} | {s['排名比']} | {s['排名水']} | {s['排名电']} | {s['积分']} | {s['总排名']} |\n")
    return md


def generate_repair_table(md, all_repairs):
    if not all_repairs:
        return md
    md.append("\n## 🔧 检维修记录\n\n")
    md.append("| 班组 | 日期 |\n")
    md.append("|:---:|:---:|\n")
    for r in all_repairs:
        md.append(f"| {r['班组']} | {r['日期']} |\n")
    return md


def generate_detail_tables(md, team_stats):
    md.append("\n---\n\n## 📋 各班明细\n\n")
    for t in teams:
        if t not in team_stats:
            continue
        s = team_stats[t]
        total = s['班数'] + s['检维修数']
        md.append(f"### {t}（{total}）\n\n")
        md.append("| 日期 | 类型 | 蒸汽消耗 | 糖浆加量 | 水消耗 | 电消耗 | 水分 |\n")
        md.append("|:---:|:---:|:---:|:---:|:---:|:---:|:---:|\n")
        for d in s["明细"]:
            md.append(f"| {d['日期']} | {d['类型']} | {d['蒸汽']} | {d['糖浆']} | {d['水']} | {d['电']} | {d['水分']} |\n")
        md.append(f"| **小计** | 正常班: {s['班数']} \\| 检维修: {s['检维修数']} | {format_num(s['蒸汽'])} | {format_num(s['糖浆'])} | {format_num(s['水'])} | {format_num(s['电'])} | {s['扣分']} |\n")
        md.append("\n")
    return md


# ═══════════════════════════════════════════════════════
# 第九部分：主程序
# ═══════════════════════════════════════════════════════

def main():
    pages = load_pages()
    team_stats, all_repairs = calc_team_stats(pages)
    
    md = []
    
    # 先生成自定义页头
    md = generate_header(md)
    
    # 再生成报表内容
    # 在这里的链接[在线报表]可以注释掉
#    md.append(f"🌐 [在线报表]({report_url})\n\n")
    md = generate_summary_table(md, team_stats)
    md = generate_average_table(md, team_stats)
    md = generate_ranking_table(md, team_stats)
    md = generate_repair_table(md, all_repairs)
    md = generate_detail_tables(md, team_stats)
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.writelines(md)


if __name__ == "__main__":
    main()