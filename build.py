import frontmatter
import glob
import os
import re

# ═══════════════════════════════════════════════════════
# 一、全局配置
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
# 二、通用工具函数
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


def format_num(v, decimals=4):
    """
    统一格式化数值显示：保留指定小数位，去掉末尾无意义0
    例如：60.599999999999994 → "60.6", 89.0 → "89", 12345.0 → "12345"
    如需修改默认小数位数，修改 decimals 参数即可
    """
    if v is None or v == "" or v == "-":
        return "-"
    try:
        n = float(v)
        # 先 round 到指定小数位，解决浮点精度问题
        n = round(n, decimals)
        # 格式化为字符串，去掉末尾无意义0
        formatted = f"{n:.{decimals}f}"
        formatted = formatted.rstrip('0').rstrip('.')
        return formatted
    except (ValueError, TypeError):
        return str(v)


# ═══════════════════════════════════════════════════════
# 三、水分状态判定
# ═══════════════════════════════════════════════════════


def format_decimal(v, decimals=4):
    """
    格式化小数：保留指定小数位，但去掉末尾无意义的0
    例如：5.1000 -> 5.1, 5.0000 -> 5, 3.1415 -> 3.1415
    如需修改默认小数位数，修改 decimals 参数即可
    """
    if v is None or v == "" or v == "-":
        return "-"
    try:
        n = float(v)
        # 先格式化为指定小数位（保留4位）
        formatted = f"{n:.{decimals}f}"
        # 去掉末尾无意义的0
        formatted = formatted.rstrip('0').rstrip('.')
        return formatted
    except (ValueError, TypeError):
        return str(v)


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
# 四、排名计算引擎
# ═══════════════════════════════════════════════════════

def rank(arr, key, asc=True):
    s = sorted(arr, key=lambda x: x[1][key] if isinstance(x[1][key], (int, float)) else float('inf'))
    if not asc:
        s.reverse()
    vals = [x[1][key] for x in s if isinstance(x[1][key], (int, float))]
    unique = sorted(set(vals), reverse=not asc)
    return {v: i+1 for i, v in enumerate(unique)}


# ═══════════════════════════════════════════════════════
# 五、数据源加载
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
# 六、班组数据统计
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
                    "日期": p.get("日期", "-"), "类型": "🛠",
                    "蒸汽": "-", "糖浆": "-", "水": "-", "电": "-",
                    "水分": format_water(p.get("水分"))
                })
            else:
                明细.append({
                    "日期": p.get("日期", "-"), "类型": "✅",
                    "蒸汽": format_num(p.get("蒸汽消耗")),
                    "糖浆": format_num(p.get("糖浆加量")),
                    "水": format_num(p.get("水消耗")),
                    "电": format_num(p.get("电消耗")),
                    "水分": format_water(p.get("水分"))
                })
        
        # 保留原始数值用于排名计算（内部使用）
        蒸汽糖浆比_raw = round(蒸汽合计 / 糖浆合计, 4) if 糖浆合计 else "-"
        # 格式化值用于显示（去掉末尾无意义0）
        蒸汽糖浆比 = format_decimal(蒸汽糖浆比_raw, 4) if 蒸汽糖浆比_raw != "-" else "-"
        水平均_raw = round(水合计 / 正常班数, 2) if 正常班数 else "-"
        水平均 = format_decimal(水平均_raw, 4) if 水平均_raw != "-" else "-"
        电平均_raw = round(电合计 / 正常班数, 1) if 正常班数 else "-"
        电平均 = format_decimal(电平均_raw, 4) if 电平均_raw != "-" else "-"
        工艺分_raw = round(process_base_score / 正常班数 * 合格数, 2) if 正常班数 > 0 else 0
        工艺分 = format_decimal(工艺分_raw, 4) if 工艺分_raw != 0 else 0
        
        team_stats[team] = {
            "蒸汽": 蒸汽合计, "糖浆": 糖浆合计, "水": 水合计, "电": 电合计,
            "扣分": 水分扣分, "班数": 正常班数, "检维修数": 检维修数,
            "合格数": 合格数, "工艺分": 工艺分,
            "比": 蒸汽糖浆比, "水均": 水平均, "电均": 电平均,
            "比_raw": 蒸汽糖浆比_raw, "水均_raw": 水平均_raw, "电均_raw": 电平均_raw, "工艺分_raw": 工艺分_raw,
            "明细": 明细
        }
    
    return team_stats, all_repairs


def calc_rankings(team_stats):
    stats_list = [(t, team_stats[t]) for t in teams if t in team_stats]
    
    # 使用原始数值（_raw）计算排名，确保排名逻辑正确
    r_ratio = rank(stats_list, "比_raw", True)
    r_water = rank(stats_list, "水均_raw", True)
    r_elec  = rank(stats_list, "电均_raw", True)
    
    for t, s in stats_list:
        s["排名比"] = r_ratio.get(s["比_raw"], "-")
        s["排名水"] = r_water.get(s["水均_raw"], "-")
        s["排名电"] = r_elec.get(s["电均_raw"], "-")
        s["积分"] = (s["排名比"] if isinstance(s["排名比"], int) else 0) + \
                    (s["排名水"] if isinstance(s["排名水"], int) else 0) + \
                    (s["排名电"] if isinstance(s["排名电"], int) else 0)
    
    r_score = rank([(t, s) for t, s in stats_list], "积分", True)
    for t, s in stats_list:
        s["总排名"] = r_score.get(s["积分"], "-")
    
    return stats_list


# ═══════════════════════════════════════════════════════
# 八、页面头部生成
# ═══════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════
# 七、图例说明生成
# ═══════════════════════════════════════════════════════

def generate_legend(md):
    """生成图例说明表"""
    md.append("## 📖 图例说明\n\n")
    md.append("| 符号 | 含义 | 说明 |\n")
    md.append("|:---:|:---|:---|\n")
    md.append("| 🍂 | 水分偏低 | 水分低于标准值，扣 5 分 |\n")
    md.append("| 👌 | 水分正常 | 水分在标准范围内，不扣分 |\n")
    md.append("| 💦 | 水分偏高 | 水分高于标准值，扣 10 分 |\n")
    md.append("| ✅ | 正常班 | 正常生产班次 |\n")
    md.append("| 🛠 | 检维修 | 设备检修维护班次 |\n")
    md.append("\n")
    return md


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
# 九、报表内容生成
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
        md.append(f"| **小计** | ✅: {s['班数']} \\| 🛠: {s['检维修数']} | {format_num(s['蒸汽'])} | {format_num(s['糖浆'])} | {format_num(s['水'])} | {format_num(s['电'])} | {s['扣分']} |\n")
        md.append("\n")
    return md


# ═══════════════════════════════════════════════════════
# 十、程序入口
# ═══════════════════════════════════════════════════════

def main():
    pages = load_pages()
    team_stats, all_repairs = calc_team_stats(pages)
    
    md = []
    
    # 先生成自定义页头
    md = generate_header(md)
    md = generate_legend(md)
    
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