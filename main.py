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
from page_factory import PageFactory

NUM_THREADS = 10


def load_config():
    try:
        with open('config.yaml', 'r', encoding='utf-8') as stream:
            config = yaml.safe_load(stream)
    except FileNotFoundError:
        input("ERROR! config.yaml not found!\n"
              "press Enter key to close this window...")
        exit()
    return config


def get_server_list_from_config():
    # 從 config.yaml 檔中讀取 SERVER_LIST 的值
    print("{csv_file_name} not found... "
          "ip list source : config.yaml\n".format(csv_file_name=config['CSV_FILE_NAME']))
    server_list = config['SERVER_LIST']
    if server_list == None:
        print("ERROR! IP_LIST in config.yaml is empty... please check")
        input("press Enter key to close this window...")
        exit()
    return server_list


def get_server_list_from_csv():
    # 從 config.yaml 中指定的 csv 檔中取資料
    print("{csv_file_name} found. "
          "ip list source : {csv_file_name}\n".format(csv_file_name=config['CSV_FILE_NAME']))
    try:
        with open(config['CSV_FILE_NAME'], 'r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            server_list = []
            for row in reader:
                server_list.append(
                    {'IP': row[0].strip(),
                     'TYPE': row[1].strip()})
    except FileNotFoundError:
        print("BUG HERE! should not got here.")
    if len(server_list) == 0:
        print("ERROR! {csv_file_name}'s content is empty... please check".format(
            csv_file_name=config['CSV_FILE_NAME']))
        input("press Enter key to close this window...")
        exit()
    return server_list


def pingme(i, queue: Queue):
    # ping server 主要邏輯
    while True:
        server = queue.get()
        ret = subprocess.Popen(
            "ping -n 1 " + server.get('IP'), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if b"Destination host unreachable." in ret.stdout.read():
            print('ping fail, ', server.get('IP'), ' is not reachable!')
        else:
            print(server.get('IP'), 'is alive')
            reachable_servers.append(server)
        queue.task_done()


def get_reachable_servers(server_list: dict):
    # ping server 多執行緒部分的邏輯
    print("=========== Start ping all servers ===========")
    reachable_server_list = []
    queue = Queue()
    for thread in range(NUM_THREADS):
        new_thread = Thread(target=pingme, args=(thread, queue))
        new_thread.setDaemon(True)
        new_thread.start()
    for server in server_list:
        queue.put(server)
    queue.join()
    print("================= End of ping =================")


requests.packages.urllib3.disable_warnings()
config = load_config()
report = {}
server_cnt = 0
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
is_ip_from_csv = True if os.path.isfile(
    config['CSV_FILE_NAME']) is True else False
if(is_ip_from_csv):
    server_list = get_server_list_from_csv()
else:
    server_list = get_server_list_from_config()
reachable_servers = []
# 利用多線程同時 ping 多個 server，並將有 ping 到的加進 reachable_servers
get_reachable_servers(server_list)
page_refactory = PageFactory(config)
pages = []
for server in reachable_servers:
    ip = server.get('IP')
    page_type = server.get('TYPE')
    server_cnt += 1
    print("server {server_cnt} is proccessing: ".format(server_cnt=server_cnt))
    pages.append((server_cnt, page_refactory.get_page_instance(page_type, ip)))
result = {}
for page in pages:
    result[page[0]] = page[1].get_crawler_result()
file_name = '{timestamp}_report.txt'.format(
    timestamp=timestamp)
with open(file_name, 'w', encoding='utf-8') as stream:
    stream.write(yaml.dump(result, allow_unicode=True))

input("\n===============================================================================\n"
      "Report was been generated, please check file =====> {timestamp}_report.yaml"
      "\n===============================================================================\n"
      "press Enter key to close this window...".format(timestamp=timestamp))
