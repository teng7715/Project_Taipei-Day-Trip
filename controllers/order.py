from fastapi import APIRouter, Request, Depends
from fastapi.security import OAuth2PasswordBearer
from models.hash_and_verify import get_current_user
from models.pydantic import OrderRequest
from pydantic import ValidationError
from models.order import create_new_order, get_one_order_details
from views.order import success_create_order_response, no_order_data_response, success_one_order_data_response
from views.error_response import error_response


router=APIRouter(tags=['Order'])


# >創建一個OAuth2PasswordBearer實例
oauth2_schema=OAuth2PasswordBearer(tokenUrl="/api/user/auth")


# >Order API
# >根據預定行程中的資料，建立新的訂單，並串接第三方金流，完成付款程序
@router.post("/api/orders")
async def create_order_endpoint(request:Request,token:str=Depends(oauth2_schema)):
    try:
        payload=get_current_user(token)
        if payload is None:
            return error_response("無法驗證憑證，請使用者重新登入",403)
        
        # >驗證前端傳來的order資料格式
            # >驗證成功 -> 去下一步：開始將資料寫入資料庫
            # >驗證失敗 -> 回傳錯誤訊息
        
        order_raw_data=await request.json()
        
        try:
            order=OrderRequest(**order_raw_data)
        except ValidationError as e:
            return error_response(str(e),400)

        email=payload.get("email")
        result=await create_new_order(email,order)

        return success_create_order_response(result)
		
    except Exception as e:
        return error_response(str(e),500)
		


# >根據訂單編號取得訂單資訊，null 表示沒有資料
# __這隻API實際上目前沒有用到，未來如果要開發訂單查詢功能時，可能才需要使用
@router.get("/api/order/{orderNumber}") 
async def get_order(request:Request,orderNumber:str,token:str=Depends(oauth2_schema)):
    try:
        payload=get_current_user(token)
        if payload is None:
            return error_response("無法驗證憑證，請使用者重新登入",403)
        
        
        result=get_one_order_details(orderNumber)
        

        # >如果「沒有」訂單相關資料，回傳None(前端會是null)
        if not result:
            return no_order_data_response()
        
        return success_one_order_data_response(result)
    
    except Exception as e:
        return error_response(str(e),500)
