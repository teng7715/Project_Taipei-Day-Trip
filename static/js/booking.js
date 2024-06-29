import { fetch_auth } from "./check_auth.js"
import { render_signout_button } from "./popup.js"
import { create_and_append } from "./get_attractions.js"


// >監聽事件：頁面一執行就先取得DOM以及發送連線到API驗證身份
document.addEventListener("DOMContentLoaded",function(){

    let booking_username=document.querySelector("#booking_username");
    let booking_image=document.querySelector("#booking_image");
    let booking_title=document.querySelector("#booking_title");
    let booking_date=document.querySelector("#booking_date");
    let booking_time=document.querySelector("#booking_time");
    let booking_cost=document.querySelector("#booking_cost");
    let booking_location=document.querySelector("#booking_location");
    let order_total=document.querySelector("#order_total");

    let contact_username=document.querySelector("#contact_username");
    let contact_email=document.querySelector("#contact_email");
    let main=document.querySelector("#main");
    let footer=document.querySelector("#footer");

    let booking_delete_icon=document.querySelector("#booking_delete_icon")


    fetch_auth()
    .then(data => {

        // >如果驗證失敗（尚未登入），導回首頁
        if (data.error){
            window.location.href = '/';
        }

        // >如果驗證成功，1.右上角顯示登出系統按鈕 2.點擊預定行程時，會導到booking頁 3.呼叫連線/api/booking的函式的同時，將user資料做為參數傳遞出去
        if (data.data){

            render_signout_button()

            let booking_cart=document.querySelector("#booking_cart")

            booking_cart.addEventListener("click",function(){
                window.location.href='/booking'
            })

            get_booking_data(data)
           
        }
    })
    .catch(error => {console.error(error)})

})  


// >監聽事件：點擊垃圾桶icon時，連線到刪除資料的API，刪除成功刷新頁面，如果有身份問題，導流到首頁
booking_delete_icon.addEventListener("click",function(){

    fetch("/api/booking",{
        method:"DELETE",
        headers:{
            "Authorization":`Bearer ${localStorage.getItem("token")}`
        },
    })
    .then(response => {
        if(response.status===403 || response.ok){return response.json()}
        else {throw new Error("API request failed")}
    })
    .then(data =>{

        if (data.ok){
            window.location.reload();
        }

        if (data.error){
            window.location.href = '/';
        }
    })
    .catch(error => {console.error(error)})

})


// >執行連線：連到/api/booking，取得使用者的購物車資料
async function get_booking_data(user) {

        try{
            let response=await fetch("/api/booking",{
                method:"GET",
                headers: {
                    "Authorization":`Bearer ${localStorage.getItem("token")}`
                },
            })

            if (response.status===403 || response.ok){
                let data=await response.json()

                // >如果後端回傳的結果是403(尚未登入、驗證失敗)，則導到首頁
                if (data.error) {
                    window.location.href = '/';
                }

                // >如果後端回傳的結果是200(已登入，且合法)，則將使用者預訂資料，以及全域的user變數傳入渲染的函式中
                if (data.data) {

                    // >使用者有購物車資料，就將會員資訊＋購物車資料拿去渲染
                    render_booking_data(data,user.data)
                }

                if (data.data === null){

                    // >反之沒有購物車資料，就去渲染沒有資料的頁面
                    render_no_booking_data(user.data)

                }
                
            }
            else {throw new Error("API request failed");}
        }
        catch (error) {console.error(error);}
}


// >函式：用來渲染『無』購物車資料狀態時的頁面
function render_no_booking_data(user){

    main.innerHTML=""
    
    let newSection=create_and_append(main,"section","booking-detail","")
    create_and_append(newSection,"h3","booking-detail__greeting",`您好，${user.name}，待預定的行程如下：`)
    create_and_append(newSection,"p","booking-detail__no-booking","目前沒有任何待預訂的行程")

    footer.classList.replace("footer", "footer--no-booking")

}


// >函式：用來渲染『有』購物車資料狀態時的頁面
function render_booking_data(data,user){

    booking_username.innerText=user.name
    contact_username.value=user.name
    contact_email.value=user.email

    let {
        data:{
            attraction:{name,address,image},
            date,
            time,
            price
        }
    }=data

    booking_image.src=image;
    booking_title.innerText=name;
    booking_date.innerText=date;
    booking_cost.innerText=`新台幣 ${price} 元`;
    booking_location.innerText=address;
    order_total.innerText=`新台幣 ${price} 元`

    if (time==="morning"){booking_time.innerText="早上９點到下午４點"};
    if (time==="afternoon"){booking_time.innerText="下午２點到晚上９點"};

}


