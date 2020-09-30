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


is_ip_from_csv = True
try:
    with open('ip.csv', 'r', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        csv_data = [ row[0] for row in reader ]
        print("ip.csv found. "
          "read ip list from ip.csv.\n\n\n")
except FileNotFoundError:
    print("ip.csv not found... "
          "read ip list from config.yaml instead.\n\n\n")
    is_ip_from_csv = False

try:
    with open('config.yaml', 'r', encoding='utf-8') as stream:
        config = yaml.safe_load(stream)
except FileNotFoundError:
    input("ERROR! config.yaml not found!\n"
          "press Enter key to close this window...")
    exit()

requests.packages.urllib3.disable_warnings()

report = {}
server_cnt = 0
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
ip_list = csv_data if is_ip_from_csv else config['IP_LIST']

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
