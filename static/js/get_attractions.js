let main_layout=document.querySelector(".main_layout");
let detection_point=document.querySelector(".detection_point");

let current_observer=null; //儲存目前的觀察者實例

//函式：能用來創建各種標籤節點
let create_and_append=(parent,tag,className,text)=>{ 
    let element=document.createElement(tag);
    if (className){
        element.classList.add(className);
    }
    element.textContent=text;
    parent.appendChild(element);
    return element;
}


//函式：用來創建12個（或任意數量）景點資訊，並變成景點卡片
let create_attraction_section=(data)=>{

    let data_count=data.data.length
    let newSection=document.createElement("section");

    if (data_count>=1 && data_count<=4){
        newSection.className="section_sheard section_layout_for_one_to_four"
    }
    else if(data_count<=8){
        newSection.className="section_sheard section_layout_for_one_to_eight"
    }
    else if(data_count<=12){
        newSection.className="section_sheard section_layout_for_one_to_twelve"
    }
   

    for (let attraction of data.data ){
    
        let newArticle=create_and_append(newSection,"article","","")
        let newDiv1=create_and_append(newArticle, "div", "name_and_image_layout", "");
        let newDiv2=create_and_append(newArticle, "div", "station_and_category", "");
        
        let newFigure=create_and_append(newDiv1,"figure","","");
        let newImg=create_and_append(newFigure,"img","attraction_image","");
        newImg.src=attraction.images[0];

        let newFigcaption=create_and_append(newDiv1,"figcaption","","");
        let newAttractionName=create_and_append(newFigcaption,"div","attraction_name",attraction.name);

        let newAttractionStation=create_and_append(newDiv2,"div","attraction_station",attraction.mrt);
        let newAttractionCategory=create_and_append(newDiv2,"div","attraction_category",attraction.category);

        main_layout.insertBefore(newSection,detection_point); //一律都在偵測點前，建立那十二個景點
    }
}


// 函式：用來建立連線＆如果有下一頁，將下一頁頁碼傳送出去
let get_attractions=(page,keyword="")=>{ 

    fetch(`/api/attractions?page=${page}&keyword=${keyword}`)
    .then(response => {
        if (response.ok){return response.json()}
        else {throw new Error("API request failed")}
    })
    .then(data => {

        if (current_observer){
            current_observer.disconnect(); 
            //載入資料前，以防萬一我們都先清空所有觀察點，避免EX:首頁有觀察點，但我自己搜尋又建立一個觀察點（當初卡住的地方）
            
            // 邏輯釐清：
            // 載入點目前的狀態是『載入第二頁』，OK去執行了，載入點也應該要轉換成『載入第三頁』，
            // 但因為我們高速轉動頁，導致這個載入點轉換前又被我們碰到
            // 第二頁因此重複加載，問題出在這裡，所以『載入點轉換成正確頁面前，載入點偵測效果都要失效』
        }

        //觀察點清空後，渲染資料
        if (data.data.length>0){
            create_attraction_section(data);
        }

        if (data.nextPage !==null){
            handle_nextPage(data.nextPage,keyword); 
        }

    })
    .catch(error => {console.error(error)})
}



//函式：有下一頁資料才會呼叫此函式，建立載入觀察點。如果載入觀察點被接觸，我們要再去連線取得下一頁資料
let handle_nextPage=(nextPage,keyword)=>{

    current_observer=new IntersectionObserver((entries) => { //page0時，觀察點會在『載入第一頁』的狀態，page1時，觀察點會在『載入第二頁』的狀態
        entries.forEach(entry => {
            if (entry.isIntersecting){   
                
                // 雖然確定接觸到了，但在載入資料前，先刪除所有接觸點
                current_observer.disconnect()   
                // EX:page0時，觀察點會在『載入第一頁』的狀態，雖然確定接觸到了，但在載入第一頁資料前就先刪掉接觸點，好避免先載入資料
                
                get_attractions(nextPage,keyword);

            }
        })
    })
    current_observer.observe(detection_point);
}


//函式：為了將使用者搜尋/或點捷運站navbar時，重新清空觀察點＋清空紀錄已載入頁面的陣列，所以建立一個能讓search.js改變變數值函式
let set_current_observer=(observer) => {
    current_observer=observer;
}


//輸出
export {
    get_attractions,
    current_observer,
    set_current_observer,
};
