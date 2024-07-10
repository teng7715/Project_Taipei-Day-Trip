from models.hash_and_verify import get_current_user, authenticate_decode_jwt


def check_auth(token):
    try:
        payload=get_current_user(token) # >如果解碼成功：會得到{"name":####,"email":####,"exp":###}的資料

        # >如果解碼失敗，回傳"Unable to verify"
        if payload is None:
            return "Unable to verify"


        # >如果解碼成功，取得使用者姓名跟email資訊
        name=payload.get("name")
        email=payload.get("email")


        # >將解碼後的會員姓名跟信箱拿去與資料庫比對，取得會員資料
        member_data=authenticate_decode_jwt(name,email)


        # > 與資料庫驗證後，確實有此會員，則回傳會員資料
        if member_data:
            return member_data
            
        else:
            # >如果沒有找到此會員的資料，回傳None
            return "member not found"
    
    except Exception as e:
        raise e