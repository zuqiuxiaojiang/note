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
 *    · 密码后门      → REPORT_CONFIG.password.accept / prefill
 * ============================================================ */

const REPORT_CONFIG = {
  title: '天使之翼',
  headerImage: './翼.png',

  navLinks: [
    { text: '首页', url: 'https://zuqiuxiaojiang.github.io' },
    { text: '个人', url: 'https://zuqiuxiaojiang.github.io/-' },
    { text: '工作', url: 'https://zuqiuxiaojiang.github.io/_' },
    { text: 'NOTE', url: 'https://zuqiuxiaojiang.github.io/note' },
  ],

  teams: ['甲班', '乙班', '丙班', '丁班'],
  processBaseScore: 40,
  waterStandard: 0,

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
   *   enabled      : true 才启用，false 完全不弹窗直接显示
   *   accept       : 密码数组，任意一个都通过（区分大小写）
   *   prefill      : 输入框打开时预填的值
   *   maxAttempts  : 最多尝试次数，用完跳 failRedirect
   *   failRedirect : 取消或次数用完时跳转的地址
   *   showToggle   : true 显示输入框右侧的"👁 显示/隐藏"按钮
   *
   *   ★ 三种后门玩法 ★
   *   【A】必须输密码：accept 里不放 ''，prefill 留 ''
   *   【B】直接点进入就过：accept 里加 ''，prefill 留 ''
   *   【C】隐形字符：accept / prefill 都填 '\uE000'
   */
  password: {
    enabled: true,
    accept: ['biang', 'ㄅㄧㄤ', '𰻝', '𰻞',"\uE039"],
    prefill: '\uE039',
    maxAttempts: 3,
    failRedirect: 'https://zuqiuxiaojiang.github.io',
    showToggle: true,   // ← 眼睛按钮开关

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
      showPassword: '显示密码',
      hidePassword: '隐藏密码',
    },
  },
};