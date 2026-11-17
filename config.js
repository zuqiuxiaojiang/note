/* ============================================================
 *  config.js —— 报表配置（外观、名单、判定标准、密码）
 * ============================================================
 *
 *  和 data.js 的分工：
 *    config.js 管"怎么算、怎么显示"：标题、导航、班组名单、水分标准、图标、密码
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

  /* ── 前端密码（仅心理门槛，源码可见，防不住懂技术的人） ──
   *
   *   enabled      : true 才启用密码层，false 完全不弹窗
   *   accept       : 密码数组，任意一个都通过（区分大小写）
   *   maxAttempts  : 最多尝试次数，用完跳 failRedirect
   *   promptText   : 弹窗里的提示文字
   *   failRedirect : 取消输入或次数用完时跳转的地址
   *   messages     : 各种弹窗文案，{remain} 会自动替换成剩余次数
   */
  password: {
    enabled: false,
    accept: ['biang', 'ㄅㄧㄤ', '𰻝', '𰻞'],
    maxAttempts: 3,
    promptText: '請輸入biangbiang麵的biang字：',
    failRedirect: 'https://zuqiuxiaojiang.github.io',
    messages: {
      correct:   '密码正确！',
      wrong:     '密码错误！您还有 {remain} 次机会',
      cancelled: '您取消了操作，页面将返回上一页',
      exhausted: '您已用完所有尝试机会，页面将返回上一页',
    },
  },
};