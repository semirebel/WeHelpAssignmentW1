# Task 1 --------------------------------------------------------
import csv  # 匯入內建的 csv 工具箱，用來寫入 CSV 檔案
import json
import urllib.request #匯入網址函式庫的請求模組：
# Python 內建專門用來處理網路 URL 的工具箱。

# 定義網址
url_ch = "https://resources-wehelp-taiwan-b986132eca78c0b5eeb736fc03240c2ff8b7116.gitlab.io/hotels-ch"
url_en = "https://resources-wehelp-taiwan-b986132eca78c0b5eeb736fc03240c2ff8b7116.gitlab.io/hotels-en"

# 讀取中文資料
with urllib.request.urlopen(url_ch) as response:
    raw_data_ch = response.read().decode("utf-8")
    # 讀取網頁內容並將其解碼為 utf-8 字串
    data_ch = json.loads(raw_data_ch).get("list", [])
    # 使用 .get("list", []) 進入清單

# 讀取英文資料
with urllib.request.urlopen(url_en) as response:
    raw_data_en = response.read().decode("utf-8")
    data_en = json.loads(raw_data_en).get("list", [])


# 建立存放[旅館資訊]的清單
hotels_list = []

# 建立存放{行政區統計}的字典
district_stats = {}

# 使用 zip 同時遍歷中文和英文資料
for ch_hotel, en_hotel in zip(data_ch, data_en):
    # 提取並定義需要的欄位
    name_ch = ch_hotel.get("旅宿名稱", "")
    name_en = en_hotel.get("hotel name", "")
    add_ch = ch_hotel.get("地址", "")
    add_en = en_hotel.get("address", "")
    phone = ch_hotel.get("電話或手機號碼", "")
    room_count = ch_hotel.get("房間數", "")

    # 如果抓出來是空的、None、或是 0，就讓它「空著」 (空字串)
    if not room_count or str(room_count).strip() == "0":
        room_count_output = ""    # 寫入 hotels.csv 會變空白
        room_count_for_stats = 0  # 統計 districts.csv 用的數值
    else:
        try:# 讀取房間數，並轉換為整數（int）
            room_count_output = int(room_count)
            room_count_for_stats = int(room_count)
        except (ValueError, TypeError):
            room_count_output = ""
            room_count_for_stats = 0
    

    # 把這一間旅館的資訊打包成一列
    hotel_row = [name_ch, name_en, add_ch, add_en, phone, room_count_output]
    hotels_list.append(hotel_row)

    # 統計 districts.csv 的資料
    if len(add_ch) >= 6: 
    #檢查中文地址的字數有沒有大於或等於 6 個字。防止異常資料
        district = add_ch[3:6]
        # 字串切片: 從第3取至第5(不包含第6)
        # "台北市士林區" = "012345"

        if district.endswith("區"):
        # 檢查抓出來的三個字，結尾是不是「區」。防錯保險機制
            if district not in district_stats:
                district_stats[district] = [0, 0]
            # 若該行政區尚未在字典中，寫入預設值[旅館數0, 房間數0]

            district_stats[district][0] += 1
            district_stats[district][1] += room_count_for_stats
            # 迴圈每讀一間旅館 +旅館數1  +房間數(若無則+0)

# 寫入hotels.csv
with open("hotels.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(hotels_list)
# 開啟"hotels.csv", w = 寫入模式(若有舊檔案會直接覆寫)
# newline="" : 防止 Windows 系統在寫入 CSV 時，每一行中間都自動多空一行空白行。

# 寫入districts.csv
with open("districts.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    for dist, stats in district_stats.items():
        writer.writerow([dist, stats[0], stats[1]])

# 使用 with open(...) as f:
    # 進入縮排區域時：自動幫你把檔案打開。
# 離開縮排區域時(不論程式是正常跑完或突然出錯中斷)，都會自動在後台幫你執行 f.close() 關閉檔案。




# Task 2 ----------------------------------------------------------
# import csv # 第一題已導入
import time # 時間控制，避免爬蟲速度過快被PTT系統判定為惡意攻擊
import urllib.request #負責處理所有跟網路連接、發送請求（Request）、下載網頁內容
from bs4 import BeautifulSoup # 結構化、解析 HTML 語法


HEADERS = {
    "Cookie": "over18=1", # 滿18歲確認標籤，越過網頁確認視窗
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
}  # 模擬瀏覽器身分，避免連線遭拒。
BASE_URL = "https://www.ptt.cc"

# 進入文章內頁，利用 BeautifulSoup 解析並取得發表時間
def get_article_publish_time(article_url):
    """進入文章內頁，利用 BeautifulSoup 解析並取得發表時間"""
    try:
    #「錯誤嘗試機制」，確保程式就算遇到網路問題不會直接崩潰死當。

        # 使用 urllib.request 發送請求
        req = urllib.request.Request(article_url, headers=HEADERS)
        with urllib.request.urlopen(req) as response:
            # 發送請求並將回傳資料命名為 response
            html_content = response.read().decode("utf-8")
            # 將讀取網頁內容解碼為 utf-8 字串並存入 html_content

        # 使用 BeautifulSoup 解析
        soup = BeautifulSoup(html_content, "html.parser")
        meta_values = soup.find_all("span", class_="article-meta-value")
        # .find_all: 將PTT網頁中<span class="article-meta-value">內容"全部抓出"存入meta_values形成串列

        if len(meta_values) >= 4:
            # 若有第四個元素(時間字串)
            return meta_values[3].text.strip()

    # 防錯機制: 若在 try 裡的任何一行發生錯誤，會跳至此步驟        
    except Exception as e:
        print(f"解析內頁失敗(可能文章被刪或格式特殊): {e}")
    
    return "" # 若中間出錯了，或者找不到第四個時間欄位，回傳空字串


def parse_ptt_steam():
    url = f"{BASE_URL}/bbs/Steam/index.html" # 爬蟲起點
    all_articles = []
    page_count = 0 # 計數器: 用以紀錄爬到第幾頁

    print("開始爬取 PTT Steam 板...")

    # 連續爬取 3 頁
    while page_count < 3:
        print(f"\n===== 正在嘗試爬取第 {page_count + 1} 頁 =====")
        print(f"目標網址: {url}")

        try:
            # 使用內建 urllib.request 抓取列表頁
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req) as response:
                html_content = response.read().decode("utf-8")
        except Exception as e:
            print(f"無法載入頁面: {e}")
            break

        # 使用 BeautifulSoup 解析列表
        soup = BeautifulSoup(html_content, "html.parser")
        divs = soup.find_all("div", class_="r-ent")
        print(f"成功下載網頁，本頁偵測到 {len(divs)} 個文章區塊。")


        if len(divs) == 0:# 若文章數為0 代表被PTT擋下
            print("警告：這一頁沒有抓到任何文章！以下是 PTT 回傳的網頁前 500 個字，供除錯參考：")
            print("-" * 50)
            print(html_content[:500])
            print("-" * 50)
            break

        for div in divs:
            title_div = div.find("div", class_="title")
            if not title_div or not title_div.find("a"):
            # 排除已被刪除的文章(被刪除的文章標題內不會有 <a> 標籤)
                continue

            a_tag = title_div.find("a")
            title = a_tag.text.strip()
            article_link = BASE_URL + a_tag["href"]

            # 取得推文數
            nrec_div = div.find("div", class_="nrec")
            like_count = nrec_div.text.strip() if nrec_div else "0"
            if not like_count:
                like_count = "0"

            # 進入內頁取得發表時間
            print(f"正在讀取: {title}")
            publish_time = get_article_publish_time(article_link)

            # 儲存這篇文章的資訊
            all_articles.append(
                {
                    "ArticleTitle": title,
                    "LikeCount": like_count,
                    "PublishTime": publish_time,
                }
            )

            # 停頓1秒，避免對伺服器造成負擔
            time.sleep(1.0)

        # 尋找「上頁」的按鈕連結，以便往下一頁移動
        action_bar = soup.find("div", class_="action-bar")
        # 找到"導覽列"(action-bar)
        if action_bar:
            prev_btn = action_bar.find("a", string="‹ 上頁")
            # 尋找文字完全符合 "‹ 上頁" 的超連結標籤
            
            if prev_btn and prev_btn.has_attr("href"):
                url = BASE_URL + prev_btn["href"]
                page_count += 1
                print(f"成功找到下一頁網址，準備翻頁...")
                time.sleep(1.0)  # 翻頁前多睡 1 秒，保護 IP
            else:
                print("錯誤：導覽列存在，但找不到『‹ 上頁』的按鈕連結。")
                break
        else:
            print("錯誤：找不到導覽列 (action-bar)，可能網頁內容不完整。")
            break


    # 將結果寫入 csv 檔案
    with open("articles.csv", "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["ArticleTitle", "LikeCount", "PublishTime"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for article in all_articles:
            writer.writerow(article)

    print("任務結束！共爬取 {page_count} 頁，資料已儲存至 articles.csv")


if __name__ == "__main__":
    parse_ptt_steam()