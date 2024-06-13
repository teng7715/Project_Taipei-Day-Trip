import {create_and_append} from "./get_attractions.js"


//>函式：用來連線取得指定景點細節資料
let load_attraction_info=(attraction_id)=>{

    fetch(`/api/attraction/${attraction_id}`) 
    .then(reponse => {
        if (reponse.ok){return reponse.json()}
        else{throw new Error ("API request failed")}
    })
    .then(data => {
        update_basic_info(data)
        render_images_and_dots(data.data.images)
        initialize_slider()
    })
    .catch(error => {console.error(error)});

}

//>取得路徑後，做切割，好取得我們要的景點編號，並將編號傳入連線函式中
let url=location.pathname
let url_split=url.split("/") 
let attraction_id=url_split[2]

load_attraction_info(attraction_id)


//>函式：單一景點資料中，除了圖片以外的資料，渲染到畫面上
function update_basic_info(data){

    let {name, category, mrt, description, address, transport}=data.data;

    document.querySelector("#attraction_name").innerText=name
    document.querySelector("#attraction_category").innerText=category
    document.querySelector("#attraction_mrt").innerText=mrt
    document.querySelector("#attraction_description").innerText=description
    document.querySelector("#attraction_address").innerText=address
    document.querySelector("#attraction_transport").innerText=transport

}

//>函式：處理圖片+點點的渲染
function render_images_and_dots(images){

    let image_container=document.querySelector('#article__image-container');
    let dots_container=document.querySelector("#article__image-dots-container");


    //>迴圈：將照片透過appendChild的方式，加到HTML當中，有幾張就加幾次
    images.forEach((url)=>{
        let newImage=create_and_append(image_container,"img","article__image","");
        newImage.src=url;
        newImage.alt="Attraction photo";
    })


    //>迴圈：以景點數量為基準，透過回圈產生出點點div
    for (let i=0;i<images.length;i++){
        let newDot=create_and_append(dots_container,"div","article__image-dot","")
    }
}


//>函式組：初始化頁面＋建立事件監聽＋事件觸發後要處理的函式
function initialize_slider(){

    let slides=document.querySelectorAll(".article__image")
    let dots=document.querySelectorAll(".article__image-dot")
    let page=0;


    show_slides(0)
    //>初始化頁面，讓圖片起始值為0（與陣列編號好對照），並將此編號傳送到函式中處裡


    let left_arrow=document.querySelector("#left_arrow");
    let right_arrow=document.querySelector("#right_arrow");


    //>將箭頭圖示＋每個點點，建立點擊事件
    left_arrow.addEventListener("click",show_previous_page)
    right_arrow.addEventListener("click",show_next_page)
    dots.forEach((dot,index)=>{
        dot.addEventListener("click",()=> {return show_direct_page(index)}) 
        //?我原本的寫法不行的原因記得寫成筆記
    })
     

    //>函式：點擊左邊箭頭，表示要回去看上一張圖，圖片值減一後，將此數值傳入處理幻燈片的函式
    function show_previous_page(){
        page--
        if (page<0){page=slides.length-1} //>如果page被點到小於0時，則將page轉跳回最後一張幻燈片的編號，做到照片循環
        show_slides(page)
    }

    //>函式：點擊右邊箭頭，表示要看下一張圖，圖片值加一後，將此數值傳入處理幻燈片的函式
    function show_next_page(){
        page++
        if (page>slides.length-1){page=0} //>如果page大於幻燈片總數，則將page轉跳回第一張幻燈片的編號，做到照片循環
        show_slides(page)
    }

    //>函式：直接點擊點點的時候，page這個變數要記得變化，避免箭頭的page與點點的page數值產生衝突
    function show_direct_page(index){
        page=index
        show_slides(page)
    }    
    
    //>函式：用來清空目前所有顯示狀況，與依照參數給定的值，來得知該顯示哪張圖片/點點
    function show_slides(page){

        slides.forEach((slide)=>{
            slide.style.display="none";
        })

        dots.forEach((dot)=>{
            dot.classList.remove("active")
        })
        
        slides[page].style.display="block";
        dots[page].classList.add("active");

    } 
}










    

    











//>以下是針對選項不同，顯示不同價格的JS處理

let time_radios=document.querySelectorAll('input[name="time"]');
let fee_amount=document.querySelector("#fee_amount");
let fees={
    morning:"新台幣 2000元",
    afternoon:"新台幣 2500元"
};


//>事件與觸發函式：當選項改變(被點選時），觸發事件，並透過event.target找到被改變/點選的值後，對照該顯示的金額內容
time_radios.forEach((radio)=>{
    radio.addEventListener("change",(event)=>{
        let selected_time=event.target.value;
        fee_amount.innerText=fees[selected_time]
    })
})

