import { navbar_check_auth } from "./check_auth.js"


document.addEventListener("DOMContentLoaded",function(){
    // >頁面載入時，要檢查使用者狀態
    navbar_check_auth()

    let order_number=document.querySelector("#order_number");
    let url=new URL(window.location.href);
    let number=url.searchParams.get("number");

    order_number.innerText=number;

})
