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
    var correctPasswords = ['biang', 'ㄅㄧㄤ', '𰻝', '𰻞',""]; // 支持多个密码
    var attempts = 0; // 当前尝试次数

    while (attempts < maxAttempts) {
        var pass1 = prompt('請輸入 biangbiang 麵的 biang 字', "\uE039");
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
    window.location.replace("https://zuqiuxiaojiang.github.io/note"); // 替换为上一页的地址
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

[首页](https://zuqiuxiaojiang.github.io) | [个人](https://zuqiuxiaojiang.github.io/-) | [工作](https://zuqiuxiaojiang.github.io/_) | [NOTE](https://zuqiuxiaojiang.github.io/note)

# Git及相关
## MGit使用方法
### 克隆仓库
远程地址：
https://gitee.com/用户名/仓库名.git | https://github.com/用户名/仓库名.git | https://gitcode.com/用户名/仓库名.git | https://atomgit.com/用户名/仓库名.git

本地路径：仓库名
### Git设置
用户名和邮箱
### 安全
SSH Keys
### 认证
用户名和ToKen

## Acode＋Git SCM 插件

### 第一步：准备 Git 环境（关键前提）

1. 打开 Acode 内置终端（Terminal）。
2. 安装 Git，执行：
   ```bash
   apk update && apk add git
   ```
3. 配置全局身份（将引号内的信息替换为你的信息）：
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "email@example.com"
   ```
   这两条命令是提交代码时的作者信息，必须配置，否则提交会失败。

如果你准备通过 SSH 连接 GitHub，还需要注意：Acode 的 Alpine 环境默认使用 Dropbear SSH，可能与 OpenSSH 冲突，导致认证失败。官方建议安装 OpenSSH 以确保兼容性。

### 第二步：安装 Git SCM 插件

在 Acode 内部完成安装：

1. 打开 Settings（设置）。
2. 选择 Plugins（插件）。
3. 搜索 “Git SCM”。
4. 点击 Install。
5. 重启 Acode，让插件生效。

### 第三步：使用 Git SCM 进行版本控制

Git SCM 插件本身主要提供源码管理（SCM）界面，很多具体操作仍需通过内置终端执行 Git 命令，或者借助图形化 Git 插件完成。以下是两种可行方式。

#### 方式一：通过内置终端使用 Git 命令（推荐，兼容性最好）

Git 安装完成后，你可以在 Acode 终端中执行标准 Git 命令，这是功能最完整的方式。

克隆仓库

```bash
git clone https://github.com/user/repo.git
```

如果是私有仓库，终端会提示你输入用户名和个人访问令牌（Token） （不是账号密码）。

克隆完成后，用 acode 命令在编辑器中打开项目：

```bash
acode repo-name
```

日常提交流程
编辑文件后，在终端中依次执行：

```bash
git add .
git commit -m "你的提交信息"
git push
```

拉取与分支

```bash
git pull                # 拉取远程更新
git branch              # 查看分支
git checkout -b feature # 创建并切换到新分支
git checkout main       # 切换回主分支
```

#### 方式二：使用图形化 Git 插件（可视化操作）

除了 Git SCM，Acode 插件市场还有基于 isomorphic-git 的图形化版本控制插件（如 Version Control (Git) ），提供按钮式界面，适合不想敲命令的场景。它的核心功能包括：

· Clone：直接克隆仓库到本地，私有仓库会弹窗提示输入 Token。
· Pull / Push：图形化同步远程代码。
· Branch Management：创建、切换、管理分支。
· Commit：填写提交信息后直接提交，配合 Status Files 查看文件变更。
· Config：在插件设置中配置用户名、邮箱等。

需要注意：这类基于 JavaScript 的插件在处理大型仓库时性能可能较慢，官方文档也明确说明“不建议用于超大仓库”。小中型项目使用没有问题。

### 认证配置：HTTPS Token 与 SSH

推送代码到 GitHub 等平台时，需要先完成认证。

#### HTTPS 方式（较简单）
使用 Personal Access Token（PAT） 代替密码。在 GitHub 的 Settings → Developer settings → Personal access tokens 中生成 Token，勾选所需的 repo 权限。克隆或推送私有仓库时，在密码提示处粘贴该 Token 即可。

#### SSH 方式（更稳定）
如果使用 SSH 地址（git@github.com:user/repo.git），需要在 Acode 终端中生成密钥并添加到 GitHub：

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

然后将公钥（~/.ssh/id_ed25519.pub）的内容复制到 GitHub 的 SSH Keys 设置中。使用 SSH 前，请确认已按官方要求处理了 Dropbear/OpenSSH 的兼容性问题。

### 常见问题提示

· 提示“git not found”或插件无法工作：说明 Git 本体没有在 Acode 终端中正确安装，回到第一步执行 apk add git。
· 认证失败：如果是 HTTPS，检查 Token 是否过期或权限不足；如果是 SSH，检查公钥是否正确添加到远程平台，以及 OpenSSH 环境是否就绪。GitHub 相关认证问题可以在插件设置中尝试重新连接或刷新缓存。
· 仓库位置：建议将克隆的仓库放在共享存储目录（如 Downloads/git），而不是 ~/storage 根目录，以避免权限或路径问题；也可以创建目录后用软链接指向。