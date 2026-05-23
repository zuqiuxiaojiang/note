import frontmatter
import glob
import os
import re

# ═══════════════════════════════════════════════════════
# 第一部分：配置区（按需修改）
# ═══════════════════════════════════════════════════════

# 报表网址
report_url = "https://zuqiuxiaojiang.github.io/note/"

# 班组列表
teams = ["甲班", "乙班", "丙班", "丁班"]

# 数据文件夹路径
data_path = "生产数据/**/*.md"

# 工艺分基数
process_base_score = 40


# ═══════════════════════════════════════════════════════
# 第二部分：工具函数（共用）
# ═══════════════════════════════════════════════════════

def clean_number(v):
    """清洗数字：兼容引号、空格、单位、中文符号"""
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
    """判断是否为正常班（有有效蒸汽消耗数据）"""
    return clean_number(p.get("蒸汽消耗")) is not None


def safe_num(p, key):
    """安全读取数字，空值返回0"""
    v = clean_number(p.get(key))
    return v if v is not None else 0


# ═══════════════════════════════════════════════════════
# 第三部分：水分处理（共用）
# ═══════════════════════════════════════════════════════

def get_water_status(val):
    """
    水分状态与扣分自动判断（两套标准）
    <=5 使用123标准：=2合格，<<2扣5分，>2扣10分
    >5 使用考核标准：10.5~11.5合格，<<10.5扣5分，>11.5扣10分
    返回: (emoji标记, 扣分)
    """
    if val <= 5:
        if val == 2:
            return ("✅", 0)
        elif val < 2:
            return ("🔵", -5)
        else:
            return ("🔴", -10)
    else:
        if 10.5 <= val <= 11.5:
            return ("✅", 0)
        elif val < 10.5:
            return ("🔵", -5)
        else:
            return ("🔴", -10)


def format_water(m):
    """只返回颜色emoji，不显示数字"""
    val = clean_number(m)
    if val is None:
        return "-"
    emoji, _ = get_water_status(val)
    return emoji


def calc_water_score(m):
    """计算水分扣分"""
    val = clean_number(m)
    if val is None:
        return 0
    _, score = get_water_status(val)
    return score


# ═══════════════════════════════════════════════════════
# 第四部分：排名算法（共用）
# ═══════════════════════════════════════════════════════

def rank(arr, key, asc=True):
    """密集排名：并列同一名次"""
    s = sorted(arr, key=lambda x: x[1][key] if isinstance(x[1][key], (int, float)) else float('inf'))
    if not asc:
        s.reverse()
    vals = [x[1][key] for x in s if isinstance(x[1][key], (int, float))]
    unique = sorted(set(vals), reverse=not asc)
    return {v: i+1 for i, v in enumerate(unique)}


# ═══════════════════════════════════════════════════════
# 第五部分：数据读取（共用）
# ═══════════════════════════════════════════════════════

def load_pages():
    """扫描所有笔记，读取frontmatter"""
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
# 第六部分：班组统计（共用核心逻辑）
# ═══════════════════════════════════════════════════════

def calc_team_stats(pages):
    """按班组计算所有统计数据"""
    team_stats = {}
    all_repairs = []
    
    for team in teams:
        rows = [p for p in pages if p.get("班组") == team]
        rows.sort(key=lambda x: str(x.get("日期", "")))
        
        蒸汽合计 = 糖浆合计 = 水合计 = 电合计 = 0
        正常班数 = 0
        水分扣分 = 0
        合格数 = 0
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
            本条扣分 = calc_water_score(m)
            水分扣分 += 本条扣分
            
            # 工艺分合格判断：正常班且不扣分
            if has_data and 本条扣分 == 0:
                合格数 += 1
            
            # 收集检维修
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
        工艺分 = round(process_base_score / 正常班数 * 合格数, 2) if 正常班数 > 0 else 0
        
        team_stats[team] = {
            "蒸汽": 蒸汽合计, "糖浆": 糖浆合计, "水": round(水合计, 1), "电": 电合计,
            "扣分": 水分扣分, "班数": 正常班数, "合格数": 合格数, "工艺分": 工艺分,
            "比": 蒸汽糖浆比, "水均": 水平均, "电均": 电平均,
            "明细": 明细
        }
    
    return team_stats, all_repairs


def calc_rankings(team_stats):
    """计算各项排名"""
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
# 第七部分：报表生成（按需选用）
# ═══════════════════════════════════════════════════════

def generate_summary_table(md, team_stats):
    """生成汇总表"""
    md.append("## 📊 消耗统计汇总\n\n")
    md.append("| 班组 | 蒸汽用量 | 糖浆加量 | 水量 | 电量 | 水分扣分 |\n")
    md.append("|:---:|:---:|:---:|:---:|:---:|:---:|\n")
    for t in teams:
        if t not in team_stats: continue
        s = team_stats[t]
        md.append(f"| {t} | {s['蒸汽']} | {s['糖浆']} | {s['水']} | {s['电']} | {s['扣分']} |\n")
    return md


def generate_average_table(md, team_stats):
    """生成平均分表（含工艺分）"""
    md.append("\n## 📈 平均分\n\n")
    md.append("| 班组 | 蒸汽÷糖浆 | 水量÷正常班 | 电量÷正常班 | 工艺分 |\n")
    md.append("|:---:|:---:|:---:|:---:|:---:|\n")
    for t in teams:
        if t not in team_stats: continue
        s = team_stats[t]
        md.append(f"| {t} | {s['比']} | {s['水均']} | {s['电均']} | {s['工艺分']} |\n")
    return md


def generate_ranking_table(md, team_stats):
    """生成积分排名表"""
    stats_list = calc_rankings(team_stats)
    md.append("\n## 🏆 积分排名\n\n")
    md.append("| 班组 | 蒸汽÷糖浆排名 | 水消耗排名 | 电消耗排名 | 各班积分 | 最低消耗排名 |\n")
    md.append("|:---:|:---:|:---:|:---:|:---:|:---:|\n")
    for t, s in stats_list:
        md.append(f"| {t} | {s['排名比']} | {s['排名水']} | {s['排名电']} | {s['积分']} | {s['总排名']} |\n")
    return md


def generate_repair_table(md, all_repairs):
    """生成检维修记录表（无记录时跳过）"""
    if not all_repairs:
        return md
    md.append("\n## 🔧 检维修记录\n\n")
    md.append("| 班组 | 日期 |\n")
    md.append("|:---:|:---:|\n")
    for r in all_repairs:
        md.append(f"| {r['班组']} | {r['日期']} |\n")
    return md


def generate_detail_tables(md, team_stats):
    """生成各班明细表（只含小计行）"""
    md.append("\n---\n\n## 📋 各班明细\n\n")
    for t in teams:
        if t not in team_stats: continue
        s = team_stats[t]
        md.append(f"### {t}\n\n")
        md.append("| 日期 | 类型 | 蒸汽消耗 | 糖浆加量 | 水消耗 | 电消耗 | 水分 |\n")
        md.append("|:---:|:---:|:---:|:---:|:---:|:---:|:---:|\n")
        for d in s["明细"]:
            md.append(f"| {d['日期']} | {d['类型']} | {d['蒸汽']} | {d['糖浆']} | {d['水']} | {d['电']} | {format_water(d['水分'])} |\n")
        md.append(f"| **小计** | 正常班: {s['班数']} | {s['蒸汽']} | {s['糖浆']} | {s['水']} | {s['电']} | {s['扣分']} |\n")
        md.append("\n")
    return md


# ═══════════════════════════════════════════════════════
# 第八部分：主程序（按需组装）
# ═══════════════════════════════════════════════════════

def main():
    # 1. 读取数据
    pages = load_pages()
    
    # 2. 计算统计
    team_stats, all_repairs = calc_team_stats(pages)
    
    # 3. 组装报表（按需选用生成函数）
    md = [
        "# 生产数据报表\n\n",
        f"🌐 [在线报表]({report_url})\n\n"
    ]
    
    md = generate_summary_table(md, team_stats)      # 汇总表
    md = generate_average_table(md, team_stats)      # 平均表（含工艺分）
    md = generate_ranking_table(md, team_stats)      # 排名表
    md = generate_repair_table(md, all_repairs)      # 检维修（可选）
    md = generate_detail_tables(md, team_stats)      # 明细表
    
    # 4. 输出
    with open("README.md", "w", encoding="utf-8") as f:
        f.writelines(md)


if __name__ == "__main__":
    main()