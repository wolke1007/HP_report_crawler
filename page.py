# coding=UTF-8

import yaml
import requests
import os
from bs4 import BeautifulSoup


class Page():

    def __init__(self, config, page_type, ip):
        self.config = config
        self.ip = ip
        self.page_type = page_type
        self.crawler_result = {}

    def get_all_element_from_html(self):
        """
        這邊為爬蟲主要邏輯實現，當中使用 soup.find(id) 的方式爬
        如果有遇到頁面的 id 為重複個且內容不為預期的時候會有問題需要另外處理之
        """
        url = self.config['URL_PATTERN'].format(ip=self.ip)
        try:
            resp = requests.get(url, verify=False,
                                timeout=self.config['TIMEOUT'])
            resp.encoding = 'utf-8'
            soup = BeautifulSoup(resp.text, 'lxml')
            for key in self.config['PAGE'][self.page_type].keys():
                html_id = self.config['PAGE'][self.page_type].get(key)
                self.crawler_result[key] = soup.find(id=html_id).text
        except AttributeError:
            self.crawler_result[key] = None  # 找不到該元素時於報告中填上 null
        except requests.exceptions.ConnectTimeout:
            print("[ERROR] Read timed out! can't not get html content from {ip} after {timeout} seconds.\n"
                  "(maybe try to increase more time to wait)\n".format(
                      ip=self.ip, timeout=self.config['TIMEOUT']))
        except requests.exceptions.ReadTimeout:
            print("[ERROR] ConnectTimeout! can't not get html content from {ip} after {timeout} seconds.\n"
                  "(maybe try to increase more time to wait)\n".format(
                      ip=self.ip, timeout=self.config['TIMEOUT']))
        except requests.exceptions.ConnectionError:
            print("[ERROR] ConnectionError! can't not get html content from {ip}.\n"
                  "(this ip may not a HP printer server)\n".format(
                      ip=self.ip, timeout=self.config['TIMEOUT']))
        except KeyError as errorMsg:
            print('[ERROR] {errorMsg}! please check config.yaml'.format(
                errorMsg=errorMsg))
            input("press Enter key to close this window...")
            os._exit(1)

    def get_crawler_result(self):
        """
        回傳此頁面爬蟲後的結果
        儲存格式為 dict，之後轉 yaml 後就會以這樣的形式呈現：
        {
            1:
                key1: value1
                key2: value2
            2:
                key1: value1
                key2: value2
        }
        """
        return self.crawler_result


if __name__ == '__main__':
    exit(0)
