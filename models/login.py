from models.hash_and_verify import authenticate_user, create_access_token


def login(login_request):
    try:
        
        # >將使用者輸入的資料送入驗證用的函式，並取得回傳值。驗證成功回傳使用者資訊，失敗則為None
        authenticate_result=authenticate_user(login_request.email,login_request.password)
        
        # >驗證失敗，回傳"Authenticate_fail"
        if not authenticate_result:
            return "Authenticate_fail"
        
        # >驗證成功，則將『使用者姓名』跟『使用者Email』資料，做為參數傳入產生Token的函式中去加密
        token=create_access_token({"name":authenticate_result[1],"email":authenticate_result[2]})
        
        return token
    
    except Exception as e:
        raise e