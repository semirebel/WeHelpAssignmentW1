# Task 1

def func1(name):

    # 設定地圖資料：座標(x,y); 在地圖左側 z=0; 右側 z=1
    task1_map = {
        "悟空":(0,0,0),
        "辛巴":(-3,3,0),
        "貝吉塔":(-4,-1,0),
        "特南克斯":(1,-2,0),
        "丁滿":(-1,4,1),
        "弗利沙":(4,-1,1),
    }


    #若輸入的角色不在範本中
    if name not in task1_map:
        print("查無此人")
    
    else:
        #取得輸入角色的座標參數 
        x1, y1, z1 = task1_map[name]
        #距離字典
        result = {}

        # items取出資料的讀取方式固定從左至右，名稱定義也須從左至右，順序不能交換
        for other_name, other_coords in task1_map.items():
        
            # 如果是自己則跳過不計算
            if other_name == name:
                continue
            
            # 取得其他角色的座標
            x2, y2, z2 = other_coords
            
            # 套用計算公式：X差值絕對值 + Y差值絕對值 + Z差值絕對值*2
            # Python 內建計算絕對值的函式: abs()
            distance = abs(x1 - x2) + abs(y1 - y2) + abs((z1 - z2)*2)
            #回傳距離結果至距離字典
            result[other_name] = distance

        # 找出最大與最小值
        max_dist = max(result.values())
        min_dist = min(result.values())

        # 距離最遠和最近的角色清單
        farthest_characters = [k for k, v in result.items() if v == max_dist]
        closest_characters = [k for k, v in result.items() if v == min_dist]
       
        # "想使用的連接符號".join(要串接的清單) < Python寫法
        farthest_str = "、".join(farthest_characters)
        closest_str = "、".join(closest_characters)
        
        print(f"最遠{farthest_str}；最近{closest_str}")
        # f = Formatted String Literals（格式化字串字面值），簡稱為 f-string
        # 省去將資料轉換為文字的步驟
       
func1("辛巴") # print 最遠弗利沙；最近丁滿、⾙吉塔
func1("悟空") # print 最遠丁滿、弗利沙；最近特南克斯
func1("弗利沙") # print 最遠⾟巴，最近特南克斯
func1("特南克斯") # print 最遠丁滿，最近悟空


# Task 2

# 將時間切分成24小時24格，預設皆為 False:沒有被預約
time_table = {
    "S1": [False] * 24,
    "S2": [False] * 24,
    "S3": [False] * 24
}

def func2(ss, start, end, criteria):
# ss:services服務列表, start/end:客戶預約的開始/結束時間, 
# criteria：客戶篩選服務的條件字串
    global time_table

    available_services = [] #時間可預約清單

# --- 純粹巡時間，找出哪些服務時間塞得下 ---
    for service in ss: 
        name = service["name"]
        can_fit = True # 設定可預約標籤以驗證是否可預約
        
        for hour in range(start, end): # 巡客戶要求的時間格
            if time_table[name][hour] == True: # 若該服務已預約(True)
                can_fit = False # 標籤改為 False 以判讀無法預約
                break           # 終止

        if can_fit: # 如巡完所有時間格子，can_fit 依然是 True，代表可預約
            available_services.append(service) # 把這家能用的服務放進口袋名單

# --- 拆解字串 以利後續資料使用 ---
    if len(available_services) == 0:  # 如果能用的服務數量是 0
        print("Sorry")
            
    else:
        #將客戶輸入的條件使用 .split 拆解字串
        if ">=" in criteria:
            field, value = criteria.split(">=")
            op = ">="
        elif "<=" in criteria:
            field, value = criteria.split("<=")
            op = "<="
        elif "=" in criteria:
            field, value = criteria.split("=")
            op = "="
                
        if field == "r":
            value = float(value)  # 將評分轉換成浮點數
        elif field == "c":
            value = int(value)    # 將價格轉換成整數 - 整數內不能有小數點!!
        
    # --- 從時間可預約清單中 過濾符合條件的服務
        matched_services = [] # 符合條件清單
        for service in available_services:
            current_val = service[field] # 抓出該店目前的數值
            
            if op == "=" and current_val == value:
                matched_services.append(service)
            elif op == ">=" and current_val >= value:
                matched_services.append(service)
            elif op == "<=" and current_val <= value:
                matched_services.append(service)
                #.append <Python語法(相當於 JS的.push)
        
    # --- 從符合條件的清單中，比對最適合項目    
        # 如果符合時間，但沒有任何一家符合 criteria 條件
        if len(matched_services) == 0:
            print("Sorry")
        
        else: # 若有符合條件得服務開始比對最適合的
            best_service = matched_services[0] # 假設清單內第一家是最好的
            
            for service in matched_services:
                if op == ">=":
                    # 如果條件是大於等於，找最小值
                    if service[field] < best_service[field]:
                        best_service = service
                elif op == "<=":
                    # 如果條件是小於等於，找最大值
                    if service[field] > best_service[field]:
                        best_service = service
                elif op == "=":
                    # 如果是等於，不用比
                    pass
            
            
            best_name = best_service["name"]
            print(best_name)
            
            # 劃位：確定預約成功，把該店在 time_table 的該時段改成 True
            for hour in range(start, end):
                time_table[best_name][hour] = True
    
services=[ 
{"name":"S1", "r":4.5, "c":1000}, 
{"name":"S2", "r":3, "c":1200}, 
{"name":"S3", "r":3.8, "c":800} 
];

func2(services, 15, 17, "c>=800");  # S3 
func2(services, 11, 13, "r<=4");  # S3 
func2(services, 10, 12, "name=S3");  # Sorry 
func2(services, 15, 18, "r>=4.5");  # S1 
func2(services, 16, 18, "r>=4");  # Sorry 
func2(services, 13, 17, "name=S1");  # Sorry 
func2(services, 8, 9, "c<=1500");  # S2 


# Task3

def func3(index): 
    rul = [0,2,5,4]
    group = index // 4
    rem = index % 4
    ans = 25 - (2*group) - (rul[rem])
    print(f"print {ans}")

func3(1)  # print 23 
func3(5)  # print 21 
func3(10)  # print 16 
func3(30)  # print 6



# Task4

def func4(sp, stat, n): 

# 比對有開放的車廂序號，存進車廂剩餘空位的字典裡
    opencar = {}
    for i, car in enumerate(stat): 
        if car == "0":
            opencar[i] = sp[i]
    
# 比對字典中，哪個最符合需求
    if len(opencar) == 0:  # 如果能用的服務數量是 0
        print("Sorry")
        
    else:
        if n in opencar.values():
            meet = "、".join(str(k) for k, v in opencar.items() if v == n)
            print(f"print {meet}")
        
        else:
            meet = {}
            for o_car, o_seat in opencar.items():
                if n < o_seat:
                    meet[o_car] = o_seat
                elif n > o_seat:
                    meet[o_car] = o_seat
            
            max_n = max(meet.values())
            min_n = min(meet.values())

            if n < min_n:
                meet = "、".join(str(k) for k, v in opencar.items() if v == min_n)
                print(f"print {meet}")
            
            elif n > max_n:
                meet = "、".join(str(k) for k, v in opencar.items() if v == max_n)
                print(f"print {meet}")

func4([3, 1, 5, 4, 3, 2], "101000", 2)  # print 5 
func4([1, 0, 5, 1, 3], "10100", 4)  # print 4 
func4([4, 6, 5, 8], "1000", 4)  # print 2 