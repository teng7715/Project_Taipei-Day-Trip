import {get_attractions}from "./get_attractions.js"
import { navbar_check_auth } from "./check_auth.js"


document.addEventListener("DOMContentLoaded",()=>{ //?DOMContentLoaded這個監測方法學起來
    get_attractions(0)
    navbar_check_auth() // >頁面載入時，檢查使用者狀態
})