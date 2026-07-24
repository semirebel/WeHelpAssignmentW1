import mysql.connector
from contextlib import contextmanager  # 導入 contextmanager
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
# HTMLResponse 網頁回應工具; RedirectResponse 轉址工具
from fastapi.templating import Jinja2Templates # 網頁渲染工具
from urllib.parse import quote # 將網址中的中文進行編碼，避免瀏覽器亂碼
import re
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv # 導入環境變數載入工具
import secrets
import hashlib
from fastmcp import FastMCP, Context

# 自動尋找並載入同資料夾底下的 .env 檔案
load_dotenv()

# 從環境變數中讀取敏感資訊（如果找不到，可以給予後備的預設值）
db_host = os.getenv("DB_HOST", "localhost")
db_user = os.getenv("DB_USER", "root")
db_password = os.getenv("DB_PASSWORD")
db_database = os.getenv("DB_DATABASE", "website")
session_secret = os.getenv("SESSION_SECRET_KEY", "default-fallback-secret-key-for-grading")

# 建立安全的資料庫連線 Context Manager
@contextmanager
def get_db_cursor(dictionary=True):
    conn = mysql.connector.connect(
        host=db_host,
        user=db_user,          
        password=db_password, 
        database=db_database,
        )
    cursor = conn.cursor(dictionary=dictionary, buffered=True)

    try:
        yield conn, cursor
    finally:
        cursor.close()
        conn.close()

# 初始化 MCP Server
mcp = FastMCP("Testing Message Website")
# 建立 FastMCP 的 HTTP ASGI 應用程式
mcp_app = mcp.http_app(path="/")
# 初始化 FastAPI 時，帶入 mcp_app 的 lifespan
app = FastAPI(lifespan=mcp_app.lifespan)
templates = Jinja2Templates(directory="templates") #指定網頁範本位置

app.add_middleware(SessionMiddleware, secret_key=session_secret)
# 幫Session加密的安全金鑰(可用亂碼)，防止駭客惡意修改瀏覽器 Cookie 裡的登入資料。 跟連線資訊一樣使用環境變數。

# 首頁路由
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={"request": request}
    ) # 使用 templates.TemplateResponse 渲染網頁


# 註冊路由
@app.post("/signup")
def signup(request: Request, name: str = Form(...), email: str = Form(...), password: str = Form(...)):
# From ()內若寫 "..." 代表為必填欄位，專有名詞為"Ellipsis"
    if not name.strip() or not email.strip() or not password.strip():
        return RedirectResponse(url=f"/ohoh?msg={quote('註冊欄位不可輸入空格')}", status_code=303)
    # if not name.strip() 與 if not name 差異:
    # if not name 僅能抓到完全沒有輸入(長度為0的空字串)
    # .strip() 會將字串前後空格刪掉，攔截輸入僅輸入空格的使用者

        # 後端準則:「永遠不要相信前端傳過來的資料」
        # 儘管前端已做欄位漏填阻擋，後端仍需防禦機制以防有心人士
    
    # 限制email不可填入特殊符號
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_regex, email):
        return RedirectResponse(url=f"/ohoh?msg={quote('Email 格式不正確或包含非法符號')}", status_code=303)
    # r:Raw String（原始字串）
    # ^:起錨點
    # \:跳脫
    # {2,}:長度至少2個
    # $:終點錨點
    # re.match(pattern, string): 對照是否符合設定內容
    try:
        with get_db_cursor(dictionary=True) as (conn, mycursor):
            sql = "SELECT * FROM member WHERE email = %s"
            mycursor.execute(sql, (email,))
            result = mycursor.fetchone()
    
            # 確認是否有同樣的Email
            if result: # 因為有拿到資料，所以等於 if True 成立！
                return RedirectResponse(url=f"/ohoh?msg={quote('重複的電子郵件')}", status_code=303)
                
            else:
                insert_sql = "INSERT INTO member (name, email, password) VALUES (%s, %s, %s)"
                mycursor.execute(insert_sql, (name, email, password))
                conn.commit() # 使用 commit 之後才會真正寫入資料庫！
                
                return RedirectResponse(url="/", status_code=303)
                # 註冊成功後強制轉址回首頁，避免使用者重新整理網頁重複送出註冊導致顯示錯誤資訊，以提升使用者體驗。

    except Exception as e:
        print(f"註冊失敗: {e}")
        return RedirectResponse(url=f"/ohoh?msg={quote('系統發生錯誤')}", status_code=303)
    

# 登入路由
@app.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...)):

    # 若欄位空白
    if not email.strip() or not password.strip():
        return RedirectResponse(url=f"/ohoh?msg={quote('電⼦郵件或密碼錯誤')}", status_code=303)

    try:
    # SQL搜尋是否有相符email帳號
        with get_db_cursor(dictionary=True) as (conn, mycursor):
            sql = "SELECT * FROM member WHERE email = %s"
            mycursor.execute(sql, (email,))
            result = mycursor.fetchone()

            # 若有相符帳號且密碼一致
            if result and password == result["password"]:
                request.session["user_id"] = result["id"]        
                request.session["user_name"] = result["name"]    
                request.session["user_email"] = result["email"]
                request.session["user_password"] = result["password"]
                return RedirectResponse(url="/member", status_code=303)
        
            #若密碼不正確
            else:
                return RedirectResponse(url=f"/ohoh?msg={quote('電子郵件或密碼錯誤')}", status_code=303)
        
    except Exception as e:
        print(f"登入失敗: {e}")
        return RedirectResponse(url=f"/ohoh?msg={quote('系統發生錯誤')}", status_code=303)


# 會員頁面
@app.get("/member")
def member_page(request: Request):
    session_id = request.session.get("user_id")
    session_password = request.session.get("user_password")

    # 安全機制: 如果從Session拿不到 user_id 代表未登入，強行踢回首頁
    if not session_id:
        return RedirectResponse(url="/", status_code=303)
    
    # 在資料庫找出 user 資訊
    try:
        with get_db_cursor(dictionary=True) as (conn, mycursor):
            mycursor.execute("SELECT * FROM member WHERE id = %s", (session_id,))
            user = mycursor.fetchone()

        if not user or session_password != user["password"]:
            request.session.clear()
            return RedirectResponse(url="/", status_code=303)

        user_name = user["name"]

        return templates.TemplateResponse(
            request=request, 
            name="member.html", 
            context={"username": user_name}
        )

    except Exception as e:
        print(f"載入會員頁面失敗: {e}")
        return RedirectResponse(url="/", status_code=303)


# 登出路由
@app.get("/logout")
def logout(request: Request):
    request.session.clear() # 清除所有session資料
    return RedirectResponse(url="/", status_code=303) # 導回首頁


# 錯誤頁面
@app.get("/ohoh")
def error_page(request: Request, msg: str = "發生錯誤"):
    return templates.TemplateResponse(
        request=request, 
        name="error.html", 
        context={"message": msg}
    )


# 產生 Token 路由
@app.put("/api/token")
def create_token(request: Request):
    session_id = request.session.get("user_id")

    if not session_id:
        return{"error": True} #一樣先檢查使用者是否有登入

    try:
        # 產生隨機字串後，透過 hashlib 使用 SHA256 進行雜湊處理
        random_bytes = secrets.token_bytes(32)
        token_string = hashlib.sha256(random_bytes).hexdigest()
        # secrets: 比一般random模組更難預測、更安全
        # hashlib模組: 標準函式庫模組，提供雜湊演算法
            # 特性:單向性(無法回推)
            # 固定長度輸出: 不論輸入的字元長度，演算後輸出的長度都是固定的
            # 雪崩效應: 輸入資料儘管只有極小的改變(多一個空格)，產生的雜湊值也會大幅變動。
        # sha256演算法: 美國國家安全局（NSA）設計，屬於 SHA-2 家族成員之一
            # 全球廣泛採用的加密標準（ex.比特幣區塊鏈、SSL/TLS 憑證）
            # 輸出結果固定256位元
        # hexdigest():將演算結果轉換為64位元的16進位字串

        # 將產生的 Token 更新至當前登入會員的資料列中
        with get_db_cursor(dictionary=False) as (conn, mycursor):
            sql = "UPDATE member SET token = %s WHERE id = %s"
            mycursor.execute(sql, (token_string, session_id))
            conn.commit()
            
        # 回傳規格規定的格式
        return {"ok": True, "token": token_string}

    except Exception as e:
        print(f"產生 Token 失敗: {e}")
        return {"error": True}


# 顯示已建立 Token
@app.get("/api/token")
def get_user_token(request: Request):
    session_id = request.session.get("user_id")

    # 未登入則回傳無 token
    if not session_id:
        return {"ok": False, "token": None}

    try:
        with get_db_cursor(dictionary=True) as (conn, mycursor):
            # 從資料庫中查出目前會員的 token 欄位
            sql = "SELECT token FROM member WHERE id = %s"
            mycursor.execute(sql, (session_id,))
            result = mycursor.fetchone()

            if result and result["token"]:
                return {"ok": True, "token": result["token"]}
            else:
                return {"ok": True, "token": None}

    except Exception as e:
        print(f"取得 Token 失敗: {e}")
        return {"error": True}

    

# 留言板

# 定義接收前端 JSON 留言內容的資料格式 (Pydantic Model)
class MessageCreate(BaseModel):
    content: str

# 建立留言
@app.post("/api/message")
def create_message(request: Request, msg_data: MessageCreate):
    session_id = request.session.get("user_id")
    
    # 檢查是否有登入，若沒有或無效則回傳錯誤 JSON
    if not session_id:
        return {"error": True}
        
    content = msg_data.content.strip() # 阻擋空留言
    if not content:
        return {"error": True}

    try:
        with get_db_cursor(dictionary=False) as (conn, mycursor):
            # 插入留言資料，對應資料庫欄位 member_id 與 content
            sql = "INSERT INTO message (member_id, content) VALUES (%s, %s)"
            mycursor.execute(sql, (session_id, content))
            conn.commit()
            return {"ok": True}
    except Exception as e:
        print(f"資料庫新增留言錯誤: {e}")
        return {"error": True}
    # try ... except Exception as e:
    # tey區域: 嘗試處理區塊，若執行失敗會跳出 執行 except Exception as e 區域
    

# 取得留言
@app.get("/api/message")
def get_messages(request: Request):
    session_id = request.session.get("user_id")
    
    # 檢查是否有登入
    if not session_id:
        return {"error": True}

    try:
        with get_db_cursor(dictionary=True) as (conn, mycursor):
        # 使用 INNER JOIN 合併 member 資料表，一次取得留言者的姓名 (name)
        # 並利用 IF 判斷該留言是不是「當前登入者」寫的，若是則 self 為 true (用於 Task 6 刪除按鈕判斷)
            sql = """
                SELECT 
                    message.id AS id, 
                    member.name AS name, 
                    message.content AS content,
                    IF(message.member_id = %s, true, false) AS self

                FROM message
                INNER JOIN member ON message.member_id = member.id
                ORDER BY message.id DESC
            """
            # IF(條件, 成立時的值, 不成立時的值)
            # FROM message --以message為主體
            # INNER JOIN member --將會員表member拉進來對照
            # ON message.member_id = member.id --以兩張表的id做為橋樑
            # ORDER BY message.id DESC --根據message.id排序(ASC:正序/DESC:反序)

            mycursor.execute(sql, (session_id,))
            results = mycursor.fetchall()

            # 格式化輸出，確保 self 的值是 Boolean (True/False)
            formatted_data = []
            for row in results: # 迴圈逐一檢查每條留言的原始資料包裹(整個字典)的內容
                formatted_data.append({
                    "id": row["id"],
                    "name": row["name"],
                    "content": row["content"],
                    "self": bool(row["self"]) # bool():強行將數字轉化成布林值
                })

            return {"ok": True, "data": formatted_data}
    except Exception as e:
        print(f"資料庫讀取留言錯誤: {e}")
        return {"error": True}


# 刪除留言

# 刪除留言路由
@app.delete("/api/message/{message_id}")
def delete_message(request: Request, message_id: int): # 直接從網址中擷取 message_id
    session_id = request.session.get("user_id")
    
    # 檢查是否有登入 Session，若無則拒絕
    if not session_id:
        return {"error": True}

    try:
        with get_db_cursor(dictionary=False) as (conn, mycursor):
        
            # 重要防禦機制:(防止駭客亂刪別人留言)
            # 使用者按下"X"後，確認該留言 member_id = session_id
            sql = "DELETE FROM message WHERE id = %s AND member_id = %s"
            mycursor.execute(sql, (message_id, session_id))
            conn.commit()
        
            # 檢查資料庫到底有沒有真的刪除到資料 (rowcount 代表受影響的資料列數)
            if mycursor.rowcount == 0:
                # 若 rowcount 是 0，代表未有任何留言被刪除 = member_id & session_id 未相符
                return {"error": True}

            return {"ok": True}
        
    except Exception as e:
        print(f"資料庫刪除留言錯誤: {e}")
        return {"error": True}
    

# Task 2:  MCP Server and Tool 

@mcp.tool(
    name="create_message",
    description="Create a new message in Testing Message Website."
)
async def create_mcp_message(content: str, ctx: Context) -> dict:
# async def：宣告這是一個非同步函式
# content: str：接收 AI 或 MCP Client 傳入的參數（即使用者想發布的留言內容）
# ctx: Context：FastMCP 內建的上下文物件（Context）。
    # 當工具被呼叫時，FastMCP 會自動將當前請求的背景資訊（包含 Request、Session 等）注入到 ctx 中

    # 安全地從 Request Context 取得 HTTP Request Headers(避免程式因找不到物件而死機)
    headers = {}
    if ctx.request_context and ctx.request_context.request:
        headers = ctx.request_context.request.headers
    # 檢查 ctx.request_context 是否存在，再檢查底層的 request 物件是否存在
    # 兩者皆存在才存取 request.headers

    auth_header = headers.get("authorization") or headers.get("Authorization")
    # 在 HTTP 協定規範中 Header 的名稱是不區分大小寫的。
    # 但不同的瀏覽器、測試工具，有些會將 key 寫成全小寫 authorization，有些會寫成首字大寫 Authorization。
    # 因此先嘗試用小寫的 .get("authorization") 找資料，若找不到再使用大寫的.get("Authorization")查找。
    # 最終抓到 auth_header 字串格式預期為：Bearer <token>

    
    # 檢查是否有帶入 Authorization Header 且符合 "Bearer <token>" 格式
    if not auth_header or not auth_header.startswith("Bearer "):
        return {"error": True}

    # 提取 Bearer 後方的 Token 字串
    token = auth_header.split(" ")[1].strip()

    # 檢查傳入的留言內容是否為空白
    clean_content = content.strip()
    if not clean_content:
        return {"error": True}

    # 查詢資料庫，比對 Token 並找出對應會員 ID
    try:
        with get_db_cursor(dictionary=True) as (conn, mycursor):
            sql_find_user = "SELECT id FROM member WHERE token = %s"
            mycursor.execute(sql_find_user, (token,))
            user = mycursor.fetchone()

            # 若 Token 找不到對應的會員，回傳錯誤
            if not user:
                return {"error": True}

            member_id = user["id"]

            # 寫入留言資料表
            sql_insert_msg = "INSERT INTO message (member_id, content) VALUES (%s, %s)"
            mycursor.execute(sql_insert_msg, (member_id, clean_content))
            conn.commit()
            
            # 成功建立留言
            return {"ok": True}

    except Exception as e:
        print(f"MCP 新增留言發生錯誤: {e}")
        return {"error": True}


# 指定 mcp 端點
app.mount("/mcp", mcp_app)
# mount()（掛載）:
# 把一個獨立的 Web 應用程式（Sub-application），「嵌套/掛載」到主應用程式的特定路徑底下。