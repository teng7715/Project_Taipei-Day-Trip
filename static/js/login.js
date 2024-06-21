//__後面上線要做的事情

    //!!2. 在EC上下載所有需要用到的後端工具
    //__4. 將地端的程式碼整理乾淨  
    //!!這個做到一半！！！ 整剩下這個檔案＋ａｐｐ．ｐｙ，其他都整理檢查完了
    //__5. 地端再次運作狀況
    //__6. 將程式碼上傳，並部署到EC2跟檢查（真緊張）


// >監聽事件：頁面載入後，透過連線的方式取得登入/註冊popup畫面的HTML內容，並在之後驗證使用者身份＋渲染畫面＋針對Popup建立監聽事件
document.addEventListener('DOMContentLoaded',function (){

    fetch('/static/login.html')
    .then(response => response.text()) //?response.text() 會將取得到的回應，解析為一個字串
    .then(data => {
        document.querySelector('.login-popup').innerHTML = data;

        //__Bug修復處理邏輯：
        //__讓針對『身份驗證同時渲染畫面&Popup畫面的監聽事件』的函式呼叫，發生在Popup HTML都建構完之後，避免Uncaught TypeError

        setup_popup();
        check_auth()
    })
    .catch(error => {console.error(error)})

});


//>函式：驗證使用者身份，且針對驗證結果不同，決定要渲染登入/註冊，還是登出系統
function check_auth(){

    fetch("/api/user/auth",{
        method:"GET",
        headers: {
            "Authorization":`Bearer ${localStorage.getItem("token")}`
        },
    })
    .then(response => {
        if(response.status===401 || response.ok){return response.json()}
        else {throw new Error("API request failed")}
    })
    .then(data => {
        
        if (data.error){
            render_login_register_button()
        }

        if (data.data){
            render_signout_button()
        }
    })
    .catch(error => {console.error(error)})

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
function setup_popup(){

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
//!!這個整理到一半！！！他下面的都還沒整理
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
        if (response.status===500){throw new Error("API request failed")}
        if (response.status===400){throw new Error("Has already been registered")}
        if (response.status===422){throw new Error("Validation failed")}
        if (response.ok){return response.json()} //!!這裡感覺可以在優化
    })
    .then(data => {
        show_message(register_message,"註冊成功，請重新登入！\n(兩秒後將自動刷新頁面）","popup__message--success");

        //> 在註冊成功後，自動刷新當前頁面
        setTimeout(() => {  
            window.location.reload(); //??setTimeout用法做筆記
        }, 2000);
    })
    .catch(error => {
        if(error.message === "API request failed") {
            show_message(register_message,"無法連接伺服器，請稍後再試","popup__message--error");
        }
        if(error.message === "Has already been registered") {
            show_message(register_message,"此Email已註冊過，請改使用其他Email","popup__message--error");
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

    console.log(typeof login_email.value) //!!DEBUG用
    console.log(typeof login_password.value) //!!DEBUG用

    fetch("/api/user/auth",{
        method:"PUT",
        headers: {"Content-Type":"application/json"},
        body:JSON.stringify({
            email:login_email.value,
            password:login_password.value
        })
    })
    .then(response => {
        if (response.status===500){throw new Error("API request failed")}
        if (response.status===400){throw new Error("Email or password incorrect")} 
        if (response.status===422){throw new Error("Validation failed")}
        if (response.ok){return response.json()} //!!這裡感覺可以在優化
    })
    .then(data => {
        
        localStorage.setItem('token',data.token)
        show_message(login_message,"登入成功！\n(兩秒後將自動刷新頁面）","popup__message--success");

        //> 在登入成功後，自動刷新當前頁面
        setTimeout(() => {  
            window.location.reload(); 
        }, 2000);

    })
    .catch(error => {

        if(error.message === "API request failed") {
            show_message(login_message,"無法連接伺服器，請稍後再試","popup__message--error");
        }
        if(error.message === "Email or password incorrect") {
            show_message(login_message,"電子郵件或密碼錯誤，請再次確認","popup__message--error");
        }
        if(error.message === "Validation failed") {
            show_message(login_message,"輸入格式有誤，請注意電子郵件格式","popup__message--error");
        }
        console.error(error)
    })

}