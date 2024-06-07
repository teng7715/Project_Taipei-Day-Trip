//http://44.230.128.247:8000/api/mrts
//http://127.0.0.1:8000/api/mrts

import {mrt_search} from "./search.js"

let left_arrow=document.querySelector("#left_arrow");
let right_arrow=document.querySelector("#right_arrow");
let navbar_list=document.querySelector("#navbar_list");

let offset=0;


//連線取得捷運站景點資訊
fetch("http://44.230.128.247:8000/api/mrts")
.then(response => {
    if (response.ok){return response.json()}
    else {throw new Error("API request failed")}
})
.then(data => {
    
    let filtered_Data=data.data.filter(station => station !== null)

    for (let i=0 ; i<filtered_Data.length ; i++){
        let newLi=document.createElement("li")
        newLi.className="navbar_item"
        newLi.textContent=`${filtered_Data[i]}`
        navbar_list.appendChild(newLi)
    }

    let navbar_items=document.querySelectorAll(".navbar_item") 
    //載入完後才建立DOM節點，跟觀察事件，避免當初觀察事件比資料載入還早建立，導致什麼都按不到的局面發生

    navbar_items.forEach(item=>{
        item.addEventListener("click",mrt_search);
    })
})
.catch(error => {console.error(error)})


//函式：用來判斷視窗寬度後，回傳捷運站navbar要左右移動多少px
let get_scroll_distance=()=>{
    let screen_width=window.innerWidth;

    if (screen_width>1200){return 900}
    else {return 250}
}


//監聽事件：點擊navbar右邊箭頭時，會移動設定好的距離
right_arrow.addEventListener('click', () => {
    let max_offset=navbar_list.scrollWidth-navbar_list.clientWidth; 
    //用來計算有多少寬度是被隱藏的，而這些隱藏的總寬度，就是我們能滑動的最大距離

    let scroll_distance=get_scroll_distance()
    
    offset -= scroll_distance;                        
    // 調整每次向左移動的距離

    if (offset < -max_offset){offset = -max_offset}; // 防止滑動超出範圍
    navbar_list.style.transform = `translateX(${offset}px)`;
});


//監聽事件：點擊navbar左邊箭頭時，會移動設定好的距離
left_arrow.addEventListener('click', () => {

    let scroll_distance=get_scroll_distance()
    offset += scroll_distance; // 調整每次移動的距離

    if (offset > 0){offset = 0;} 

    navbar_list.style.transform = `translateX(${offset}px)`;
});