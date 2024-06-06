
//這邊連線的網址應該要改成我們線上環境的IP位置嗚嗚！
//然後API的檔案接受的來源也要改一下
// http://44.230.128.247:8000/api/mrts
// http://127.0.0.1:8000/api/mrts

let left_arrow=document.querySelector("#left_arrow");
let right_arrow=document.querySelector("#right_arrow");
let navbar_list=document.querySelector("#navbar_list");

let offset=0;

fetch("http://44.230.128.247:8000/api/mrts")
.then(response => {
    if (response.ok){return response.json()}
    else {throw new Error("API request failed")}
})
.then(data => {
    
    let filtered_Data=data.data.filter(station => station !== null) //這邊到時候記得做筆記，新學到的，過濾語法

    for (let i=0 ; i<filtered_Data.length ; i++){
        let newLi=document.createElement("li")
        newLi.className="navbar_item"
        newLi.textContent=`${filtered_Data[i]}`
        navbar_list.appendChild(newLi)
    }
})
.catch(error => {console.error(error)})


//試試看囉（？）


// right_arrow.addEventListener('click', () => {
//     if (offset > -(navbar_list.scrollWidth - navbar_list.clientWidth)) {
//         offset -= 150; // Adjust the distance of each move
//         navbar_list.style.transform = `translateX(${offset}px)`;
//     }
// });


// left_arrow.addEventListener('click', () => {
//     if (offset < 0) {
//         offset += 150; // Adjust the distance of each move
//         navbar_list.style.transform = `translateX(${offset}px)`;
//     }
// });


right_arrow.addEventListener('click', () => {
    let max_offset=navbar_list.scrollWidth-navbar_list.clientWidth; //用來計算有多少寬度是被隱藏的，而這些隱藏的總寬度，就是我們能滑動的最大距離
    offset -= 900; // 調整每次向左移動的距離（這邊有點反直覺，但原理就是雖然我們按右鍵是要看到更右邊的資訊，但實際上那一整條資料是往左移
    if (offset < -max_offset){offset = -max_offset}; // 防止滑動超出範圍
    navbar_list.style.transform = `translateX(${offset}px)`;
});

left_arrow.addEventListener('click', () => {
    offset += 900; // 調整每次移動的距離
    if (offset > 0){offset = 0;} // 防止滑動超出範圍，這邊判斷是基準是offset > 0，其實是檢查 offset 是否小於 0，也就是說，我們是不是已經有點擊右邊箭頭讓他滑動。如果 offset 小於 0，表示內容向右滑動過，這時我們才允許進一步向左滑動。
    navbar_list.style.transform = `translateX(${offset}px)`;
});


