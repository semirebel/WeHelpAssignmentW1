// Task 4 追加 //

let currentIndex = 13; // Task 3 已經畫完 13 個了，小本本從 13 開始記
let globalAttractions = [];
let globalImages = [];
let globalHost = "";
const loadMoreBtn = document.getElementById("load-more-btn");



// Task 3

document.addEventListener("DOMContentLoaded", function() {
    // 定義兩個資料來源的網址
    const url1 = "https://cwpeng.github.io/test/assignment-3-1";
    const url2 = "https://cwpeng.github.io/test/assignment-3-2";
    

    // 使用 Promise.all 同時發出兩個 fetch 請求 (使用 fetch 抓取資料)
    Promise.all([
        fetch(url1).then(response => response.json()),
        fetch(url2).then(response => response.json()),
    ])
    .then(([data1, data2]) => {
        /* // 在 Console 印出這兩份資料觀察結構
        console.log("第一份資料：", data1);
        console.log("第二份資料：", data2); */

        // Task 4 追加 //
        globalAttractions = data1.rows;
        globalImages = data2.rows;
        globalHost = data2.host;
        /* 在.then 內使用 const 宣告變數只能在then的()內使用，系統跑完Task3部分設置的前13個 .then()的任務即結束 */
        /* Task 4 追加 "全域大倉庫"(globalAttractions、globalImages、globalHost)
        將 Promise.all 讀取到的資料完整複製存入，以供點擊"loadMore"按鈕後讀取 */


        const attractions = data1.rows; // 第一份的景點陣列
        const images = data2.rows;      // 第二份的圖片陣列
        const host = data2.host;        // 主網址 https://cwpeng.github.io/test

        // 透過 class 找到 HTML 中的兩個主要父容器
        const barsContainer = document.querySelector(".bars");
        const contentContainer = document.querySelector(".contentblocks");
        
        // 清空原本 HTML 寫死的舊資料
        barsContainer.textContent = "";
        contentContainer.textContent = "";

        // 使用迴圈把前 13 個景點的資料整理出來(3個給bar，10個給content)
        for (let i = 0; i < 13; i++) {
            const attraction = attractions[i];
            const imgData = images[i];
            const picString = imgData.pics; 
            /* 第二份資料的 pics：/resources/images/40-0.jpg/resources/images/40-1.jpg...
            有好幾張圖片的網址黏在一起，必須取出第一個 */
            
            const picArray = picString.split(/(?=\/resources)/); 
            /* split 會切除指定字串再分割，ex:"蘋果-香蕉-芭樂".split("-") 切完成為["蘋果", "香蕉", "芭樂"]
                寫成 /(?=\/resources)/，則是指定遇到/resources時進行分割但不去除指定字串，才不會破壞圖片網址。*/
            
            const firstImgUrl = host + picArray[0]; // 組合出完整的景點第一張圖網址

            /* 確認是否成功組合
            console.log(`第 ${i+1} 個景點名稱:`, attraction.sname, " | 圖片網址:", firstImgUrl); */

            // 前3個景點塞進bars
            if (i < 3) {
                // 創建外層 <div class="bars0">
                const barDiv = document.createElement("div");
                barDiv.className = `bars${i + 1}`; // 會依序建立 bars1, bars2, bars3

                // 創建圖片 <img>
                const barImg = document.createElement("img");
                barImg.src = firstImgUrl;
                barImg.className = "bar-img";
                barImg.alt = "Promotion";

                // 創建文字 <span>
                const barSpan = document.createElement("span");
                barSpan.textContent = attraction.sname;

                // 依序組合節點并塞入大容器
                barDiv.appendChild(barImg);
                barDiv.appendChild(barSpan);
                barsContainer.appendChild(barDiv);
            }
            // 後 10 個景點塞進 contentblocks
            else {
                // 創建外層 <div class="contentblocks-items">
                const itemDiv = document.createElement("div");
                itemDiv.className = "contentblocks-items";

                // 創建星星 <img>
                const starImg = document.createElement("img");
                starImg.src = "star.png";
                starImg.className = "star-img";
                starImg.alt = "Promotion";

                // 創建景點主圖 <img>
                const mainImg = document.createElement("img");
                mainImg.src = firstImgUrl;
                mainImg.className = "contentblocks-img";
                mainImg.alt = "Promotion";

                // 創建標題 <div class="contentblocks-title">
                const titleDiv = document.createElement("div");
                titleDiv.className = "contentblocks-title";
                titleDiv.textContent = attraction.sname;

                // 照順序 appendChild 進去
                itemDiv.appendChild(starImg);
                itemDiv.appendChild(mainImg);
                itemDiv.appendChild(titleDiv);
                contentContainer.appendChild(itemDiv);
            }
        }

        loadMoreBtn.addEventListener("click", function() {
            let end = currentIndex + 10; // 點擊後要畫到的終點

            for (let i = currentIndex; i < end; i++) {
                // 安全檢查：沒資料就藏按鈕並跳出
                if (i >= globalAttractions.length) {
                    loadMoreBtn.style.display = "none";
                    break;
                }

                const attraction = globalAttractions[i]; // 依目前編號至全域倉庫撈出第一份資料
                const imgData = globalImages[i]; // 依目前編號至全域倉庫撈出第二份資料(圖片)
                const picString = imgData.pics; 
                const picArray = picString.split(/(?=\/resources)/); // 切割圖片網址
                const firstImgUrl = globalHost + picArray[0]; // 組合出圖片完整網址

                // 點按鈕載入的通通都是後面的景點塞進 contentblocks

                // 製作新的物件欄位
                const itemDiv = document.createElement("div");
                itemDiv.className = "contentblocks-items";
                
                // 製作新的星星圖
                const starImg = document.createElement("img");
                starImg.src = "star.png";
                starImg.className = "star-img";
                starImg.alt = "Promotion";

                // 製作新的圖片欄位
                const mainImg = document.createElement("img");
                mainImg.src = firstImgUrl;
                mainImg.className = "contentblocks-img";
                mainImg.alt = "Promotion";

                // 製作新的物件標題欄位
                const titleDiv = document.createElement("div");
                titleDiv.className = "contentblocks-title";
                titleDiv.textContent = attraction.sname;

                // appendChild 塞入資料
                itemDiv.appendChild(starImg);
                itemDiv.appendChild(mainImg);
                itemDiv.appendChild(titleDiv);
                contentContainer.appendChild(itemDiv);
            }

            currentIndex += 10; // 進度往後推 10
        });
    })
    .catch(error => {
        console.error("處理資料失敗：", error);
    });
});

