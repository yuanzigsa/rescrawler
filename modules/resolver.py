import re
import paramiko
import modules.sync as sync
from modules.logger import logging
from modules.xdbSearcher import XdbSearcher
import concurrent.futures


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
# def get_remote_ip_resolve(node, ip, key_path, domains):
#     try:
#         # 创建 SSH 客户端
#         ssh = paramiko.SSHClient()
#         ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#         # 连接到远程服务器
#         ssh.connect(ip, username='root', key_filename=key_path)
#         logging.info(f"已成功连接到 {node}-{ip} 节点，正在进行解析...\n"
#                      "=================================================================================")
#         # 执行域名解析命令
#         domains_resolve_ip = {}
#         for domain in domains:
#             command = f"nslookup {domain}"
#             stdin, stdout, stderr = ssh.exec_command(command)
#             # 跳过前两行
#             for _ in range(2):
#                 stdout.readline()
#             # 获取命令执行结果
#             result = stdout.read().decode('utf-8')
#             ipv4_addresses = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', result)
#             domains_resolve_ip[domain] = ipv4_addresses
#             error_message = stderr.read().decode('utf-8')
#             if error_message:
#                 logging.error(f"在 {node}-{ip} 主机进行域名解析的时候出错: {error_message}")
#
#         ssh.close()
#         return domains_resolve_ip
#     except Exception as e:
#         logging.error(f"连接到目标服务器 {node}-{ip} 出错: {e}")
#         return None


# 获取其他地域远程主机的域名解析结果
import paramiko
import re
import threading
import logging


def resolve_domain(node, ip, key_path, domain):
    try:
        # 创建 SSH 客户端
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # 连接到远程服务器
        ssh.connect(ip, username='root', key_filename=key_path)
        logging.info(f"已成功连接到 {node}-{ip} 节点，正在进行解析...\n"
                     "=================================================================================")

        # 执行域名解析命令
        command = f"nslookup {domain}"
        stdin, stdout, stderr = ssh.exec_command(command)

        # 跳过前两行
        for _ in range(2):
            stdout.readline()

        # 获取命令执行结果
        result = stdout.read().decode('utf-8')
        ipv4_addresses = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', result)

        ssh.close()
        return domain, ipv4_addresses

    except Exception as e:
        logging.error(f"在 {node}-{ip} 主机进行域名解析的时候出错: {e}")
        return domain, None


def get_remote_ip_resolve(nodes):
    threads = []

    # 定义要解析的域名列表
    domains = ["example.com", "google.com", "github.com"]

    # 遍历每个节点创建线程
    for node, ip, key_path in nodes:
        thread = threading.Thread(target=resolve_domain, args=(node, ip, key_path, domains))
        threads.append(thread)
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    # 定义节点信息，包括节点名称、IP地址和SSH密钥路径
    nodes = [("Node1", "192.168.1.1", "/path/to/key1.pem"),
             ("Node2", "192.168.1.2", "/path/to/key2.pem"),
             # Add more nodes as needed
             ]

    # 配置日志
    logging.basicConfig(level=logging.INFO)

    # 调用函数进行远程解析
    get_remote_ip_resolve(nodes)


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
    resolve_node = sync.read_from_json_file("config/resolve_node.json")
    key_path = "config/id_rsa"
    download_url_path = "res/download_url.txt"

    # 提取下载url中的域名
    domains = extract_domains(download_url_path)
    logging.info(f"提取完成，共提取到{len(domains)}个域名，分别是：{domains}")

    # 通过在各个远程节点将域名解析为IP
    # 可以定义哪些用哪些节点以外的节点来进行解析，这样得到的结果都是想要的地区
    dns_info = {}
    for node in resolve_node:
        resolve_node_ip = resolve_node[node]
        domains_resolve_ip = get_remote_ip_resolve(node, resolve_node_ip, key_path, domains)
        dns_info[node] = {}
        if domains_resolve_ip is not None:
            for domain, ip_list in domains_resolve_ip.items():
                dns_info[node][domain] = {}
                ipinfo = ip_region_search(ip_list)
                dns_info[node][domain] = ipinfo
        else:
            logging.warning(f"{node}-{resolve_node_ip}节点解析到的IP为空，可能是建立ssh连接失败，请检查")
    # 写入本地文件
    sync.write_to_json_file(dns_info, "info/dns_info.json")
    return domains, dns_info


