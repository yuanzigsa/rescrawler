import os
import json
import random
import requests
import threading
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from modules.logger import logging

# 定义一个锁，用于同步访问计数器
lock = threading.Lock()
found_urls_count = 0

# 下载页面的检查规则
def check_page(response):
    if response.status_code == 200:
        if "The requested URL was not found on this serve" not in response.text:
            if "抱歉，页面失踪了" not in response.text:
                return True

# 检查URL是否有效
def check_url(max_urls_to_find, page_url_path, number, stop_event):
    global found_urls_count
    url = f"https://baoku.360.cn/soft/show/appid/{number}"
    try:
        if stop_event.is_set():
            return
        response = requests.get(url, timeout=5)
        if check_page(response):
            with lock:
                if found_urls_count >= max_urls_to_find:
                    stop_event.set()
                    return
                found_urls_count += 1
                logging.info(f"找到有效URL: {url} (总计: {found_urls_count})")
                with open(page_url_path, "a") as file:
                    file.write(url + "\n")
                if found_urls_count >= max_urls_to_find:
                    stop_event.set()
                    return
    except requests.exceptions.RequestException as e:
        logging.error(f"错误: {url}, error: {e}")


# 多线程检查url
def  check_urls_concurrently(max_urls_to_find, page_url_path):
    number_values = random.sample(range(1, 1001), 1000)
    stop_event = threading.Event()
    with ThreadPoolExecutor(max_workers=64) as executor:
        futures = []
        for number in number_values:
            if stop_event.is_set():
                break
            future = executor.submit(check_url,max_urls_to_find, page_url_path, number, stop_event)
            futures.append(future)

        # 等待所有线程完成，或者直到stop_event被设置
        for future in futures:
            if stop_event.is_set():
                future.cancel()
            else:
                future.result()
                
# 获取页面面的下载URL
def get_download_url(download_url_path, url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            a_tags = soup.find_all('a', class_='normal-down-btn')
            if not a_tags:
                raise ValueError("没有找到下载URL。")
            for a in a_tags:
                download_url = a.get('href')
                if download_url:
                    with open(download_url_path, 'a', encoding='utf-8') as f:
                        f.write(download_url + '\n')
                    logging.info('找到下载URL:', download_url)
        else:
            logging.info('请求页面失败，状态码:', response.status_code)
    except requests.RequestException as e:
        logging.error(f'请求URL时出现错误: {e}')
    except ValueError as ve:
        logging.error(f'处理URL时出现错误: {ve}')
    except Exception as ex:
        logging.error(f'处理URL "{url}" 时出现未知错误: {ex}')

def start(max_urls_to_find, page_url_path, download_url_path):
    # 清空之前的数据
    if os.path.exists(page_url_path):
        os.remove(page_url_path)
    if os.path.exists(download_url_path):
        os.remove(download_url_path)
    # 筛选出下载页面
    check_urls_concurrently(max_urls_to_find, page_url_path)
    # 提取下载url
    with open(page_url_path, 'r', encoding='utf-8') as file:
        for line in file:
            url = line.strip()
            get_download_url(url)
