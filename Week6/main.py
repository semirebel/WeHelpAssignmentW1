import mysql.connector
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

# 自動尋找並載入同資料夾底下的 .env 檔案
load_dotenv()

# 從環境變數中讀取敏感資訊（如果找不到，可以給予後備的預設值）
db_host = os.getenv("DB_HOST", "localhost")
db_user = os.getenv("DB_USER", "root")
db_password = os.getenv("DB_PASSWORD")
db_database = os.getenv("DB_DATABASE", "website")
session_secret = os.getenv("SESSION_SECRET_KEY", "default-fallback-secret-key-for-grading")

mydb = mysql.connector.connect(
  host=db_host,
  user=db_user,          
  password=db_password, 
  database=db_database,
)

print(mydb)

app = FastAPI() #初始化 FastAPI
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


# Task 2: 註冊路由
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
    
    # 執行 SQL 查詢
    mycursor = mydb.cursor(dictionary=True)

    sql = "SELECT * FROM member WHERE email = %s"
    # %s: 佔位符，告知資料庫先跳過此資訊，待會再提供
    # 此指令用於防止有心人士輸入特殊語法惡意攻擊(SQL 注入攻擊（SQL Injection）)
    mycursor.execute(sql, (email,)) # 把實際變數帶入
    # sql 搭配 mycursor，可將指令與資料分開，驅動程式會將email資料加上引號、內容的引號前加上\，
    # 確保程式判斷資料就只是資料，不會誤認成指令。
    result = mycursor.fetchone() # fetchone()第一筆符合的資料

    # 確認是否有同樣的Email
    if result: # 因為有拿到資料，所以等於 if True 成立！
        return RedirectResponse(url=f"/ohoh?msg={quote('重複的電子郵件')}", status_code=303)
        
    else:
        insert_sql = "INSERT INTO member (name, email, password) VALUES (%s, %s, %s)"
        mycursor.execute(insert_sql, (name, email, password))
        mydb.commit() # 使用 commit 之後才會真正寫入資料庫！
        
        return RedirectResponse(url="/", status_code=303)
        # 註冊成功後強制轉址回首頁，避免使用者重新整理網頁重複送出註冊導致顯示錯誤資訊，以提升使用者體驗。


# Task 3: 登入路由
@app.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...)):

    # 若欄位空白
    if not email.strip() or not password.strip():
        return RedirectResponse(url=f"/ohoh?msg={quote('電⼦郵件或密碼錯誤')}", status_code=303)

    # SQL搜尋是否有相符email帳號
    mycursor = mydb.cursor(dictionary=True)
    sql = "SELECT * FROM member WHERE email = %s"
    mycursor.execute(sql, (email,))
    result = mycursor.fetchone()

    # 若有相符帳號
    if result:

        # 確認密碼是否一致
        db_password = result["password"] 
        
        # 若密碼正確
        if password == db_password:
            request.session["user_id"] = result["id"]        
            request.session["user_name"] = result["name"]    
            request.session["user_email"] = result["email"]
            request.session["user_password"] = result["password"]
            return RedirectResponse(url="/member", status_code=303)
        
        #若密碼不正確
        else:
            return RedirectResponse(url=f"/ohoh?msg={quote('電子郵件或密碼錯誤')}", status_code=303)
        
    # 若沒有相符帳號
    else:
        return RedirectResponse(url=f"/ohoh?msg={quote('電子郵件或密碼錯誤')}", status_code=303)


# 會員頁面
@app.get("/member")
def member_page(request: Request):
    session_id = request.session.get("user_id")
    session_password = request.session.get("user_password")

    # 安全機制: 如果從Session拿不到 user_id 代表未登入，強行踢回首頁
    if not session_id:
        return RedirectResponse(url="/", status_code=303)
    
    # 在資料庫找出 user 資訊
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute("SELECT * FROM member WHERE id = %s", (session_id,))
    user = mycursor.fetchone()
    
    if not user or session_password != user["password"]:
        # 如果已無此編號使用者 或 密碼對不起來，立刻登出踢回首頁
        request.session.clear() # 清除所有session資料
        return RedirectResponse(url="/", status_code=303)

    # 若密碼一致
    user_name = user["name"]

    return templates.TemplateResponse(
        request=request, 
        name="member.html", 
        context={"username": user_name}
    )


# Task 4: 登出路由
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

    

# Task 5: 留言板

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
        mycursor = mydb.cursor()
        # 插入留言資料，對應資料庫欄位 member_id 與 content
        sql = "INSERT INTO message (member_id, content) VALUES (%s, %s)"
        mycursor.execute(sql, (session_id, content))
        mydb.commit()
        mycursor.close()
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
        mycursor = mydb.cursor(dictionary=True)
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
        mycursor.close()

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


# Task 6: 刪除留言

# 定義接收前端刪除請求的資料格式 (Pydantic Model)
class MessageDelete(BaseModel):
    id: int  # 接收要刪除的留言 ID

# 刪除留言路由
@app.delete("/api/message")
def delete_message(request: Request, msg_data: MessageDelete):
    session_id = request.session.get("user_id")
    
    # 檢查是否有登入 Session，若無則拒絕
    if not session_id:
        return {"error": True}

    message_id = msg_data.id

    try:
        mycursor = mydb.cursor()
        
        # 重要防禦機制:(防止駭客亂刪別人留言)
        # 使用者按下"X"後，確認該留言 member_id = session_id
        sql = "DELETE FROM message WHERE id = %s AND member_id = %s"
        mycursor.execute(sql, (message_id, session_id))
        mydb.commit()
        
        # 檢查資料庫到底有沒有真的刪除到資料 (rowcount 代表受影響的資料列數)
        if mycursor.rowcount == 0:
            # 若 rowcount 是 0，代表未有任何留言被刪除 = member_id & session_id 未相符
            mycursor.close() # 立即關閉資料庫連線
            return {"error": True}

        mycursor.close()
        return {"ok": True}
        
    except Exception as e:
        print(f"資料庫刪除留言錯誤: {e}")
        return {"error": True}