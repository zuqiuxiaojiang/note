/* ============================================================
 *  config.js —— 报表配置（外观、名单、判定标准）
 * ============================================================
 *
 *  和 data.js 的分工：
 *    config.js 管"怎么算、怎么显示"：标题、导航、班组名单、水分标准、图标
 *    data.js   管"数据本身"：      每天的消耗记录
 *  两个文件互不干扰，各改各的。
 *
 *  改哪里：
 *    · 换标题/头像   → REPORT_CONFIG.title / headerImage
 *    · 加/减班组     → REPORT_CONFIG.teams（记得同步 data.js 里的班组字段）
 *    · 改工艺分基数  → REPORT_CONFIG.processBaseScore
 *    · 切水分标准    → REPORT_CONFIG.waterStandard（0自动 / 1 123标准 / 2 考核标准）
 *    · 换图标 emoji  → REPORT_CONFIG.icons
 *    · 开关密码      → REPORT_CONFIG.password.enabled
 *  ============================================================ */

const REPORT_CONFIG = {
  title: '天使之翼',
  headerImage: './翼.png',

  navLinks: [
    { text: '首页', url: 'https://zuqiuxiaojiang.github.io' },
    { text: '个人', url: 'https://zuqiuxiaojiang.github.io/-' },
    { text: '工作', url: 'https://zuqiuxiaojiang.github.io/_' },
    { text: 'NOTE', url: 'https://zuqiuxiaojiang.github.io/note' },
  ],

  /* 班组名单：data.js 里的"班组"字段必须在此列表内，否则该记录被忽略 */
  teams: ['甲班', '乙班', '丙班', '丁班'],

  /* 工艺分基数（满分） */
  processBaseScore: 40,

  /* 水分标准：
   *   0 = 自动判断（≤5 用 123 标准，>5 用考核标准）
   *   1 = 强制 123 标准（=2 合格，<2 扣5分，>2 扣10分）
   *   2 = 强制考核标准（10.5~11.5 合格，<10.5 扣5分，>11.5 扣10分）
   */
  waterStandard: 0,

  /* 图例 emoji（改图标只改这里，data.js 不用动） */
  icons: {
    normal:    '✅',
    repair:    '🛠',
    waterOk:   '👌',
    waterLow:  '🍂',
    waterHigh: '💦',
    waterNone: '🈚️',
  },

  /* 前端密码（仅心理门槛，源码可见，防不住懂技术的人）
   *   enabled: true 时打开页面先弹密码框，取消或连错3次跳 failRedirect
   */
  password: {
    enabled: false,
    accept: ['biang', 'ㄅㄧㄤ', '𰻝', '𰻞'],
    failRedirect: 'https://zuqiuxiaojiang.github.io',
  },
};