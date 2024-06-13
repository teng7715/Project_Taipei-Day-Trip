import {get_attractions,current_observer,set_current_observer} from "./get_attractions.js"

let search=document.querySelector("#search");
let search_button=document.querySelector("#search_button")
let main_layout=document.querySelector(".main_layout");


//>函式：點擊捷運站navbar後，觸發事件，透過事件抓取到點擊的捷運站名，並形式上放入搜尋欄中＋執行搜尋函式
let mrt_search=(event)=>{

    let station=event.target.innerText; //?這邊的用法需要再查一下跟做筆記，沒有學過
    search.value=station;

    //>呼叫搜尋功能
    start_search();
}


//>函式：用來搜尋
let start_search=()=> {

    let keyword=search.value;

    if (keyword){ //>使用者真的有輸入資料時，才執行以下程式區塊

        let sections=document.querySelectorAll("section")

        sections.forEach(section => { //>先清空當初的內容
            main_layout.removeChild(section);
        });

        if(current_observer){ 

            //__如果觀察者實例當中有資料（也就是有在偵測），先將所有觀察區塊都取消
            current_observer.disconnect();
        
          
            set_current_observer(null);//?這邊這段隔著JS文件改值的方法，學起來
            //__再來保險起見清空當初的觀察者實例->如果觀察者實例當中有資料，也就是他有在針對某個東西做偵測時，把他偵測的狀態移除
            //__好讓我們針對搜尋建立新的觀察，避免像當初卡住的地方一樣，都搜尋了，首頁的資料還是一直跑出來
        
        }
        
        get_attractions(0,keyword);

        search.value=""
    } 
}


search_button.addEventListener("click",start_search);

export {mrt_search} 
