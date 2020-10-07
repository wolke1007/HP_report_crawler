# coding=UTF-8

import yaml
import requests
from bs4 import BeautifulSoup

class Page():

    def __init__(self, config, page_type, ip):
        self.config = config
        self.ip = ip
        self.page_type = page_type
        self.crawler_result = {}

    def get_all_element_from_html(self):
        url = self.config['URL_PATTERN'].format(ip=self.ip)
        try:
            resp = requests.get(url, verify=False, timeout=self.config['TIMEOUT'])
            resp.encoding = 'utf-8'
            soup = BeautifulSoup(resp.text, 'lxml')
            for key in self.config['PAGE'][self.page_type].keys():
                html_id = self.config['PAGE'][self.page_type].get(key)
                try:
                    self.crawler_result[key] = soup.find(id=html_id).text
                except AttributeError:
                    self.crawler_result[key] = None  # 找不到該元素時於報告中填上 null
        except requests.exceptions.ConnectTimeout:
            print("Read timed out! can't not get html content from {ip} after {timeout} seconds.\n"
                "(maybe try to increase more time to wait)\n".format(
                    ip=self.ip, timeout=self.config['TIMEOUT']))
        except requests.exceptions.ReadTimeout:
            print("ConnectTimeout! can't not get html content from {ip} after {timeout} seconds.\n"
                "(maybe try to increase more time to wait)\n".format(
                    ip=self.ip, timeout=self.config['TIMEOUT']))    
        except requests.exceptions.ConnectionError:
            print("ConnectionError! can't not get html content from {ip}.\n"
                "(this ip may not a HP printer server)\n".format(
                    ip=self.ip, timeout=self.config['TIMEOUT']))
        
    def get_crawler_result(self):
        return self.crawler_result