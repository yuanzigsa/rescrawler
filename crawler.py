import re
import os
import random
import subprocess
import modules.qihu_crawler as qihu
import modules.sync as sync
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
【更新时间】：2024/1/24
【当前路径】：{os.getcwd()}
"""


def create_hosts(domains, dns_info, isp):
    our_node = sync.read_from_json_file("config/our_node.json")
    hosts = []
    host1 = "127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4"
    host2 = "::1         localhost localhost.localdomain localhost6 localhost6.localdomain6"
    hosts.extend([host1, host2])
    for node in dns_info.keys():
        for domain in dns_info[node].keys():
            for ip in dns_info[node][domain].keys():
                if dns_info[node][domain][ip]["isp"] == isp and dns_info[node][domain][ip]["province"] not in our_node[isp]:
                    logging.info(f"{ip:<18}{domain:<28}{dns_info[node][domain][ip]['province']}-{dns_info[node][domain][ip]['isp']}")
                    host = f"{ip}\t{domain}"
                    if host not in hosts:
                        hosts.append(host)
    if len(hosts) == 2:
        logging.error("未匹配到对应的结果，请检查！")
    else:
        file_path = "res/download_url.txt"
        temp_lines = []
        host_domains = []

        # 写入本地hosts文件
        with open("res/hosts", "w", encoding="utf-8") as file:
            for host in hosts:
                file.write(f"{host}\n")

        # 获取没有解析结果的域名
        for domain in domains:
            for host in hosts:
                if domain in host:
                    host_domains.append(domain)

        # 剔除没有获取到域名解析结果的下载url
        host_domains = set(host_domains)
        with open(file_path, "r", encoding="utf-8") as f:
            download_url = f.readlines()
            url_counts = 0
            for url in download_url:
                for domain in host_domains:
                    if domain in url:
                        temp_lines.append(url)
                url_counts += 1
            # 统计
            difference = set(download_url).difference(set(temp_lines))
            urls = set()
            for domain in difference:
                match1 = re.search(r'https://(.*?\.com|.*?\.cn)', domain)
                match2 = re.search(r'http://(.*?\.com|.*?\.cn)', domain)
                if match1 or match2:
                    urls.add(match1.group(1)) if match1 else urls.add(match2.group(1))
            for domain in urls:
                logging.warning(f"{domain} 未获取到指定解析结果，已将其从下载url中删除")
            logging.info(f"共创建：{len(hosts) - 2}条host")
            logging.info(f"原始下载url数量：{url_counts}条")
            logging.info(f"剔除没有获取到符合条件的域名解析结果的下载url后，剩余：{len(set(temp_lines))}条")
        # 写入下载url
        with open(file_path, "w", encoding="utf-8") as download_url:
            temp_lines = list(set(temp_lines))
            download_url.writelines(temp_lines)
        logging.info("已创建本地hosts文件，请将res/hosts文件同步更新到目标服务器/etc/目录下")
        logging.info("已创建本地download_url.txt文件，请将res/download_url.txt文件同步更新到目标服务器/opt/concdownloader/res/目录下 ")


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
    max_urls_to_find = 50
    page_url_path = "info/page_urls.txt"
    download_url_path = "info/download_url.txt"
    # qihu.start(max_urls_to_find, page_url_path,  download_url_path)
    # with open(page_url_path, 'r', encoding='utf-8') as file:
    #     for line in file:
    #         url = line.strip()
            # qihu.get_download_url(download_url_path,url)
    # if check_user_select() is True:
    logging.info("爬取未定义，直接开始解析！")
    isp = input("请输入你想指定运营商的解析结果（如：联通、移动、电信）: ")
    if "联通" or "移动" or "电信" in isp:
        isp = f"中国{isp}"
    else:
        logging.info("输入无效，程序退出！")
    logging.info("开始解析Url...")
    domains, dns_info = resolver.get_match_region_ip(isp)
    # 创建指定运营商的解析host
    create_hosts(domains, dns_info, isp)
    # 上传至服务器
    subprocess.run("scp /opt/resCrawler/res/hosts root@118.182.250.31:/root/", shell=True)
    subprocess.run("scp /opt/resCrawler/res/download_url.txt root@118.182.250.31:/root/", shell=True)
    # 创建其他线程下载工具
    # 爬取资源
    # 提取域名
    # 解析域名 （外省解析）
    # 查IP归属
    # 写hosts
