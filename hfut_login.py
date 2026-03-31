#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
合肥工业大学校园网自动登录脚本 (翡翠湖校区)
支持通过命令行参数、配置文件或环境变量配置账号密码。
"""

import socket
import requests
import time
import sys
import os
import re
import json
import argparse
import base64

DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
LOG_FILE = os.path.expanduser("~/.hfut_login.log")

def load_config():
    """从命令行参数、环境变量或 config.json 加载配置"""
    parser = argparse.ArgumentParser(description="合肥工业大学校园网自动登录脚本")
    parser.add_argument("-u", "--username", help="学号")
    parser.add_argument("-p", "--password", help="密码")
    parser.add_argument("-c", "--config", help="配置文件路径 (默认 config.json)")
    args = parser.parse_args()

    # 优先级: 命令行参数 > 环境变量 > 配置文件
    username = args.username
    password = args.password

    if not username or not password:
        # 尝试从环境变量读取
        username = os.environ.get("HFUT_USERNAME")
        password = os.environ.get("HFUT_PASSWORD")

    if not username or not password:
        # 尝试从配置文件读取
        config_path = args.config or DEFAULT_CONFIG_PATH
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    username = config.get("username")
                    password = config.get("password")
            except Exception:
                pass

    if not username or not password:
        print("错误: 未提供用户名或密码。请使用 -u/-p 参数、环境变量或 config.json 文件。")
        sys.exit(1)

    return username, password

def get_ip():
    """获取本机真实内网 IP（绕过代理 fake-ip）"""
    import subprocess
    for iface in ['en0', 'en1']:
        try:
            result = subprocess.run(['ipconfig', 'getifaddr', iface], capture_output=True, text=True)
            ip = result.stdout.strip()
            if ip and ip != '198.18.0.1' and '.' in ip:
                return ip
        except Exception:
            pass
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None

def get_ac_name():
    """从认证页面获取当前 AP 的 wlanacname"""
    try:
        resp = requests.get('http://210.45.240.105/a79.htm', timeout=5)
        match = re.search(r'wlanacname=([^&"\']+)', resp.text)
        if match:
            return match.group(1)
        if 'Location' in resp.headers:
            match = re.search(r'wlanacname=([^&]+)', resp.headers['Location'])
            if match:
                return match.group(1)
    except Exception:
        pass
    return None

def do_login(ip, ac_name, username, password):
    """发送登录请求"""
    url = 'http://210.45.240.105:801/eportal/'
    params = {
        'c': 'Portal',
        'a': 'login',
        'callback': 'dr1003',
        'login_method': '1',
        'user_account': username,
        'user_password': password,
        'wlan_user_ip': ip,
        'wlan_user_ipv6': '',
        'wlan_user_mac': '000000000000',
        'wlan_ac_ip': '',
        'wlan_ac_name': ac_name if ac_name else '',
        'jsVersion': '3.3.2',
        'v': str(int(time.time()))
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        return resp.text
    except Exception as e:
        return str(e)

def log(msg):
    timestamp = time.strftime("%Y年%m月%d日 %H:%M:%S")
    with open(LOG_FILE, 'a') as f:
        f.write(f"{timestamp}: {msg}\n")
    print(msg)

def main():
    username, password = load_config()
    log("=== 开始校园网认证 ===")

    # 等待 IP 获取
    ip = None
    for i in range(30):
        ip = get_ip()
        if ip and ip != '198.18.0.1':
            break
        time.sleep(1)
    if not ip or ip == '198.18.0.1':
        log(f"错误：无法获取有效 IP 地址")
        sys.exit(1)
    log(f"获取到 IP: {ip}")

    # 获取 AP 名称
    ac_name = get_ac_name()
    if ac_name:
        log(f"获取到 AP 名称: {ac_name}")
    else:
        ac_name = "HFUT-WS7880"
        log(f"未获取到 AP 名称，使用默认值: {ac_name}")

    # 尝试登录
    for attempt in range(1, 4):
        resp_text = do_login(ip, ac_name, username, password)
        # 解析返回
        try:
            json_str = re.search(r'\(({.*})\)', resp_text).group(1)
            data = json.loads(json_str)
        except Exception:
            log(f"解析响应失败: {resp_text[:100]}")
            time.sleep(3)
            continue

        result = data.get('result')
        ret_code = data.get('ret_code')
        msg = data.get('msg', '')

        if result == '1':
            log("✅ 登录成功")
            sys.exit(0)
        elif ret_code == 2:
            log("⚠️ 当前设备已登录，无需重复认证")
            sys.exit(0)
        elif ret_code == 1:
            try:
                decoded = base64.b64decode(msg).decode('utf-8')
                if 'inuse' in decoded or 'login again' in decoded:
                    log("🔄 其他设备已登录，正在强制登录...")
                    time.sleep(1)
                    continue
                elif 'ldap auth error' in decoded or 'error' in decoded:
                    log("❌ 密码错误，请检查账号密码")
                    sys.exit(1)
            except Exception:
                log(f"未知错误 (ret_code=1): {msg}")
        else:
            log(f"登录尝试 {attempt} 失败: {resp_text[:100]}")
            time.sleep(3)

    log("❌ 多次登录失败，请手动检查网络或账号")
    sys.exit(1)

if __name__ == "__main__":
    main()