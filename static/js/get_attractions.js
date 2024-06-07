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


// 函式：用來建立連線+將下一頁資料（無論有還沒有）傳送出去
let get_attractions=(page,keyword="")=>{ 

    fetch(`http://44.230.128.247:8000/api/attractions?page=${page}&keyword=${keyword}`)
    .then(response => {
        if (response.ok){return response.json()}
        else {throw new Error("API request failed")}
    })
    .then(data => {
        if (data.data.length>0){
            create_attraction_section(data);
            handle_nextPage(data.nextPage,keyword);
        }
    })
    .catch(error => {console.error(error)})
}


//函式：用來判斷是否有下一頁資料，因此需要建立觀察點的觀察事件，以及如果與觀察點接觸，我們要再去連線取得下一頁資料
let handle_nextPage=(nextPage,keyword)=>{
   
    if (current_observer){
            current_observer.disconnect(); 
            //無論有沒有下一頁，以防萬一我們都先清空所有觀察點，避免EX:首頁有觀察點，但我自己搜尋又建立一個觀察點（當初卡住的地方）
            //清空後下面才去依照狀況看是否要建立新的觀察點
    }

    if (nextPage !==null){ //如果nextPage，不是空值，也就是有下一頁，我們才建立監聽事件
        current_observer=new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting){
                    get_attractions(nextPage,keyword)
                }
            })
        })
    current_observer.observe(detection_point);
    }
}


//函式：為了將使用者搜尋/或點捷運站navbar時，重新清空觀察點，所以建立一個能讓search.js改變變數值函式
let set_current_observer=(observer) => {
    current_observer=observer;
}


//輸出
export {
    get_attractions,
    current_observer,
    set_current_observer,
};
