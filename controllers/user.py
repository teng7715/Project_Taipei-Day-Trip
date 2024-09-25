from fastapi import APIRouter, Depends
from models.pydantic import MemberCreate, LoginRequest
from models.register import register
from models.login import login
from models.check_auth import check_auth
from views.user import success_register_response, success_token_response, success_member_data_response, error_member_data_response
from views.error_response import error_response
from fastapi.security import OAuth2PasswordBearer


router=APIRouter(tags=['User'])


# >創建一個OAuth2PasswordBearer實例
oauth2_schema=OAuth2PasswordBearer(tokenUrl="/api/user/auth")


# >User API
# >『註冊』一個新的會員
@router.post("/api/user")
async def register_endpoint(member:MemberCreate):
    
	# > 處理來自前端的註冊請求。這個函數接收MemberCreate類型的數據（包含使用者的名字、電子郵件和密碼）且會進行資料型態驗證
    try:
        result=register(member)
        
        if result == "Already_registered":
            return error_response("此Email已註冊過，請改使用其他Email",400)
        if result == "ok":
            return success_register_response()
    
    except Exception as e:
        return error_response(str(e),500)



# >『登入』會員帳戶。驗證使用者帳號密碼，如確定有此會員，產生Token，並回傳
@router.put("/api/user/auth")
async def login_endpoint(login_request:LoginRequest):
    try:
        result=login(login_request)

        if result == "Authenticate_fail":
            return error_response("登入失敗，帳號密碼錯誤",400)

        return success_token_response(result)
    
    except Exception as e:
        return error_response(str(e),500)



# >『取得當前的會員資訊』
@router.get("/api/user/auth")
async def check_auth_endpoint(token:str=Depends(oauth2_schema)):

    #?depends的用法可能要做筆記跟多看幾遍，每次都卡卡女神
	#?反正這邊的意思是：token這個格式是字串的參數，不是直接從呼叫函式時的參數傳入，而是通過 Depends從oauth2_schema中獲得的（也就是oauth2_schema自動解析請求中的Authorization header後，取得的JWT）

    try:
        result=check_auth(token)

        if result == "Unable to verify":
            return error_response("無法驗證憑證",401)
        if result == "member not found":
            return error_member_data_response()
        
        return success_member_data_response(result[0],result[1],result[2])

    
    except Exception as e:
        return error_response(str(e),500)
