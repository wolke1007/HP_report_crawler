# 使用說明

## 限制

1. 理論上防毒會擋，要給權限
2. config.yaml 與 ip.csv 這兩個檔案必須與執行檔(exe)位於同一層
3. config.yaml 這個檔案必須存在
4. ip.csv 的存在則可有可無(沒有的話會從 config.yaml 中撈 IP_LIST)
5. 因為爬蟲使用多執行緒執行，故報告中的順序與表格中主機的順序不會一致

## config.yaml

* CSV_FILE_NAME
  * ip 列表的 csv 檔案名稱，預設為 ip.csv
* USING_CSV
  * 是否要用 csv 裡面的 IP 來跑這個程式(不然就要用 config 中的 SERVER_LIST)
* NUM_THREADS
  * 決定多執行緒的數量，數量越多可以一次對越多機器操作
  * 預設為 5
  * 其實我不知道這個設多少會是效能甜蜜點，但有試過 10 是可以正常運作的  
    但保守點設個 5 先，設太高出錯的話可以嘗試設少一點點XD
* URL_PATTERN
  * 除了 ip 以外的 url
  * 目前寫死只有一個頁面，未來視需求支援多個頁面
* TIMEOUT
  * 此為爬蟲時等待頁面回應的時間，為避免機器回應速度太慢但其實還沒死掉所以不能設太短
  * 以秒為單位
  * 預設為 10 秒(曾有遇過 5 秒還沒回應的 囧)
* SERVER_LIST  
  * ip 列表
  * 若 ip.csv 不存在則會讀這邊，算是提供另一種輸入方式的選擇
* PAGE
  * TYPE
    * 此為怕不同機種有不同的頁面而做的設計
    * 可視需求添增報告中呈現的中文與對應的 HTML id(例: "舉個栗子": "Chestnut.SampleDiv.SampleId")  

## 備註
  * 使用 pyinstaller 產出 exe 檔
  * 使用套件:
    * bs4
    * requests
    * yaml
    * csv
