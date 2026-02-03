# 第一步：Termux 环境配置

### 1. 更新源并安装 Git（如遇询问按 Y）
pkg update -y && pkg upgrade -y
pkg install git -y

### 2. 授予存储权限（会弹出授权窗口，请点击允许）
termux-setup-storage

### 3. 进入存储目录并创建 Obsidian 文件夹
cd storage/emulated/0
### 4. 配置 Git 全局身份（修改引号内容为你的信息）
git config --global user.name "zuqiuxiaojiang"
git config --global user.email "553777402@qq.com"

### 5. 验证配置
echo "用户名：" && git config --global user.name
echo "邮箱：" && git config --global user.email
###### 需修改："你的英文用户名" 和 "你的Gitee注册邮箱"（保持引号）

# 第二步：克隆仓库

### 先删除可能的残留文件夹（如有重要数据请提前备份）
rm -rf note

### 克隆仓库（修改以下三个地方：用户名、Token、仓库名）
git clone https://用户名:Token@gitee.com/用户名/note.git

### 示例（仅供格式参考，请勿直接复制）：
git clone https://zuqiuxiaojiang:私人令牌@gitee.com/zuqiuxiaojiang/note.git

###### 需修改：将两处 用户名 替换为 Gitee 英文用户名，将 Token 替换为 32 位私人令牌


# 第三步：创建 .gitignore

在 Obsidian 中新建文件 .gitignore，粘贴以下内容：

### Obsidian 系统配置（不同设备不同步）
.obsidian/workspace.json
.obsidian/workspaces.json
.obsidian/workspace-mobile.json
.obsidian/plugins/obsidian-git/data.json

### 缓存与临时文件
.obsidian/cache/
.trash/
.DS_Store
Thumbs.db
*.tmp

### 私人文件（不同步到云端）
私人笔记/
日记/private/
Personal/

### 大文件（节省流量）
*.mp4
*.mov
*.avi
*.zip
*.tar.gz
*.rar
*.psd
*.dmg


# 第四步：首次提交测试

### 进入仓库目录
cd ~/storage/shared/Obsidian/note

### 添加 .gitignore 到 Git
git add .gitignore

### 首次提交
git commit -m "初始化：添加忽略文件"

### 推送到 Gitee
git push origin main

### 如果提示主分支是 master 而非 main，使用：
### git push origin master

###### 备用：强制覆盖本地

cd ~/storage/shared/Obsidian/note
git fetch origin
git reset --hard origin/main
或 git reset --hard origin/master

###### 提示：所有命令在 Termux 中长按即可粘贴，执行时注意观察报错信息。如果克隆步骤提示 already exists，请先执行第一步中的 rm -rf note。
