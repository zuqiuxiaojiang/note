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
 *    · 改密码文案    → REPORT_CONFIG.password.ui
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
   *   enabled      : true 才启用密码层，false 完全不弹窗直接显示
   *   accept       : 密码数组，任意一个都通过（区分大小写）
   *   maxAttempts  : 最多尝试次数，用完跳 failRedirect
   *   failRedirect : 取消或次数用完时跳转的地址
   *
   *   界面文案都在这里，想改提示语只改这个段。
   */
  password: {
    enabled: true,
    accept: ['biang', 'ㄅㄧㄤ', '𰻝', '𰻞',""],
    maxAttempts: 3,
    failRedirect: 'https://zuqiuxiaojiang.github.io',

    /* 界面文案 */
    ui: {
      title: '🔒 访问验证',
      hint: '請輸入 biangbiang 麵的 biang 字',
      placeholder: '在此输入密码…',
      submit: '进入',
      cancel: '返回首页',
      attemptsText: '剩余 {remain} 次机会',
      errorEmpty: '请输入密码',
      errorWrong: '密码错误',
      errorExhausted: '尝试次数已用完，即将返回首页…',
      cancelled: '已取消，即将返回…',
    },
  },
};