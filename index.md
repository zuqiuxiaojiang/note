<!-- 引入外部CSS文件 -->
<link rel="stylesheet" href="styles.css">

<!--在<head>后加入如下代码（设置页面过期）-->
<meta http-equiv="cache-control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="pragma" content="no-cache">
<meta http-equiv="expires" content="0">
<!--在</head>前加入如上代码（设置页面过期）-->

<!--在<head>后加入如下代码（使用window.location.replace()替换了history.go(-1)）-->
<SCRIPT language=JavaScript>
function password() {
    var maxAttempts = 3; // 最大尝试次数
    var correctPasswords = ["逢考必過","𰻝", "𰻞"]; // 支持多个密码
    var attempts = 0; // 当前尝试次数

    while (attempts < maxAttempts) {
        var pass1 = prompt('㊗️您考試💯。請輸入：逢考必過', '逢考必過');
        if (!pass1) { // 如果用户取消输入
            alert('您取消了操作，页面将返回上一页');
            window.location.replace("https://zuqiuxiaojiang.github.io/note"); // 替换为上一页的地址
            return; // 提前退出函数
        }
        if (correctPasswords.includes(pass1)) { // 检查密码是否在数组中
            alert('密码正确！');
            return "密码验证通过"; // 返回一个明确的值
        } else {
            attempts++;
            alert('密码错误！您还有 ' + (maxAttempts - attempts) + ' 次机会');
        }
    }
    alert('您已用完所有尝试机会，页面将返回上一页');
    window.location.replace("https://zuqiuxiaojiang.github.ionote"); // 替换为上一页的地址
    return "密码验证失败"; // 返回一个明确的值
}

// 调用函数，但不直接写入文档
password();
</SCRIPT>
<!--在</head>前加入如上代码（使用window.location.replace()替换了history.go(-1)）-->

<h1>
<img src="./国旗-球形.png" alt="图片" class="inline-image" />
<span class="inline-title">笔记</span>
</h1>

## 🚏🚶⛩️🏃：

###### 仅限本地查看
[[汇总仪表盘]]
[[各班明细]]