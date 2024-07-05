import {render_login_register_button, render_signout_button, booking_popup} from "./popup.js"


//>函式：驗證使用者身份，且針對驗證結果不同，決定要渲染登入/註冊，還是登出系統
function fetch_auth(){

    return fetch("/api/user/auth",{
        method:"GET",
        headers: {
            "Authorization":`Bearer ${localStorage.getItem("token")}`
        },
    })
    .then(response => {
        if(response.status===401 || response.ok){return response.json()}
        else {throw new Error("API request failed")}
    })
}


function navbar_check_auth(){
    
    fetch_auth()
    .then(data => {

    let booking_cart=document.querySelector("#booking_cart");
    let member_centre=document.querySelector("#member_centre");

    // >如果驗證失敗（尚未登入），1. 按鈕渲染成登入/註冊  2. 針對『 預定行程＋會員中心 』按鈕，點擊時只會跳出登入popup 
    if (data.error){

        render_login_register_button()

        booking_cart.addEventListener("click",function(){
            booking_popup()
        })        

        member_centre.addEventListener("click",function(){
            booking_popup()
        })        

    }

    // >如果驗證成功， 1. 按鈕渲染成登出 2. 針對『 預定行程 』按鈕，點擊時會導流到/booking頁面 3. 針對『 會員中心 』按鈕，點擊時會導流到/membercentre頁面
    if (data.data){
        
        render_signout_button()

        booking_cart.addEventListener("click",function(){
            window.location.href='/booking'
        })

        member_centre.addEventListener("click",function(){
            window.location.href='/membercentre'
        })
    }
})
.catch(error => {console.error(error)})

}

export { fetch_auth, navbar_check_auth }