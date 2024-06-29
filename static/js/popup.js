
// >監聽事件：頁面載入後，針對Popup建立監聽事件
document.addEventListener('DOMContentLoaded',function (){

    if (document.querySelector("#popup")){
        setup_login_popup();
    }
        
});


// >函式：用在當點擊『預定行程』or 『開始預約行程』時，如果尚未登入，會跳出登入popup
function booking_popup(){

    let popup=document.querySelector("#popup");
    let popup_overlay=document.querySelector("#popup_overlay");
    let popup_login_section=document.querySelector("#popup_login_section");
    let popup_register_section=document.querySelector("#popup_register_section");

    popup.classList.remove("popup--hidden")
    popup_overlay.classList.remove("popup--hidden")

    //>除了上方寫到的讓popup跟overlay整體呈現出來之外，也透過下面兩行重置，讓每次點了都會先顯示登入區塊，而不會被之前點擊的結果給影響（EX:之前在註冊區塊關掉的，結果下次再點一次，變成先呈現註冊區塊）
    popup_login_section.classList.remove("popup--hidden");
    popup_register_section.classList.add("popup--hidden");

    clean_input_data() //>清除之前輸入過的資料＋提示語狀態

}


//>函式：當使用者未登入時，畫面要渲染成可以看到登入/註冊按鈕，與popup畫面
function render_login_register_button(){

    let login_or_signout=document.querySelector("#login_or_signout");
    let popup=document.querySelector("#popup");
    let popup_login_section=document.querySelector("#popup_login_section");
    let popup_register_section=document.querySelector("#popup_register_section");
    let popup_overlay=document.querySelector("#popup_overlay");


    login_or_signout.textContent="登入/註冊";

    login_or_signout.addEventListener("click",function(){

        popup.classList.remove("popup--hidden")
        popup_overlay.classList.remove("popup--hidden")

        //>除了上方寫到的讓popup跟overlay整體呈現出來之外，也透過下面兩行重置，讓每次點了都會先顯示登入區塊，而不會被之前點擊的結果給影響（EX:之前在註冊區塊關掉的，結果下次再點一次，變成先呈現註冊區塊）
        popup_login_section.classList.remove("popup--hidden");
        popup_register_section.classList.add("popup--hidden");

        clean_input_data() //>清除之前輸入過的資料＋提示語狀態
    
    })
}


//>函式：當使用者已登入時，畫面要渲染成有登出按鈕＋針對登出按鈕建立監聽事件
function render_signout_button(){
    let login_or_signout=document.querySelector("#login_or_signout");
    login_or_signout.textContent="登出系統";

    login_or_signout.addEventListener("click",function(){
        localStorage.removeItem("token")
        window.location.reload()
    })
}


//>函式：呼叫後就會建立popup畫面中，叉叉、送出鈕等等有關的監聽事件
function setup_login_popup(){

    let popup=document.querySelector("#popup");
    let popup_login_section=document.querySelector("#popup_login_section");
    let popup_register_section=document.querySelector("#popup_register_section");
    let popup_overlay=document.querySelector("#popup_overlay");
    let popup_close_icon=document.querySelectorAll(".popup__close-icon");
    let login_footer_link=document.querySelector("#login_footer_link");
    let register_footer_link=document.querySelector("#register_footer_link");
    let register_button=document.querySelector("#register_button");
    let login_button=document.querySelector("#login_button")


    //>監聽事件：點擊後可以關閉popup的叉叉按鈕
    popup_close_icon.forEach(icon =>{
        icon.addEventListener("click",function(){
            popup.classList.add("popup--hidden")
            popup_overlay.classList.add("popup--hidden")
        })
        clean_input_data() //>清除之前輸入過的資料
    })


    //>監聽事件：登入頁底下，點擊時可以切換到註冊頁的文字
    login_footer_link.addEventListener("click",function(){
        popup_login_section.classList.add("popup--hidden")
        popup_register_section.classList.remove("popup--hidden")
    })


    //>監聽事件：註冊頁底下，點擊時可以切換到登入頁的文字
    register_footer_link.addEventListener("click",function(){
        popup_login_section.classList.remove("popup--hidden")
        popup_register_section.classList.add("popup--hidden")
    })


    //>監聽事件：註冊按鈕
    register_button.addEventListener("click",function(event){
        event.preventDefault();
        send_register_data();
    })


    //>監聽事件：登入按鈕
    login_button.addEventListener("click",function(event){
        event.preventDefault();
        send_login_data();
    })

}


//>函式：用來清除輸入欄資料＋讓所有提示語都隱藏  
function clean_input_data(){
    document.querySelectorAll(".popup__input").forEach(input =>{
        input.value=""
    })

    document.querySelector("#login_message").classList.add("popup--hidden");
    document.querySelector("#register_message").classList.add("popup--hidden");
};


//>函式：用來處理提示字的顯示、內容和對應的CSS顏色設定
function show_message(target,message,css_color){
    target.classList.remove("popup--hidden","popup__message--error","popup__message--success");
    target.classList.add(css_color);
    target.innerText=message;
};


//>函式：連線註冊API，且會檢查輸入欄位是否不為空的 
function send_register_data(){

    let register_name=document.querySelector("#register_name");
    let register_email=document.querySelector("#register_email");
    let register_password=document.querySelector("#register_password");
    let register_message=document.querySelector("#register_message");

    //>註冊帳號時，可能的情境一：任一欄位的資料沒有輸入＝> 就退回去不讓他送出，且傳送錯誤訊息
    if ( !register_name.value || !register_email.value || !register_password.value){
        show_message(register_message,"所有欄位均為必填，請確認是否遺漏","popup__message--error")
        return;
    }

    fetch("/api/user",{
        method:"POST",
        headers: {"Content-Type":"application/json"},
        body:JSON.stringify({
            name:register_name.value,
            email:register_email.value,
            password:register_password.value
        })
    })
    .then(response => {
        if (response.status===400 || response.ok){return response.json()}; 

        if (response.status===422){throw new Error("Validation failed")}
        else {throw new Error("API request failed")}
    })
    .then(data => {
        if (data.error){
            show_message(register_message,"此Email已註冊過，請改使用其他Email","popup__message--error");
        }
        if (data.ok){
            show_message(register_message,"註冊成功，請重新登入！\n(兩秒後將自動刷新頁面）","popup__message--success");
            
            //> 在註冊成功後，自動刷新當前頁面
            setTimeout(() => {  
                window.location.reload(); //??setTimeout用法做筆記
            }, 2000);
        }
    })
    .catch(error => {
        if(error.message === "API request failed") {
            show_message(register_message,"無法連接伺服器，請稍後再試","popup__message--error");
        }
        if(error.message === "Validation failed") {
            show_message(register_message,"註冊格式有誤，請注意電子郵件格式","popup__message--error");
        }
        console.error(error)
    })
}


//>函式：連線登入API，且會檢查輸入欄位是否不為空的
function send_login_data(){

    let login_email=document.querySelector("#login_email");
    let login_password=document.querySelector("#login_password"); 
    let login_message=document.querySelector("#login_message");

    if ( !login_email.value || !login_password.value){
        show_message(login_message,"所有欄位均為必填，請確認是否遺漏","popup__message--error")
        return;
    }

    fetch("/api/user/auth",{
        method:"PUT",
        headers: {"Content-Type":"application/json"},
        body:JSON.stringify({
            email:login_email.value,
            password:login_password.value
        })
    })
    .then(response => {
        if (response.status===400 || response.ok){return response.json()};
       
        if (response.status===422){throw new Error("Validation failed")}
        else {throw new Error("API request failed")}
    })
    .then(data => {
        if (data.error){
            show_message(login_message,"電子郵件或密碼錯誤，請再次確認","popup__message--error");
        }
        if (data.token){
            localStorage.setItem('token',data.token)
            show_message(login_message,"登入成功！\n(兩秒後將自動刷新頁面）","popup__message--success");

            //> 在登入成功後，自動刷新當前頁面
            setTimeout(() => {  
                window.location.reload(); 
            }, 2000);
        }
    })
    .catch(error => {
        if(error.message === "API request failed") {
            show_message(login_message,"無法連接伺服器，請稍後再試","popup__message--error");
        }
        if(error.message === "Validation failed") {
            show_message(login_message,"輸入格式有誤，請注意電子郵件格式","popup__message--error");
        }
        console.error(error)
    })
}

export { render_login_register_button, render_signout_button, booking_popup }; 