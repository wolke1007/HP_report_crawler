# coding=UTF-8

import requests
from bs4 import BeautifulSoup
import yaml
from datetime import datetime
import csv
import subprocess
from threading import Thread
from queue import Queue

NUM_THREADS = 10


def get_ip_list(is_ip_from_csv):
    ip_list = csv_data if is_ip_from_csv else config['IP_LIST']
    if ip_list == None and not is_ip_from_csv:
        print("ERROR! IP_LIST in config.yaml is empty... please check")
        input("press Enter key to close this window...")
        exit()
    elif len(ip_list) == 0 and is_ip_from_csv:
        print("ERROR! {csv_file_name}'s content is empty... please check".format(
            csv_file_name=config['CSV_FILE_NAME']))
        input("press Enter key to close this window...")
        exit()
    return ip_list

def pingme(i, queue):
    while True:
        ip = queue.get()
        ret = subprocess.Popen(
            "ping -n 1 " + ip, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if b"Destination host unreachable." in ret.stdout.read():
            print('ping fail, ', ip, ' is not reachable!')
        else:
            print(ip, 'is alive')
            reachable_servers.append(ip)
        queue.task_done()

def get_reachable_servers(server_list):
    print("=========== Start ping all servers ===========")
    reachable_server_list = []
    queue = Queue()
    for thread in range(NUM_THREADS):
        new_thread = Thread(target=pingme, args=(thread, queue))
        new_thread.setDaemon(True)
        new_thread.start()
    for ip in server_list:
        queue.put(ip)
    queue.join()
    print("================= End of ping =================")

def generate_report(report, server_cnt, html_id):
    report[server_cnt] = {}
    for key in html_id.keys():
        report[server_cnt][key] = soup.find(id=html_id.get(key)).text
    return report


# 讀取 config 檔
try:
    with open('config.yaml', 'r', encoding='utf-8') as stream:
        config = yaml.safe_load(stream)
except FileNotFoundError:
    input("ERROR! config.yaml not found!\n"
          "press Enter key to close this window...")
    exit()

is_ip_from_csv = True
try:
    with open(config['CSV_FILE_NAME'], 'r', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        csv_data = [row[0].strip() for row in reader]
        print("{csv_file_name} found. "
              "read ip list from {csv_file_name}.\n".format(csv_file_name=config['CSV_FILE_NAME']))
except FileNotFoundError:
    print("{csv_file_name} not found... "
          "read ip list from config.yaml instead.\n".format(csv_file_name=config['CSV_FILE_NAME']))
    is_ip_from_csv = False

requests.packages.urllib3.disable_warnings()

report = {}
server_cnt = 0
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
ip_list = get_ip_list(is_ip_from_csv)
reachable_servers = []
# 利用多線程同時 ping 多個 server，並將有 ping 到的加進 reachable_servers
get_reachable_servers(ip_list)

for ip in reachable_servers:
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
        report=report, server_cnt=server_cnt, html_id=config['HTML_ID'])
    print("...")


file_name = '{timestamp}_report.txt'.format(
    timestamp=timestamp)
with open(file_name, 'w', encoding='utf-8') as stream:
    stream.write(yaml.dump(report, allow_unicode=True))

input("\n===============================================================================\n"
      "Report was been generated, please check file =====> {timestamp}_report.yaml"
      "\n===============================================================================\n"
      "press Enter key to close this window...".format(timestamp=timestamp))
