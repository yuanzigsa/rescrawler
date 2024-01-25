import re
import os
import json
import subprocess
import paramiko
import threading
import modules.sync as sync
from modules.logger import logging
from modules.xdbSearcher import XdbSearcher


# 提取域名
def extract_domains(file_path):
    domains = set()
    with open(file_path, 'r') as file:
        for line in file:
            match1 = re.search(r'https://(.*?\.com|.*?\.cn)', line)
            match2 = re.search(r'http://(.*?\.com|.*?\.cn)', line)
            if match1:
                domains.add(match1.group(1))
            if match2:
                domains.add(match2.group(1))
    return domains


# 获取其他地域远程主机的域名解析结果
def resolve_domain(node, ip, key_path, domains):
    try:
        # 创建 SSH 客户端
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # 连接到远程服务器
        ssh.connect(ip, username='root', key_filename=key_path)
        logging.info(f"已成功连接到 {node}-{ip} 节点，正在进行解析...\n"
                     "======================================================================================")
        resolve_result = dict()
        for domain in domains:
            # 执行域名解析命令
            command = f"dig +short {domain}"
            stdin, stdout, stderr = ssh.exec_command(command)
            # 获取命令执行结果
            result = stdout.read().decode('utf-8')
            ipv4_addresses = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', result)
            resolve_result[domain] = ipv4_addresses
        ssh.close()
        # 写入本地临时存储文件
        sync.write_to_json_file(resolve_result, f'info/{node}_resolve_result.json')

    except Exception as e:
        logging.error(f"在 {node}-{ip} 主机进行域名解析的时候出错: {e}")
        return None

def resolve_domains():
    def get_dns_ip(domain):
        try:
            # 运行 dig 命令并捕获输出
            result = subprocess.check_output(['dig', '+short', domain], universal_newlines=True)
            # 将输出按行拆分为列表
            ip_addresses = result.strip().split('\n')
            return ip_addresses
        except subprocess.CalledProcessError as e:
            print(f"Error executing dig: {e}")
            return None

    # 替换为你想要查询的域名
    domain_to_query = 'down.qq.com'

    # 调用函数并获取结果
    ip_addresses = get_dns_ip(domain_to_query)

    # 打印结果
    if ip_addresses:
        print(f"IP addresses for {domain_to_query}: {', '.join(ip_addresses)}")
    else:
        print("Failed to retrieve IP addresses.")



def get_remote_ip_resolve(nodes, key_path,  domains):
    threads = []
    # 遍历每个节点创建线程
    for node in nodes:
        thread = threading.Thread(target=resolve_domain, args=(node, nodes[node], key_path, domains))
        threads.append(thread)
        thread.start()
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    logging.info("域名解析完成，结果已保存info/dns_info.json文件中。")


# 查询IP归属地
def ip_region_search(ip_list):
    # 加载整个 xdb
    dbPath = "res/china.xdb"
    cb = XdbSearcher.loadContentFromFile(dbfile=dbPath)
    # 仅需要使用上面的全文件缓存创建查询对象, 不需要传源 xdb 文件
    searcher = XdbSearcher(contentBuff=cb)
    # 执行查询
    ipinfo = {}
    for ip in ip_list:
        result = searcher.search(ip)
        # 提取需要的信息
        province = result.split('|')[2]
        city = result.split('|')[3]
        district = result.split('|')[4]
        isp = result.split('|')[-3]
        ipinfo[ip] = {}
        ipinfo[ip]['province'] = province
        ipinfo[ip]['city'] = city
        ipinfo[ip]['district'] = district
        ipinfo[ip]['isp'] = isp
        # 构建输出格式
        logging.info(f"IP:{ip.ljust(18)}归属：{province}-{city}-{isp}")

    # 关闭searcher
    searcher.close()
    return ipinfo


# 获取匹配的IP地址
def get_match_region_ip():
    subprocess.run("rm -rf info/*", shell=True)
    resolve_node = sync.read_from_json_file("config/resolve_node.json")
    key_path = "config/id_rsa"
    download_url_path = "res/download_url.txt"
    result = subprocess.run("wget -O /opt/resCrawler/res/download_url.txt https://gitee.com/yuanzichaopu/concdownloader/releases/download/concdownloader/download_url.txt", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        logging.info("已下载最新的url库")
    else:
        logging.error(f"下载url库失败，错误信息：{result.stderr.decode()}")
        exit(1)

    # 提取下载url中的域名
    domains = extract_domains(download_url_path)
    logging.info(f"提取完成，共提取到{len(domains)}个域名，分别是：{domains}")

    # 通过在各个远程节点将域名解析为IP
    # 可以定义哪些用哪些节点以外的节点来进行解析，这样得到的结果都是想要的地区
    get_remote_ip_resolve(resolve_node, key_path, domains)

    dns_info = {}
    for node in resolve_node:
        dns_info[node] = {}
        if os.path.exists(f'info/{node}_resolve_result.json'):
            domains_resolve_ip = sync.read_from_json_file(f'info/{node}_resolve_result.json')
            if domains_resolve_ip is not None:
                for domain, ip_list in domains_resolve_ip.items():
                    dns_info[node][domain] = {}
                    ipinfo = ip_region_search(ip_list)
                    dns_info[node][domain] = ipinfo
                # 删除临时文件
                os.remove(f'info/{node}_resolve_result.json')
            else:
                logging.warning(f"{node}-{resolve_node[node]}节点解析到的IP为空，可能是建立ssh连接失败，请检查")
        else:
            pass
    # 写入本地文件
    sync.write_to_json_file(dns_info, "info/dns_info.json")
    return domains, dns_info


