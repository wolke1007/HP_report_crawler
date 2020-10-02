# coding=UTF-8

import requests
from bs4 import BeautifulSoup
import yaml
from datetime import datetime
import csv
import subprocess
from threading import Thread
from queue import Queue
from page1 import Page1
from default_page import DefaultPage
from page_factory import PageFactory

NUM_THREADS = 10


def load_config():
    # 讀取 config 檔
    try:
        with open('config.yaml', 'r', encoding='utf-8') as stream:
            config = yaml.safe_load(stream)
    except FileNotFoundError:
        input("ERROR! config.yaml not found!\n"
              "press Enter key to close this window...")
        exit()
    return config


def get_server_list_from_config():
    server_list = config['SERVER_LIST']
    if server_list == None:
        print("ERROR! IP_LIST in config.yaml is empty... please check")
        input("press Enter key to close this window...")
        exit()
    return server_list


def get_server_list_from_csv():
    try:
        with open(config['CSV_FILE_NAME'], 'r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            server_list = []
            for row in reader:
                server_list.append(
                    {'IP': row[0].strip(),
                     'TYPE': row[1].strip()})
            print("{csv_file_name} found. "
                  "read ip list from {csv_file_name}.\n".format(csv_file_name=config['CSV_FILE_NAME']))
    except FileNotFoundError:
        print("{csv_file_name} not found... "
              "read ip list from config.yaml instead.\n".format(csv_file_name=config['CSV_FILE_NAME']))
    if len(server_list.get('SERVER_LIST')) == 0:
        print("ERROR! {csv_file_name}'s content is empty... please check".format(
            csv_file_name=config['CSV_FILE_NAME']))
        input("press Enter key to close this window...")
        exit()
    return server_list


def pingme(i, queue: Queue):
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


def generate_report(report: dict, server_cnt: int, html_id: dict):
    report[server_cnt] = {}
    for key in html_id.keys():
        try:
            report[server_cnt][key] = soup.find(id=html_id.get(key)).text
        except AttributeError:
            report[server_cnt][key] = None  # 找不到該元素時於報告中填上 null
    return report


requests.packages.urllib3.disable_warnings()
config = load_config()
report = {}
server_cnt = 0
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
is_ip_from_csv = True if os.path.isfile(
    config['CSV_FILE_NAME']) is True else False
if(is_ip_from_csv):
    print("{csv_file_name} found... "
          "ip list source : {csv_file_name}\n".format(csv_file_name=config['CSV_FILE_NAME']))
    server_list = get_server_list_from_csv()
else:
    print("{csv_file_name} not found... "
          "ip list source : config.yaml\n".format(csv_file_name=config['CSV_FILE_NAME']))
    server_list = get_server_list_from_config()
reachable_servers = []
# 利用多線程同時 ping 多個 server，並將有 ping 到的加進 reachable_servers
get_reachable_servers(server_list)
page_refactory = PageFactory()

for server in reachable_servers:
    ip = server.get('IP')
    page_type = server.get('TYPE')
    url = config['URL_PATTERN'].format(ip=ip)
    server_cnt += 1
    print("start proccessing server {server_cnt}:".format(
        server_cnt=server_cnt))
    try:
        resp = requests.get(url, verify=False, timeout=config['TIMEOUT'])
    except requests.exceptions.ConnectTimeout:
        print("ConnectTimeout! can't not get html content from {ip} after {timeout} seconds.\n"
              "(maybe try to increase more time to wait)\n".format(
                  ip=ip, timeout=config['TIMEOUT']))
        continue
    except requests.exceptions.ConnectionError:
        print("ConnectionError! can't not get html content from {ip}.\n"
              "(this ip may not a HP printer server)\n".format(
                  ip=ip, timeout=config['TIMEOUT']))
        continue

    print(".")
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.text, 'lxml')
    print("..")
    report = generate_report(
        report=report, server_cnt=server_cnt, html_id=config.get('PAGE').get(page_type))
    print("...")


file_name = '{timestamp}_report.txt'.format(
    timestamp=timestamp)
with open(file_name, 'w', encoding='utf-8') as stream:
    stream.write(yaml.dump(report, allow_unicode=True))

input("\n===============================================================================\n"
      "Report was been generated, please check file =====> {timestamp}_report.yaml"
      "\n===============================================================================\n"
      "press Enter key to close this window...".format(timestamp=timestamp))
