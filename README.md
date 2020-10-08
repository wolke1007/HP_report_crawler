# 使用說明

## 限制

1. 理論上防毒會擋，要給權限
2. config.yaml 與 ip.csv 這兩個檔案必須與執行檔(exe)位於同一層
3. config.yaml 這個檔案必須存在
4. ip.csv 的存在則可有可無(沒有的話會從 config.yaml 中撈 IP_LIST)

## config.yaml

* URL_PATTERN  
  * 除了 ip 以外的 url
  * 目前寫死只有一個頁面，未來視需求支援多個頁面
* IP_LIST  
  * ip 列表
  * 若 ip.csv 不存在則會讀這邊，算是提供另一種輸入方式的選擇
* TIMEOUT  
  * 設定 url request 的逾時時間，以秒為單位
* HTML_ID  
  * 需要資訊的對應 HTML id 與報告中呈現的中文
  * 可視需求添增 key value(但目前只能用在目前寫死的那頁中)

## 備註
  * 使用 pyinstaller 產出 exe 檔
  * 使用套件:
    * bs4
    * requests
    * yaml
    * csv