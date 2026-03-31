# HFUT 校园网自动登录脚本

> 适用于合肥工业大学翡翠湖校区无线网络 `HFUT-WiFi`，连接 WiFi 后自动完成认证。
> 脚本支持 **macOS / Linux / Windows**，可通过命令行、环境变量或配置文件配置账号密码。

## ✨ 特性

- 🚀 自动获取本机 IP 和接入点名称
- 🔄 支持重试，自动处理已登录、密码错误、强制踢掉其他设备等情况
- 📝 详细日志记录（`~/.hfut_login.log`）
- 🎯 支持命令行参数、环境变量、配置文件三种配置方式
- ⚙️ 可配合系统计划任务实现开机/联网自动运行

## 📦 环境要求

- Python 3.6+
- `requests` 库

## 🔧 安装步骤

### 1. 安装 Python 3 和 requests

#### macOS（推荐使用 Homebrew）

bash

```
brew install python@3.14
pip3 install --user --break-system-packages requests
```



#### Linux / Windows

请从 [python.org](https://www.python.org/downloads/) 下载安装 Python 3，然后执行：

bash

```
pip install requests
```



### 2. 下载脚本

bash

```
git clone https://github.com/yourusername/hfut-autologin.git
cd hfut-autologin
```



### 3. 配置账号

有以下三种方式，**任选其一**：

#### 方式一：命令行参数

bash

```
python3 hfut_login.py -u 学号 -p 密码
```



#### 方式二：环境变量

在 `~/.bashrc`（或 `~/.zshrc`）中添加：

bash

```
export HFUT_USERNAME="你的学号"
export HFUT_PASSWORD="你的密码"
```



然后执行 `source ~/.bashrc`（或重新打开终端）。

#### 方式三：配置文件（推荐）

复制示例配置并修改：

bash

```
cp config.example.json config.json
nano config.json   # 填入真实账号密码
```



`config.json` 格式：

json

```
{
    "username": "你的学号",
    "password": "你的密码"
}
```



### 4. 测试脚本

bash

```
python3 hfut_login.py
```



如果看到 `✅ 登录成功` 或 `⚠️ 当前设备已登录`，说明一切正常。

## 🔧 自动化方案

### 🍎 macOS – 使用 launchd

创建 plist 文件 `~/Library/LaunchAgents/com.hfut.login.plist`：

xml

```
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.hfut.login</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/python3</string>
        <string>/Users/yourusername/hfut-autologin/hfut_login.py</string>
        <string>--config</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StartInterval</key>
    <integer>3600</integer>
    <key>StandardOutPath</key>
    <string>/Users/yourusername/hfut-autologin/login.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/yourusername/hfut-autologin/error.log</string>
</dict>
</plist>
```



加载任务：

bash

```
launchctl load ~/Library/LaunchAgents/com.hfut.login.plist
```



脚本将在开机时自动执行，并每隔 3600 秒（1 小时）重新执行一次。

### 🐧 Linux – 使用 crontab

编辑 crontab：

bash

```
crontab -e
```



添加一行（每小时执行一次）：

bash

```
0 * * * * /usr/bin/python3 /home/yourusername/hfut-autologin/hfut_login.py --config >> /home/yourusername/hfut-autologin/login.log 2>&1
```



### 🪟 Windows – 使用任务计划程序

1. 打开“任务计划程序”，创建基本任务
2. 触发器选择“登录时”或“每天”
3. 操作选择“启动程序”
   - 程序：`python.exe`
   - 参数：`hfut_login.py --config`
   - 起始目录：脚本所在文件夹
4. 保存任务即可自动运行

## 🌐 自定义登录 URL

不同校区、不同运营商的认证地址可能不同，常见地址如下：

| 区域/类型  | 登录地址                             |
| :--------- | :----------------------------------- |
| 宣城校区   | `http://172.18.3.3:801/eportal/`     |
| 翡翠湖校区 | `http://210.45.240.105:801/eportal/` |
| 屯溪路校区 | `http://210.45.240.105:801/eportal/` |

除翡翠湖校区外其他校区仅供示范，可通过浏览器访问校园网登录页面，抓包获取实际提交的地址，然后修改 `config.json` 中的 `login_url`。

## 🔒 安全建议

- 密码以明文形式存储在 `config.json` 中，**切勿将该文件提交到公开仓库**
- 可在 `.gitignore` 中添加 `config.json` 避免误提交
- 如需更高安全性，可考虑使用 Python 的 `keyring` 库存储密码（本项目暂未集成）

## ❓ 常见问题

### 1. 提示“requests 模块未找到”

请运行 `pip3 install requests` 安装。

### 2. 登录后依然无法上网

可能是 IP 已过期或设备限制，请尝试手动登录网页版确认。

### 3. 如何调试？

修改 `config.json` 中的 `check_url` 为一个可访问的网址（如 `https://www.baidu.com`），运行脚本后查看输出或日志文件。

## 📄 开源协议

MIT License
