# coding=UTF-8

import requests
from bs4 import BeautifulSoup
import yaml
from datetime import datetime
import csv


def generate_report(report, server_cnt, html_id):
    report[server_cnt] = {}
    for key in html_id.keys():
        report[server_cnt][key] = soup.find(id=html_id.get(key)).text
    return report


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

for ip in ip_list:
    url = config['URL_PATTERN'].format(ip=ip)
    try:
        server_cnt += 1
        print("start proccessing server: {server_cnt}".format(
            server_cnt=server_cnt))
        resp = requests.get(url, verify=False, timeout=config['TIMEOUT'])
        print(".")
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'lxml')
        print("..")
        report = generate_report(
            report=report, server_cnt=server_cnt, html_id=config['HTML_ID'])
        print("...")
    except:
        print("server ip {ip} is not reachable, after {timeout} seconds.".format(
            ip=ip, timeout=config['TIMEOUT']))
        continue

file_name = '{timestamp}_report.txt'.format(
    timestamp=timestamp)
with open(file_name, 'w', encoding='utf-8') as stream:
    stream.write(yaml.dump(report, allow_unicode=True))

input("\n===============================================================================\n"
      "Report was been generated, please check file =====> {timestamp}_report.yaml"
      "\n===============================================================================\n"
      "press Enter key to close this window...".format(timestamp=timestamp))
