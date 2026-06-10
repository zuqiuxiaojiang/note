import frontmatter
import glob
import os
import re

# ═══════════════════════════════════════════════════════
# 第一部分：配置区（按需修改）
# ═══════════════════════════════════════════════════════

report_url = "https://你的用户名.github.io/你的仓库名/"
teams = ["甲班", "乙班", "丙班", "丁班"]
data_path = "生产数据/**/*.md"
process_base_score = 40

# 水分标准选择：0=自动判断，1=123标准(=2合格)，2=考核标准(11~12合格)
water_standard = 0  # ← 这里改：0自动，1用2的标准，2用11的标准

# 自定义导航链接
nav_links = [
    {"text": "首页", "url": "https://zuqiuxiaojiang.github.io"},
    {"text": "个人", "url": "https://zuqiuxiaojiang.github.io/-"},
    {"text": "工作", "url": "https://zuqiuxiaojiang.github.io/_"},
    {"text": "NOTE", "url": "https://zuqiuxiaojiang.github.io/note"},
]

# 页头图片和标题
header_image = "./翼.png"
header_title = "天使之翼"

# 图例emoji配置（日后修改这里即可）
ICON_NORMAL = "✅"      # 正常班标记
ICON_REPAIR = "🛠"       # 检维修标记
ICON_WATER_OK = "👌"     # 水分合格
ICON_WATER_LOW = "🍂"    # 水分偏干
ICON_WATER_HIGH = "💦"   # 水分偏潮


# ═══════════════════════════════════════════════════════
# 第二部分：工具函数
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


def safe_num(p, key):
    """安全读取数字，空值返回0"""
    v = clean_number(p.get(key))
    return v if v is not None else 0


def has_any_data(p):
    """判断该行是否有任意数据（蒸汽/糖浆/水/电任一即可）"""
    keys = ["蒸汽消耗", "糖浆加量", "水消耗", "电消耗"]
    return any(clean_number(p.get(k)) is not None for k in keys)


def format_num(v):
    """
    格式化数字：保留最多4位小数，去掉末尾无意义0
    例如：88.7000 → 88.7，2.51260000 → 2.5126，10 → 10
    """
    if v is None or v == "" or v == "-":
        return "-"
    try:
        n = float(v)
        # 保留4位小数，去掉末尾0
        s = f"{n:.4f}"
        # 去掉末尾的0
        s = s.rstrip('0').rstrip('.') if '.' in s else s
        return s
    except (ValueError, TypeError):
        return str(v)


# ═══════════════════════════════════════════════════════
# 第三部分：水分处理（标准可选）
# ═══════════════════════════════════════════════════════

def get_water_status(val):
    """
    水分状态与扣分判断
    根据 water_standard 配置选择标准：
    - 0: 自动判断（val<=5用123标准，val>5用考核标准）
    - 1: 强制123标准（=2合格，<<2扣5分，>2扣10分）
    - 2: 强制考核标准（11~12合格，<<11扣5分，>12扣10分）
    """
    # 判断使用哪套标准
    if water_standard == 1:
        use_123 = True
    elif water_standard == 2:
        use_123 = False
    else:  # water_standard == 0，自动判断
        use_123 = (val <= 5)
    
    if use_123:
        # 123标准：=2合格，<<2扣5分，>2扣10分
        if val == 2:
            return (ICON_WATER_OK, 0)
        elif val < 2:
            return (ICON_WATER_LOW, -5)
        else:
            return (ICON_WATER_HIGH, -10)
    else:
        # 考核标准：11~12合格，<<11扣5分，>12扣10分
        if 11 <= val <= 12:
            return (ICON_WATER_OK, 0)
        elif val < 11:
            return (ICON_WATER_LOW, -5)
        else:
            return (ICON_WATER_HIGH, -10)


def format_water(m):
    """只返回颜色emoji"""
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
# 第四部分：排名算法
# ═══════════════════════════════════════════════════════

def rank(arr, key, asc=True):
    """密集排名"""
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
    """扫描所有笔记"""
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
# 第六部分：班组统计（核心逻辑）
# ═══════════════════════════════════════════════════════

def calc_team_stats(pages):
    """按班组计算所有统计数据"""
    team_stats = {}
    all_repairs = []
    
    for team in teams:
        rows = [p for p in pages if p.get("班组") == team]
        rows.sort(key=lambda x: str(x.get("日期", "")))
        
        蒸汽合计 = 0.0  # 用浮点数避免整数精度问题
        糖浆合计 = 0.0
        水合计 = 0.0    # 水消耗用浮点数累加，避免小数精度丢失
        电合计 = 0.0
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
                水合计   += safe_num(p, "水消耗")   # 浮点数累加
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
            
            # 明细行：正常班用✅，检维修用🛠
            if is_repair:
                明细.append({
                    "日期": p.get("日期", "-"),
                    "类型": ICON_REPAIR,  # 🛠
                    "蒸汽": "-",
                    "糖浆": "-",
                    "水": "-",
                    "电": "-",
                    "水分": format_water(p.get("水分"))
                })
            else:
                明细.append({
                    "日期": p.get("日期", "-"),
                    "类型": ICON_NORMAL,  # ✅
                    "蒸汽": format_num(p.get("蒸汽消耗")),
                    "糖浆": format_num(p.get("糖浆加量")),
                    "水": format_num(p.get("水消耗")),
                    "电": format_num(p.get("电消耗")),
                    "水分": format_water(p.get("水分"))
                })
        
        # 平均值计算：用浮点数除法，保留精度
        蒸汽糖浆比 = round(蒸汽合计 / 糖浆合计, 4) if 糖浆合计 else "-"
        水平均 = round(水合计 / 正常班数, 4) if 正常班数 else "-"  # 保留4位再格式化
        电平均 = round(电合计 / 正常班数, 4) if 正常班数 else "-"
        工艺分 = round(process_base_score / 正常班数 * 合格数, 4) if 正常班数 > 0 else 0
        
        team_stats[team] = {
            "蒸汽": 蒸汽合计, "糖浆": 糖浆合计, "水": 水合计, "电": 电合计,
            "扣分": 水分扣分, "班数": 正常班数, "检维修数": 检维修数,
            "合格数": 合格数, "工艺分": 工艺分,
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
# 第七部分：页头生成（含密码验证）
# ═══════════════════════════════════════════════════════

def generate_header(md):
    """生成自定义 HTML 页头 + 密码验证 + 图例表格"""
    nav_items = " | ".join([f'<a href="{link["url"]}">{link["text"]}</a>' for link in nav_links])

    # 图例表格（方便外人理解emoji含义）
    legend = f"""## 📖 图例说明

| 符号 | 含义 |
|:---:|:---|
| {ICON_NORMAL} | 正常班 |
| {ICON_REPAIR} | 检维修 |
| {ICON_WATER_OK} | 水分合格 |
| {ICON_WATER_LOW} | 水分偏干（扣5分） |
| {ICON_WATER_HIGH} | 水分偏潮（扣10分） |

"""

    # 🔒 密码验证层（整合自用户提供的代码，已修复跳转URL）
    password_gate = r"""<!-- 设置页面过期 -->
<meta http-equiv="cache-control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="pragma" content="no-cache">
<meta http-equiv="expires" content="0">

<!-- 密码验证 -->
<SCRIPT language=JavaScript>
function password() {
    var maxAttempts = 3; // 最大尝试次数
    var correctPasswords = ["biang","ㄅㄧㄤ","𰻝", "𰻞"]; // 支持多个密码
    var attempts = 0; // 当前尝试次数

    while (attempts < maxAttempts) {
        var pass1 = prompt('請輸入biangbiang麵的biang字：', '');
        if (!pass1) { // 如果用户取消输入
            alert('您取消了操作，页面将返回上一页');
            window.location.replace("https://zuqiuxiaojiang.github.io/note"); // 返回上一页
            return;
        }
        if (correctPasswords.includes(pass1)) { // 检查密码是否在数组中
            alert('密码正确！');
            return "密码验证通过";
        } else {
            attempts++;
            alert('密码错误！您还有 ' + (maxAttempts - attempts) + ' 次机会');
        }
    }
    alert('您已用完所有尝试机会，页面将返回上一页');
    window.location.replace("https://zuqiuxiaojiang.github.io/note"); // 返回上一页
    return "密码验证失败";
}

// 调用函数
password();
</SCRIPT>
"""

    header = f"""<!-- 引入外部CSS文件 -->
<link rel="stylesheet" href="styles.css">

{password_gate}

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

{legend}
"""
    md.append(header)
    return md


# ═══════════════════════════════════════════════════════
# 第八部分：报表生成
# ═══════════════════════════════════════════════════════

def generate_summary_table(md, team_stats):
    """汇总表"""
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
    """平均表（含工艺分）"""
    md.append("\n## 📈 平均分\n\n")
    md.append("| 班组 | 蒸汽÷糖浆 | 水量÷正常班 | 电量÷正常班 | 工艺分 |\n")
    md.append("|:---:|:---:|:---:|:---:|:---:|\n")
    for t in teams:
        if t not in team_stats:
            continue
        s = team_stats[t]
        md.append(f"| {t} | {format_num(s['比'])} | {format_num(s['水均'])} | {format_num(s['电均'])} | {format_num(s['工艺分'])} |\n")
    return md


def generate_ranking_table(md, team_stats):
    """排名表"""
    stats_list = calc_rankings(team_stats)
    md.append("\n## 🏆 积分排名\n\n")
    md.append("| 班组 | 蒸汽÷糖浆排名 | 水消耗排名 | 电消耗排名 | 各班积分 | 最低消耗排名 |\n")
    md.append("|:---:|:---:|:---:|:---:|:---:|:---:|\n")
    for t, s in stats_list:
        md.append(f"| {t} | {s['排名比']} | {s['排名水']} | {s['排名电']} | {s['积分']} | {s['总排名']} |\n")
    return md


def generate_repair_table(md, all_repairs):
    """检维修记录（无记录时跳过）"""
    if not all_repairs:
        return md
    md.append("\n## 🔧 检维修记录\n\n")
    md.append("| 班组 | 日期 |\n")
    md.append("|:---:|:---:|\n")
    for r in all_repairs:
        md.append(f"| {r['班组']} | {r['日期']} |\n")
    return md


def generate_detail_tables(md, team_stats):
    """各班明细（小计行对齐修复）"""
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
        # 小计行：类型列显示正常班和检维修数量，保持7列对齐
        md.append(f"| **小计** | {ICON_NORMAL}:{s['班数']} \\| {ICON_REPAIR}:{s['检维修数']} | {format_num(s['蒸汽'])} | {format_num(s['糖浆'])} | {format_num(s['水'])} | {format_num(s['电'])} | {s['扣分']} |\n")
        md.append("\n")
    return md


# ═══════════════════════════════════════════════════════
# 第九部分：主程序
# ═══════════════════════════════════════════════════════

def main():
    pages = load_pages()
    team_stats, all_repairs = calc_team_stats(pages)
    
    md = []
    
    # 先生成自定义页头（含图例）
    md = generate_header(md)
    
    # 再生成报表内容
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