import { fetch_auth } from "./check_auth.js"
import { render_signout_button } from "./popup.js"
import { create_and_append } from "./get_attractions.js"

let attraction_id;

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
let contact_phone=document.querySelector("#contact_phone")

let main=document.querySelector("#main");
let footer=document.querySelector("#footer");

let booking_delete_icon=document.querySelector("#booking_delete_icon")



// >監聽事件：頁面一執行就發送連線到API驗證身份
document.addEventListener("DOMContentLoaded",function(){

    fetch_auth()
    .then(data => {

        // >如果驗證失敗（尚未登入），導回首頁
        if (data.error){
            window.location.href = '/';
        }

        // >如果驗證成功
            // >1.右上角顯示登出系統按鈕 
            // >2.點擊預定行程時，會導到booking頁 
            // >3. 針對『 會員中心 』按鈕，點擊時會導流到/membercentre頁面 
            // >4.呼叫連線/api/booking的函式的同時，將user資料做為參數傳遞出去

        if (data.data){

            render_signout_button()

            let booking_cart=document.querySelector("#booking_cart")

            booking_cart.addEventListener("click",function(){
                window.location.href='/booking'
            })

            member_centre.addEventListener("click",function(){
                window.location.href='/membercentre'
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

                // >如果後端回傳的結果是200(已登入，且合法)，則將使用者預訂資料傳入渲染的函式中
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
            attraction:{id,name,address,image},
            date,
            time,
            price
        }
    }=data

    attraction_id=id;

    booking_image.src=image;
    booking_title.innerText=name;
    booking_date.innerText=date;
    booking_cost.innerText=`新台幣 ${price} 元`;
    booking_location.innerText=address;
    order_total.innerText=`新台幣 ${price} 元`

    if (time==="morning"){booking_time.innerText="早上９點到下午４點"};
    if (time==="afternoon"){booking_time.innerText="下午２點到晚上９點"};

}


// >TapPay：設定SDK參數，APP ID、Key、使用測試環境
TPDirect.setupSDK(151749,'app_vwbMDFa5lqtwzV7hrcVukM6R9IoBOtqogmNIW9f5M0ZeMNVpM1mYpEaIIDl0','sandbox');


// >TapPay：設定輸入欄位的相關設定
TPDirect.card.setup({

    fields:{
        number: {
            element: '#card_number',
            placeholder: '**** **** **** ****'
        },
        expirationDate: {
            element: '#card_expiration_date',
            placeholder: 'MM / YY'
        },
        ccv: {
            element: '#card_ccv',
            placeholder: 'CVV'
        }
    },

    styles: {
        // Style all elements
        'input': {
            'color': 'gray',
            'font-size': '16px',
            'font-weight': "500",
        },
        // style focus state
        ':focus': {
            'color': 'black'
        },
        // style valid state
        '.valid': {
            'color': 'green'
        },
        // style invalid state
        '.invalid': {
            'color': 'red'
        },
    },

    isMaskCreditCardNumber:true,  // > 設定是否要啟用遮蔽卡號功能
    maskCreditCardNumberRange: {  // > 此設定在卡號輸入正確後，會顯示前六後四碼信用卡卡號
        beginIndex: 6,
        endIndex: 11
    }

});


let order_summary_button=document.querySelector("#order_summary_button")

// >監聽事件：點擊確認訂購按鈕後，會檢查聯絡資訊跟信用卡資訊都正確後，才fetch到後端API
order_summary_button.addEventListener("click",function(){

    let check_contact_form_result=check_contact_form()

    // >取得TapPay Fields的狀態，輸入都正確會回傳true，反之則是false
    let tappay_status=TPDirect.card.getTappayFieldsStatus().canGetPrime


    TPDirect.card.getPrime((result) => {

        if (result.status !== 0 || check_contact_form_result === false) {
            return
        }

        // >確認聯絡資訊＋信用卡資訊都輸入完整後，就去取得
        if (check_contact_form_result && tappay_status){

            let time;

            if (booking_time.innerText==="早上９點到下午４點"){time="morning"};
            if (booking_time.innerText==="下午２點到晚上９點"){time="afternoon"};

            let price;

            if (booking_cost.innerText==="新台幣 2500 元"){price=2500};
            if (booking_cost.innerText==="新台幣 2000 元"){price=2000};

            let order_data={
                prime:result.card.prime,
                order:{
                    price:price,
                    trip:{
                        attraction:{
                            id:attraction_id,
                            name:booking_title.innerText,
                            address:booking_location.innerText,
                            image:booking_image.src
                        },
                        date:booking_date.innerText,
                        time:time
                    },
                    contact:{
                        name:contact_username.value,
                        email:contact_email.value,
                        phone:contact_phone.value
                    }
                }
            }


            fetch("api/orders",{
                method:"POST",
                headers:{
                    "Authorization":`Bearer ${localStorage.getItem("token")}`,
                    "Content-Type":"application/json"
                },
                body:JSON.stringify(order_data)
            })
            .then(response => {
                if(response.status===400 || response.status===403 || response.ok){return response.json()}
                else {throw new Error("API request failed")}
            })
            .then(data => {

                window.location.href = `/thankyou?number=${data.data.number}`;

            })
            .catch(error => {console.error(error)})

        }
    })
})


// > 函式：針對聯絡資訊的檢查，檢查1.每個欄位是否輸入＋2.信箱跟電話是否符合正則表達式
function check_contact_form(){

    let contact_form=document.querySelector("#contact_form");

    let contact_email=document.querySelector("#contact_email").value.trim();
    let contact_phone=document.querySelector("#contact_phone").value.trim();

    let contact_email_error_message=document.querySelector("#contact_email_error_message");
    let contact_phone_error_message=document.querySelector("#contact_phone_error_message");

    let final_ckeck_result=true;

    contact_email_error_message.innerText=""
    contact_phone_error_message.innerText=""
    

    if (!contact_form.checkValidity()){
        contact_form.reportValidity();
        return false;
    }

    let email_rule=/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/; 
    let phone_rule= /^09\d{8}$/;

    
    if (!email_rule.test(contact_email)){
        make_error_message(contact_email_error_message,"電子信箱格式有誤，請再次檢查");
        final_ckeck_result=false
    }

    if (!phone_rule.test(contact_phone)){
        make_error_message(contact_phone_error_message,"手機號碼格式有誤，請輸入09開頭共十個數字");
        final_ckeck_result=false
    }

    return final_ckeck_result

}


// >函式：單純用來產生要顯示錯誤訊息的DOM
function make_error_message(dom,message){
    dom.innerText=message
    dom.style.color="red"
}


// >TapPay：用來得知目前卡片資訊的輸入狀態
TPDirect.card.onUpdate(function (update) {

    let payment_info_error_message=document.querySelector("#payment_info_error_message")

    if (update.status.number === 1 || update.status.expiry === 1 || update.status.ccv === 1) {
        make_error_message(payment_info_error_message,"所有付款資訊皆須填寫，請再次檢查")
    }
    else if (update.status.number === 2 || update.status.expiry === 2 || update.status.ccv === 2) {
        make_error_message(payment_info_error_message,"付款資訊有誤，請再次檢查")
    } 
    else if (update.status.number === 0 && update.status.expiry === 0 &&  update.status.ccv === 0){
        make_error_message(payment_info_error_message,"")
    }

})
