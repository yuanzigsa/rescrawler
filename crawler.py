import os
import random
import modules.resolver as resolver
from modules.logger import logging


# Time : 2024/1/13
# Author : yuanzi


# 支持单IP以及多IP自动识别按小时进行轮询下载
logo = f"""开始启动AutoDownloader程序...\n
 ███████                     ██████                               ██               
░██░░░░██                   ██░░░░██                             ░██               
░██   ░██   █████   ██████ ██    ░░  ██████  ██████   ███     ██ ░██  █████  ██████
░███████   ██░░░██ ██░░░░ ░██       ░░██░░█ ░░░░░░██ ░░██  █ ░██ ░██ ██░░░██░░██░░█
░██░░░██  ░███████░░█████ ░██        ░██ ░   ███████  ░██ ███░██ ░██░███████ ░██ ░ 
░██  ░░██ ░██░░░░  ░░░░░██░░██    ██ ░██    ██░░░░██  ░████░████ ░██░██░░░░  ░██   
░██   ░░██░░██████ ██████  ░░██████ ░███   ░░████████ ███░ ░░░██ ███░░██████░███   
░░     ░░  ░░░░░░ ░░░░░░    ░░░░░░  ░░░     ░░░░░░░░ ░░░    ░░░ ░░░  ░░░░░░ ░░░    
  
【程序版本】：v1.0
【更新时间】：2024/1/4
【当前路径】：{os.getcwd()}
"""


def create_hosts(dns_info):
    hosts = []
    host1 = "127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4"
    host2 = "::1         localhost localhost.localdomain localhost6 localhost6.localdomain6"
    hosts.extend([host1, host2])
    for node in dns_info.keys():
        for domain in dns_info[node].keys():
            for ip in dns_info[node][domain].keys():
                host = f"{ip}\t{domain}"
                if host not in hosts:
                    hosts.append(host)
    # 写入本地文件
    with open("res/hosts", "w", encoding="utf-8") as file:
        for host in hosts:
            file.write(f"{host}\n")


# 随机排列hosts列表
def random_hosts():
    with open('res/hosts', 'r') as file:
        lines = file.readlines()
    header = lines[:2]
    content = lines[2:]
    random.shuffle(content)
    with open('res/hosts', 'w') as file:
        file.writelines(header + content)


# 检查用户选择
def check_user_select():
    choice = input("开始爬取Url？（y/n）: ")
    if choice == 'y':
        print("开始爬取Url...")
        return True
    elif choice == 'n':
        print("程序已退出。")
        exit()
    else:
        print("无效的选项，请重新输入。")
        return False


if __name__ == '__main__':
    # 启动程序
    logging.info(logo)
    # if check_user_select() is True:
    logging.info("开始解析Url...")
    dns_info = resolver.get_match_region_ip()

    create_hosts(dns_info)
    logging.info("已创建本地hosts文件")


    # 创建其他线程下载工具
    # 爬取资源
    # 提取域名
    # 解析域名 （外省解析）
    # 查IP归属
    # 写hosts
    # ip =$(curl - s http: // myip.ipip.net)
    # echo
    # "My public IP address is: $ip"
