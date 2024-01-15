import os
import random
import time
import modules.qihu_crawler as qihu
import modules.resolver as resolver
from modules.logger import logging


# Time : 2024/1/13
# Author : yuanzi


logo = f"""开始启动ResCrawler程序...\n
 ███████                     ██████                               ██               
░██░░░░██                   ██░░░░██                             ░██               
░██   ░██   █████   ██████ ██    ░░  ██████  ██████   ███     ██ ░██  █████  ██████
░███████   ██░░░██ ██░░░░ ░██       ░░██░░█ ░░░░░░██ ░░██  █ ░██ ░██ ██░░░██░░██░░█
░██░░░██  ░███████░░█████ ░██        ░██ ░   ███████  ░██ ███░██ ░██░███████ ░██ ░ 
░██  ░░██ ░██░░░░  ░░░░░██░░██    ██ ░██    ██░░░░██  ░████░████ ░██░██░░░░  ░██   
░██   ░░██░░██████ ██████  ░░██████ ░███   ░░████████ ███░ ░░░██ ███░░██████░███   
░░     ░░  ░░░░░░ ░░░░░░    ░░░░░░  ░░░     ░░░░░░░░ ░░░    ░░░ ░░░  ░░░░░░ ░░░    
  
【程序版本】：v1.0
【更新时间】：2024/1/13
【当前路径】：{os.getcwd()}
"""


def create_hosts(dns_info, province, isp):
    hosts = []
    host1 = "127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4"
    host2 = "::1         localhost localhost.localdomain localhost6 localhost6.localdomain6"
    hosts.extend([host1, host2])
    for node in dns_info.keys():
        for domain in dns_info[node].keys():
            for ip in dns_info[node][domain].keys():
                if dns_info[node][domain][ip]["province"] != "宁夏省" and dns_info[node][domain][ip]["province"] != "陕西省" and dns_info[node][domain][ip]["province"] != "湖北省" and dns_info[node][domain][ip]["province"] != province and dns_info[node][domain][ip]["isp"] == isp:
                    logging.info(f"{ip:<18}{domain:<28}{dns_info[node][domain][ip]['province']}-{dns_info[node][domain][ip]['isp']}")
                    host = f"{ip}\t{domain}"
                    if host not in hosts:
                        hosts.append(host)
    if len(hosts) == 2:
        logging.error("未匹配到对应的结果，请检查！")
    else:
        # 写入本地文件
        with open("res/hosts", "w", encoding="utf-8") as file:
            for host in hosts:
                file.write(f"{host}\n")
        logging.info("已创建本地hosts文件")


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
    logging.info("开始爬取资源...")
    max_urls_to_find = 10
    page_url_path = "../info/page_urls.txt"
    download_url_path = "../info/download_url.txt"
    # qihu.start(max_urls_to_find, page_url_path,  download_url_path)
    # if check_user_select() is True:
    logging.info("开始解析Url...")
    dns_info = resolver.get_match_region_ip()
    # 只写入中国联通的dns解析，宁夏省除外
    time.sleep(1)
    province = input("请输入你想指定省份的解析结果（如：宁夏、湖北、甘肃）: ")
    isp = input("请输入你想指定运营商的解析结果（如：联通、移动、电信）: ")
    if province is not None:
        if "联通" or  "移动" or "电信" in isp:
            create_hosts(dns_info, f"{province}省", f"中国{isp}")

    # 创建其他线程下载工具
    # 爬取资源
    # 提取域名
    # 解析域名 （外省解析）
    # 查IP归属
    # 写hosts
    # ip =$(curl - s http: // myip.ipip.net)
    # echo
    # "My public IP address is: $ip"
