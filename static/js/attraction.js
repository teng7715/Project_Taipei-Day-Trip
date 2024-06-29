//!!有有時右上角登入/註冊按鈕會出現Uncaught TypeError的BUG

import { create_and_append } from "./get_attractions.js"
import { fetch_auth,navbar_check_auth } from "./check_auth.js"
import { booking_popup } from "./popup.js"


// >頁面載入時，要檢查使用者狀態
navbar_check_auth()


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

    let {name, category, mrt, description, address, transport}=data.data; //>使用解構賦值

    document.querySelector("#attraction_name").innerText=name
    document.querySelector("#attraction_category").innerText=category
    document.querySelector("#attraction_mrt").innerText=mrt
    document.querySelector("#attraction_description").innerText=description
    document.querySelector("#attraction_address").innerText=address
    document.querySelector("#attraction_transport").innerText=transport //?innerText

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
        page--  //?符號先後的差異
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
            dot.classList.remove("active") //?classList的用法
        })
        
        slides[page].style.display="block";
        dots[page].classList.add("active");
        //++這邊想想怎麼樣可以把圖片動畫加進去
    } 
}


//>以下是針對選項不同，顯示不同價格的JS處理

let time_radios=document.querySelectorAll('input[name="time"]'); //?querySelector可以用input[name="time"]
let fee_amount=document.querySelector("#fee_amount");
let fees={
    morning:"新台幣 2000元",
    afternoon:"新台幣 2500元"
};


//>事件與觸發函式：當選項改變(被點選時），觸發事件，並透過event.target找到被改變/點選的值後，對照該顯示的金額內容
time_radios.forEach((radio)=>{
    radio.addEventListener("change",(event)=>{ //>透過change事件來追蹤點點改變時，該呈現的說明文字
        let selected_time=event.target.value;
        fee_amount.innerText=fees[selected_time]
    })
})


let sent_booking_button=document.querySelector("#sent_booking_button")

// >監聽事件：當使用者點擊『開始預約行程按鈕時』，先去User API驗證是否合法登入，如果尚未登入或不合法，跳出popup，反之，則去執行建立booking資料的函式
sent_booking_button.addEventListener("click",function(event){

    event.preventDefault();

    fetch_auth()
    .then(data =>{

        if (data.error){
            booking_popup()
        }

        if (data.data){
            create_booking_data()
        }

    })
    .catch(error => console.log(error))
})


// >函式：整理以及建立要傳到後端的booking資料
function create_booking_data(){

    let booking_form=document.querySelector("#booking_form");

    //?這段用法記得筆記起來
    // >透過checkValidity()方法檢查表單中的任何一個元素是否有效（就是有沒有符合當初HTML的設定）
    if (!booking_form.checkValidity()) { 
        
        // >如果沒有，就透過reportValidity()方法觸發表單的驗證，並顯示預設的錯誤訊息
        booking_form.reportValidity();
        return; // > 當表單無效時，return會阻止後續的程式碼執行
    }


    let date=document.querySelector("input[name='date']").value
    let time=document.querySelector("input[name=time]:checked").value //?這邊input[name=time]:checked的用法記得做筆記
    let fee_amount=document.querySelector("#fee_amount").textContent


    let int_attraction_id=parseInt(attraction_id) // >原本的景點ID是字串格式，這邊轉換成數值


    if (fee_amount==="新台幣 2000元"){ 
        fee_amount=2000;
    }
    else if(fee_amount==="新台幣 2500元"){
        fee_amount=2500;
    }


    let booking_data={
        "attractionId": int_attraction_id,
        "date": date,
        "time": time,
        "price":fee_amount
    }

    sent_booking_data(booking_data)

}


// >函式：POST方法發送連到Booking API
function sent_booking_data(booking_data){

    fetch("/api/booking",{
        method:"POST",
        headers:{
            "Authorization":`Bearer ${localStorage.getItem("token")}`,
            "Content-Type":"application/json"
        },
        body:JSON.stringify(booking_data)
    })
    .then(response => {
        if(response.ok){return response.json()}
        else {throw new Error("API request failed")}
    })
    .then(data => {
        if (data.ok){
            window.location.href = '/booking';
        }
    })
    .catch(error => console.error(error))

}