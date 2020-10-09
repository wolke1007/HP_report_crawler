# coding=UTF-8

import requests
from bs4 import BeautifulSoup
import yaml
from datetime import datetime
import csv
import subprocess
import os
from threading import Thread
from queue import Queue
from page import Page
import time


def load_config():
    """
    讀取 config.yaml
    """
    try:
        with open('config.yaml', 'r', encoding='utf-8') as stream:
            config = yaml.safe_load(stream)
    except FileNotFoundError:
        input("[ERROR] config.yaml not found!\n"
              "press Enter key to close this window...")
        exit(1)
    return config


def validate_config(config):
    """
    檢查 config.yaml 各主要 key 是否健全沒缺失
    """
    keys_should_be_exist = [
        'CSV_FILE_NAME',
        'USING_CSV',
        'NUM_THREADS',
        'SERVER_LIST',
        'URL_PATTERN',
        'TIMEOUT',
        'PAGE'
    ]
    for key in keys_should_be_exist:
        if key not in config.keys():
            print('[ERROR] main key missing! please check key: {key} is exist in config.yaml'.format(key = key))
            input("press Enter key to close this window...")
            exit(1)
    

def get_server_list_from_config():
    """
    從 config.yaml 檔中讀取 SERVER_LIST 的值
    """
    print("{csv_file_name} not found... "
          "ip list source : config.yaml\n".format(csv_file_name=config['CSV_FILE_NAME']))
    server_list = config['SERVER_LIST']
    if server_list == None:
        print("[ERROR] SERVER_LIST in config.yaml is empty please check!")
        input("press Enter key to close this window...")
        exit(1)
    return server_list


def get_server_list_from_csv():
    """
    從 config.yaml 中指定的 csv 檔中取資料
    資料格式為:
        192.168.2.126 TYPE_1
        192.168.2.12 TYPE_2
    這樣的形式紀錄
    """
    print("{csv_file_name} found. "
          "ip list source : {csv_file_name}\n".format(csv_file_name=config['CSV_FILE_NAME']))
    try:
        with open(config['CSV_FILE_NAME'], 'r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            server_list = []
            for row in reader:
                server_list.append(
                    {'IP': row[0].strip(),  # 資料的第 0 個資料是 IP
                     'TYPE': row[1].strip()})  # 資料的第 1 個資料是 TYPE
    except FileNotFoundError:
        print("[BUG] BUG IN get_server_list_from_csv()! should not got here.")
        input("press Enter key to close this window...")
        exit(1)
    if len(server_list) == 0:
        print("[ERROR] {csv_file_name}'s content is empty please check!".format(
            csv_file_name=config['CSV_FILE_NAME']))
        input("press Enter key to close this window...")
        exit(1)
    return server_list


def pingme(thread, queue: Queue):
    """
    ping server 主要邏輯
    """
    while True:
        server = queue.get()
        ip = server.get('IP')
        ret = subprocess.Popen(
            ["ping.exe", ip.strip(), "-n", "2"], stdout=subprocess.PIPE).communicate()[0]
        if b"unreachable" in ret:
            print('ping fail, ', server.get('IP'), ' is not reachable!')
        else:
            print(server.get('IP'), 'is alive')
            reachable_servers.append(server)
        queue.task_done()


def get_reachable_servers(server_list: list):
    """
    ping server 多執行緒部分的邏輯
    """
    print("=========== Start ping all servers ===========")
    queue = Queue()
    for thread in range(NUM_THREADS):
        new_thread = Thread(target=pingme, args=(thread, queue))
        new_thread.setDaemon(True)
        new_thread.start()
    for server in server_list:
        queue.put(server)
    queue.join()
    print("================= End of ping =================")


def crwaling(thread, queue: Queue):
    """
    爬蟲主要邏輯在 page.get_all_element_from_html() 中實現
    """
    server = queue.get()
    if (server):
        page = server['page']
        ip = server['server'].get('IP')
        print("server {ip} is proccessing... ".format(ip=ip))
        page.get_all_element_from_html()
        pages.append(page)
        queue.task_done()


def get_pages_content(reachable_servers: list, config, pages: list):
    """
    爬蟲多執行緒部分的邏輯
    """
    print("=========== Start crawling all pages ===========")
    queue = Queue()
    threads = []
    for thread in range(NUM_THREADS):
        new_thread = Thread(target=crwaling, args=(thread, queue))
        new_thread.setDaemon(True)
        new_thread.start()
        threads.append(new_thread)
    for server in reachable_servers:
        page = Page(config=config, page_type=server.get('TYPE'), 
                    ip=server.get('IP'))
        queue.put({'server': server,
                   'page': page,
                   'pages': pages})
    queue.join()
    print("================= End of crawling =================")


if __name__ == '__main__':
    config = load_config()
    validate_config(config)
    NUM_THREADS = config.get('NUM_THREADS')
    is_using_csv = config.get('USING_CSV')
    requests.packages.urllib3.disable_warnings()
    report = {}
    server_cnt = 0
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    is_ip_from_csv = True if os.path.isfile(
        config['CSV_FILE_NAME']) is True else False
    if(is_using_csv and is_ip_from_csv):
        server_list = get_server_list_from_csv()
    else:
        server_list = get_server_list_from_config()
    reachable_servers = []
    # 利用多線程同時 ping 多個 server，並將有 ping 到的加進 reachable_servers
    get_reachable_servers(server_list)
    pages = []
    # 利用多線程同時爬多個 page，並將有爬到的頁面加進 pages
    get_pages_content(reachable_servers, config, pages)
    result = {}
    # 從 page 實體中取出報告的部分
    for num, page in enumerate(pages, start=1):
        result[num] = page.get_crawler_result()
    file_name = '{timestamp}_report.txt'.format(
        timestamp=timestamp)
    with open(file_name, 'w', encoding='utf-8') as stream:
        stream.write(yaml.dump(result, allow_unicode=True))

    input("\n===============================================================================\n"
        "Report was been generated, please check file =====> {timestamp}_report.yaml"
        "\n===============================================================================\n"
        "press Enter key to close this window...".format(timestamp=timestamp))
