import {get_attractions,current_observer,set_current_observer} from "./get_attractions.js"

let search=document.querySelector("#search");
let search_button=document.querySelector("#search_button")
let main_layout=document.querySelector(".main_layout");


//函式：點擊捷運站navbar後，觸發事件，透過事件抓取到點擊的捷運站名，並形式上放入搜尋欄中＋執行搜尋函式
let mrt_search=(event)=>{

    let station=event.target.innerText;
    search.value=station;

    //呼叫搜尋功能
    start_search();
}


//函式：用來搜尋
let start_search=()=> {

    let keyword=search.value;


    if (keyword){

        let sections=document.querySelectorAll("section")

        sections.forEach(section => { //先清空當初的內容
            main_layout.removeChild(section);
        });

        if(current_observer){ 
            //再來清空當初的觀察者實例->如果觀察者實例當中有資料，也就是他有在針對某個東西做偵測時，把他偵測的狀態移除
            //好讓我們針對搜尋建立新的觀察，避免像當初卡住的地方一樣，都搜尋了，首頁的資料還是一直跑出來
            //也清空紀錄已載入頁面的陣列資料
            current_observer.disconnect();
            let clean_pages=[];

            set_current_observer(null,clean_pages);
        }

        get_attractions(0,keyword);

        search.value=""
    } 
}


search_button.addEventListener("click",start_search);

export {mrt_search} 
