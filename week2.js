// Task1

function func1(name){ 

    // 建立角色座標資料庫，線段左邊區域 = z0，右邊區域 = z1
    const characters = { 
        "悟空":[0,0,0],
        "辛巴":[-3,3,0],
        "貝吉塔":[-4,-1,0],
        "特南克斯":[1,-2,0],
        "丁滿":[-1,4,1],
        "弗利沙":[4,-1,1],
    }
    /*  JS語法中:
    [] = 建立陣列(Array)清單，用來打包多項資料；
    () = 呼叫函數 或 數學運算。 */

    // 檢查角色是否存在
    if (!characters[name]) {
        console.log("查無此人");
        return;
    }

    const [x1, y1, z1] = characters[name];
    

    // 建立筆記本
    let maxDistance = -1;       // 最遠距離預設為負數，供認和角色可超越
    let minDistance = Infinity; // 最近距離預設為無限，供任何角色可超越
    let closestCharacters = []; // 最近的人的陣列清單
    let farthestCharacters = [];// 最遠的人的陣列清單


    for (const [otherName, [x2, y2, z2]] of Object.entries(characters)) {
        if (otherName === name) continue; // 跳過自己

        // 絕對值公式計算距離
        const distance = Math.abs(x1 - x2) + Math.abs(y1 - y2) + Math.abs((z1 - z2) * 2);

        // 印出測試距離
        //console.log(`【距離測試】從 [${name}] 到 [${otherName}] 的距離是：${distance}`);

        // 判斷是否距離最遠
        if (distance > maxDistance) {
            maxDistance = distance; // 若刷新最高紀錄，覆寫最遠距離
            farthestCharacters = [otherName]; // 覆寫新紀錄保持者
        } else if (distance === maxDistance) {
            farthestCharacters.push(otherName); // 與紀錄平手，"推"進最遠名單中
        }

        // 判斷是否距離最近
        if (distance < minDistance) {
            minDistance = distance;         
            closestCharacters = [otherName]; 
        } else if (distance === minDistance) {
            closestCharacters.push(otherName); 
        }
    }

    console.log(`最遠${farthestCharacters.join('、')}；最近${closestCharacters.join('、')}`);
    // 陣列 . join(連接符號) < JS寫法   
} 

func1("辛巴");  // print 最遠弗利沙；最近丁滿、⾙吉塔
func1("悟空");  // print 最遠丁滿、弗利沙；最近特南克斯
func1("弗利沙");  // print 最遠⾟巴，最近特南克斯 
func1("特南克斯");  // print 最遠丁滿，最近悟空



// Task2
// 將時間切分成24小時24格，預設皆為 false:沒有被預約
const time_table = {
    "S1": Array(24).fill(false),
    "S2": Array(24).fill(false),
    "S3": Array(24).fill(false)
}; // .fill : 把指定的物件（數字、字串、布林值等），填入到陣列的每一個格子裡。

function func2(ss, start, end, criteria) {
    let available_services = []; // 時間可預約清單

    // --- 純粹巡時間，找出哪些服務時間塞得下 ---
    for (let service of ss) {
        let name = service.name;
        let can_fit = true; // 設定可預約標籤

        for (let hour = start; hour < end; hour++) { // 巡客戶要求的時間格
            if (time_table[name][hour] === true) { // 若該服務已預約
                can_fit = false; // 標籤改為 false
                break;           // 終止
            }
        }

        if (can_fit) {
            available_services.push(service); // .push 同 Python的 .append
        }
    }

    // --- 拆解字串 以利後續資料使用 ---
    if (available_services.length === 0) { // .length 同 Python 的 len() 
        console.log("Sorry");
        return;
    }

    let field, value, op;
    // 將客戶輸入的條件使用 .split 拆解字串
    if (criteria.includes(">=")) {
        [field, value] = criteria.split(">=");
        op = ">=";
    } else if (criteria.includes("<=")) {
        [field, value] = criteria.split("<=");
        op = "<=";
    } else if (criteria.includes("=")) {
        [field, value] = criteria.split("=");
        op = "=";
    }

    if (field === "r") {
        value = parseFloat(value); // 將評分轉換成浮點數
    } else if (field === "c") {
        value = parseInt(value, 10); // 將價格轉換成整數
    }

    // --- 從時間可預約清單中 過濾符合條件的服務 ---
    let matched_services = [];
    for (let service of available_services) {
        let current_val = service[field]; // 抓出該店目前的數值

        if (op === "=" && current_val === value) {
            matched_services.push(service);
        } else if (op === ">=" && current_val >= value) {
            matched_services.push(service);
        } else if (op === "<=" && current_val <= value) {
            matched_services.push(service);
        }
    }

    // --- 從符合條件的清單中，比對最適合項目 ---
    if (matched_services.length === 0) {
        console.log("Sorry");
    } else {
        let best_service = matched_services[0]; // 假設清單內第一家是最好的

        for (let service of matched_services) {
            if (op === ">=") {
                // 如果條件是大於等於，找最小值
                if (service[field] < best_service[field]) {
                    best_service = service;
                }
            } else if (op === "<=") {
                // 如果條件是小於等於，找最大值
                if (service[field] > best_service[field]) {
                    best_service = service;
                }
            }
            // 如果是等於，不用比
        }

        let best_name = best_service.name;
        console.log(best_name);

        // 劃位：確定預約成功，把該店在 time_table 的該時段改成 true
        for (let hour = start; hour < end; hour++) {
            time_table[best_name][hour] = true;
        }
    }
}

const services=[ 
{"name":"S1", "r":4.5, "c":1000}, 
{"name":"S2", "r":3, "c":1200}, 
{"name":"S3", "r":3.8, "c":800} 
]; 
func2(services, 15, 17, "c>=800");  // S3 
func2(services, 11, 13, "r<=4");  // S3 
func2(services, 10, 12, "name=S3");  // Sorry 
func2(services, 15, 18, "r>=4.5");  // S1 
func2(services, 16, 18, "r>=4");  // Sorry 
func2(services, 13, 17, "name=S1");  // Sorry 
func2(services, 8, 9, "c<=1500");  // S2



// Task3
function func3(index){ 
    let rul = [0,2,5,4];
    let group = Math.floor(index/4);
    let rem = index % 4;
    let ans = 25 - (2*group) - (rul[rem]);
    console.log("print",ans)
} 
func3(1);  // print 23 
func3(5);  // print 21 
func3(10);  // print 16 
func3(30);  // print 6



// Task4
function func4(sp, stat, n){ 

    // 比對有開放的車廂序號，存進車廂剩餘空位的字典裡
    let opencar = {}
    for(let i=0;i<stat.length;i++){
    /* for(起始值;條件式;步進值)
    i 為變數，預設0; 條件設為stat的長度 ; 每執行完一次迴圈 i+1
    即為在stat字串中，從第一項(編號0)開始確認直到第n項(編號n-1)結束 */
        if(stat[i] === "0"){
            opencar[i] = sp[i]
        }
    }

    // 比對字典中，哪個最符合需求
    if(Object.keys(opencar).length === 0){
        /* JS 中，只有「陣列」或「字串」有 .length 屬性。
        透過.key 將物件中的值抓出來變成「陣列」*/
        console.log("Sorry")
    }

    else{
        if(Object.values(opencar).includes(n)) {
        // .includes：opencar 的所有值裡面，有包含 n 

            // 找出所有「值 (v) 等於 n」的「鍵 (k)」
            let meet = Object.keys(opencar).filter(k => opencar[k] === n);
            /* Object.keys(opencar) 拿到所有車廂，
            .filter() 會過濾出座位剛好等於 n 的車廂 */
            
            console.log(`print ${meet.join('、')}`);
            /* 使用反單引號"`" 可直接寫純文字(後方會自動加一空格) 亦可寫進變數
            .join 可將陣列中的元素乾淨串接並自行指定串接符號 */
        }

        else if(Object.values(opencar).some(v => v > n)){
        // .some: 裡面有沒有「某些」值滿足(條件)呢？
            
            let f_car = Object.keys(opencar).filter(k => opencar[k] > n);
            // 過濾所有opencar中 key值 > n 的項目 存入 f_car
            let f_seat = f_car.map(k => opencar[k]);
            // .map:不會破壞原陣列，僅查找並製作對應的新陣列
            let min_n = Math.min(...f_seat);
            let meet = f_car.filter(k => opencar[k] === min_n);
            console.log(`print ${meet.join('、')}`);
        }
            
        
        else if(Object.values(opencar).some(v => v < n)){
            
            let f_car = Object.keys(opencar).filter(k => opencar[k] < n);
            // 過濾所有opencar中 key值 > n 的項目 存入 f_car
            let f_seat = f_car.map(k => opencar[k]);
            // .map:不會破壞原陣列，僅查找並製作對應的新陣列
            let max_n = Math.max(...f_seat);
            let meet = f_car.filter(k => opencar[k] === max_n);
            console.log(`print ${meet.join('、')}`);
        }
    }   
} 
func4([3, 1, 5, 4, 3, 2], "101000", 2);  // print 5 
func4([1, 0, 5, 1, 3], "10100", 4);  // print 4 
func4([4, 6, 5, 8], "1000", 4);  // print 2