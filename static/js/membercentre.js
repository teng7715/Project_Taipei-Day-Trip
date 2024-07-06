import { fetch_auth } from "./check_auth.js"
import { render_signout_button } from "./popup.js"
import { create_and_append } from "./get_attractions.js"


// >監聽事件：頁面一執行就發送連線到API驗證身份
document.addEventListener("DOMContentLoaded",function(){

    fetch_auth()
    .then(data => {

        // >如果驗證失敗（尚未登入），導回首頁
        if (data.error){
            window.location.href = '/';
        }

        // >如果驗證成功
            // >1. 右上角顯示登出系統按鈕 
            // >2. 針對『 預定行程 』按鈕，點擊時會導流到/booking頁面
            // >3. 針對『 會員中心 』按鈕，點擊時會導流到/membercentre頁面
            // >4. 執行會連線到/api/membercentre的函式

        if (data.data){

            render_signout_button()

            let booking_cart=document.querySelector("#booking_cart");
            let member_centre=document.querySelector("#member_centre");

            booking_cart.addEventListener("click",function(){
                window.location.href='/booking'
            })

            member_centre.addEventListener("click",function(){
                window.location.href='/membercentre'
            })

            get_member_order_history()
           
        }
    })
    .catch(error => {console.error(error)})

})  


// >函式：連到/api/membercentre，取得使用者所有訂購歷史紀錄
function get_member_order_history(){

    fetch("/api/membercentre",{
        headers:{"Authorization":`Bearer ${localStorage.getItem("token")}`},
    })
    .then(response => {
        if(response.status===403 || response.ok){return response.json()}
        else {throw new Error("API request failed")}
    })
    .then(data => {

        // >如果後端回傳的結果是403(尚未登入、驗證失敗)，則導到首頁
        if (data.error) {
            window.location.href = '/';
        }

        // >如果後端回傳的結果是200(已登入，且合法)，且使用者有歷史訂單資料
        if (data.data) {
            render_order_history_data(data.data)
        }

        // >反之沒有購物車資料，就去渲染沒有資料的頁面
        if (data.data === null){
            render_no_order_history_data()
        }

    })
    .catch(error => {console.error(error)})

}

// >函式：用來渲染『有』歷史紀錄資料時的頁面
function render_order_history_data(datas){

    let order_history=document.querySelector("#order_history")

    datas.forEach(order => {

        if (order.time==="morning"){order.time="早上９點到下午４點"};
        if (order.time==="afternoon"){order.time="下午２點到晚上９點"};

        if (order.status===1){order.status="已付款"};
        if (order.status===0){order.status="未付款"};

        let new_order_history_item=create_and_append(order_history,"div","order-history__item","");

        create_and_append(new_order_history_item,"div","order-history__item-decorate-bar","");

        let new_img_container=create_and_append(new_order_history_item,"div","order-history__item-image-container","");
        let new_img=create_and_append(new_img_container,"img","order-history__item-image","");
        new_img.src=order.image;
        new_img.alt="Attraction Image";

        let new_order_details_container=create_and_append(new_order_history_item,"div","order-history__item-details-container","");
        create_and_append(new_order_details_container,"p","",`訂單編號：${order.order_number}`);
        create_and_append(new_order_details_container,"p","",`訂購景點：${order.attraction_name}`);
        create_and_append(new_order_details_container,"p","",`預定地址：${order.address}`);
        create_and_append(new_order_details_container,"p","",`預定日期：${order.date}`);
        create_and_append(new_order_details_container,"p","",`預定時段：${order.time}`);
        create_and_append(new_order_details_container,"hr","order-history__item-details-separator","");
        create_and_append(new_order_details_container,"p","",`聯絡人姓名：${order.contact_name}`);
        create_and_append(new_order_details_container,"p","",`聯絡人信箱：${order.contact_email}`);
        create_and_append(new_order_details_container,"p","",`聯絡人電話：${order.contact_phone}`);
        create_and_append(new_order_details_container,"hr","order-history__item-details-separator","");
        create_and_append(new_order_details_container,"p","",`訂單總額：${order.price}`);
        create_and_append(new_order_details_container,"p","",`訂單總額：${order.status}`);

    })

}


// >函式：用來渲染『無』歷史紀錄資料時的頁面
function render_no_order_history_data(datas){

    let order_history_no_info=document.querySelector("#order_history_no_info")
    order_history_no_info.classList.remove("hidden")

    let footer=document.querySelector("#footer")
    footer.classList.replace("footer", "footer--no-booking")
}