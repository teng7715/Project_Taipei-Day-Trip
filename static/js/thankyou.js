import { render_signout_button } from "./popup.js"
import { navbar_check_auth } from "./check_auth.js"





let order_number=document.querySelector("#order_number");
let url=new URL(window.location.href);
let number=url.searchParams.get("number");

order_number.innerText=number;


// ++這邊目前先這樣簡單處理，但要不要項預約頁一樣驗證身份在BLABLBLA的，可以再想想
document.addEventListener("DOMContentLoaded",function(){
    // >頁面載入時，要檢查使用者狀態
    navbar_check_auth()
})
