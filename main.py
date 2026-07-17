from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from urllib.parse import quote  # 將網址中的中文進行編碼，避免瀏覽器亂碼
from starlette.middleware.sessions import SessionMiddleware
# --- Task 4: 旅館資料整理、比對 --- # 後端: 負責"資料驗證"
from contextlib import asynccontextmanager
import httpx  # 用來發送網路請求抓取 JSON

HOTEL_DATA = {}

# 伺服器啟動時執行一次抓取
@asynccontextmanager
async def lifespan(app: FastAPI):
    global HOTEL_DATA
    ch_url = "https://resources-wehelp-taiwan-b986132eca78c0b5eeb736fc03240c2ff8b7116.gitlab.io/hotels-ch"
    en_url = "https://resources-wehelp-taiwan-b986132eca78c0b5eeb736fc03240c2ff8b7116.gitlab.io/hotels-en"
    
    try:
        async with httpx.AsyncClient() as client:
            # 同時發出兩個請求抓取中文與英文 JSON
            ch_response = await client.get(ch_url)
            en_response = await client.get(en_url)
            
            ch_data = ch_response.json().get("list", [])  # 中文旅館陣列
            en_data = en_response.json().get("list", [])  # 英文旅館陣列
            
            # 處理中文資料: 以 id 當作 key，塞入中文資訊
            for hotel in ch_data:
                h_id = int(hotel["_id"])
                HOTEL_DATA[h_id] = {
                    "name_zh": hotel["旅宿名稱"],
                    "name_en": "No English Name",  # 先給個預設值，後面有英文再蓋掉(防禦型寫法，避免兩份資料不全)
                    "phone": hotel.get("電話或手機號碼") or "暫無提供"  # 如果是空字串或 None 就用預設字
                }
            
            # 處理英文資料
            for hotel in en_data:
                h_id = int(hotel["_id"])

                # 先把英文版可能提供的電話或傳真抓出來 (優先拿 tel，沒 tel 就拿 fax)
                en_phone = hotel.get("tel") or hotel.get("fax")
                
                # 如果這個 ID 之前在中文版就已經建立過了
                if h_id in HOTEL_DATA:
                    HOTEL_DATA[h_id]["name_en"] = hotel.get("hotel name", "No English Name")
                    
                    # 如果中文版當時沒抓到電話，但英文版有 tel 或 fax
                    if HOTEL_DATA[h_id]["phone"] == "暫無提供" and en_phone:
                        HOTEL_DATA[h_id]["phone"] = en_phone
                        
                # 如果這家旅館 只有英文版有，中文版查無資料
                else:
                    HOTEL_DATA[h_id] = {
                        "name_zh": "暫無中文名稱",
                        "name_en": hotel.get("hotel name"),
                        "phone": en_phone or "暫無提供"
                    }
    except Exception as e: # try 一定要結尾配 except(捕捉錯誤) 或 finally
        print(f"載入外部旅館資料失敗: {e}")

    yield # 暫停並放行(持續運作，不進行關閉清理工作)
# --- --- --- --- ---

app = FastAPI(lifespan=lifespan)  # FastAPI物件 # Task 4 追加 lifespann

# --- Task 3 追加 ---
# secret_key: 用來加密 Cookie 的金鑰，可自由更改為任何複雜的字串
app.add_middleware(SessionMiddleware, secret_key="kkkyrlisss")
# --- --- --- --- ---

# 設定 Jinja2 樣板資料夾路徑
templates = Jinja2Templates(directory="templates")
templates.env.cache = None  # 強制清空樣板快取(避免讀取失敗的樣板)

# Task 1: 首頁路由
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    # 使用 templates.TemplateResponse 渲染網頁
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={"request": request}
    )

# Task 2: 驗證
@app.post("/login")
def login(request: Request, email: str = Form(None), password: str = Form(None)):
    # 檢查欄位是否為空值
    if not email or not password:
        error_msg = "請輸入信箱和密碼"
        # quote: 將中文編碼成網址格式
        # status_code=303 將使用者按鈕之後送出的post請求強制改成get請求開啟指定網址
        return RedirectResponse(url=f"/ohoh?msg={quote(error_msg)}", status_code=303)
    
    # 驗證帳號與密碼是否正確
    if email == "abc@abc.com" and password == "abc":
        # --- Task 3 追加 --- session 將後端狀態的 LOGGED-IN 設定為 True
        request.session["LOGGED-IN"] = True
        return RedirectResponse(url="/member", status_code=303)
    else:
        error_msg = "信箱或密碼輸入錯誤"
        return RedirectResponse(url=f"/ohoh?msg={quote(error_msg)}", status_code=303)

# Task 2: 成功頁面
@app.get("/member", response_class=HTMLResponse)
def member_page(request: Request):

    # --- Task 3 追加 ---
    # 警衛機制：總是檢查後端的 LOGGED-IN 狀態是否為 True
    # 如果狀態不是 True , 是 False 或是 None (根本沒登入過)
    if not request.session.get("LOGGED-IN"):
        # 強制重導向回首頁 (即無法顯示登入看見的內容)
        return RedirectResponse(url="/", status_code=303)
    # --- --- --- --- ---

    return templates.TemplateResponse(
        request=request,
        name="member.html",
        context={"request": request}
    )


# Task 3: 登出
@app.get("/logout")
def logout(request: Request):
    # 將後端的 LOGGED-IN 狀態設定為 False，取消登入狀態
    request.session["LOGGED-IN"] = False
    return RedirectResponse(url="/", status_code=303) # 強制導回首頁


# Task 2: 錯誤頁面
@app.get("/ohoh", response_class=HTMLResponse)
def error_page(request: Request, msg: str = None):
    # 從網址列（Query String）接收 msg 參數，並透過 context 傳給 HTML 範本
    return templates.TemplateResponse(
        request=request,
        name="ohoh.html",
        context={"request": request, "message": msg}
    )

# Task 4: 旅館資訊
# 指定型態為 : int，FastAPI 會自動幫我們把網址的文字轉成數字
@app.get("/hotel/{hotel_id}", response_class=HTMLResponse)
def hotel_page(request: Request, hotel_id: int):
    
    # 檢查前端傳過來的 hotel_id 是否存在於全域變數 HOTEL_DATA 中
    if hotel_id in HOTEL_DATA:
        hotel_info = HOTEL_DATA[hotel_id]
        
        # 若存在，傳送 success=True 還有該旅館的詳細欄位給 hotel.html 樣板
        return templates.TemplateResponse(
            request=request,
            name="hotel.html",
            context={
                "request": request,
                "success": True,
                "name_zh": hotel_info["name_zh"],
                "name_en": hotel_info["name_en"],
                "phone": hotel_info["phone"]
            }
        )
    else:
        # 如果找不到該編號，同樣渲染 hotel.html，但傳送 success=False 讓網頁顯示「查詢不到相關資料」
        return templates.TemplateResponse(
            request=request,
            name="hotel.html",
            context={
                "request": request,
                "success": False
            }
        )