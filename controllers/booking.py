from fastapi import APIRouter, Request, Depends
from fastapi.security import OAuth2PasswordBearer
from models.hash_and_verify import get_current_user
from models.pydantic import Booking
from pydantic import ValidationError
from models.booking import create_booking_record, get_booking_record, delete_booking_record
from views.booking import success_create_booking_response, no_booking_data_response, success_booking_data_response, success_delete_booking_response
from views.error_response import error_response


router=APIRouter(tags=['Booking'])


# >創建一個OAuth2PasswordBearer實例
oauth2_schema=OAuth2PasswordBearer(tokenUrl="/api/user/auth")


# >Booking API
# >建立新的預定行程：API接收使用者的Token跟預定資料
@router.post("/api/booking")
async def create_booking_endpoint(request:Request,token:str=Depends(oauth2_schema)):
    try:
        # >1. 先透過取得的Token驗證身份(確認是否登入)
            # >如果解碼成功：會得到回傳值：{"name":####,"email":####,"exp":###}
            # >如果解碼失敗，回傳403 Error Message，表示沒有登入或登入已過期等等狀態
        
        payload=get_current_user(token)
        
        if payload is None:
            return error_response("無法驗證憑證，請使用者重新登入",403)
        
        # >2. 驗證前端傳來的Booking資料格式
            # >驗證成功 -> 去下一步：開始將資料寫入資料庫
            # >驗證失敗 -> 回傳錯誤訊息
        
        booking_raw_data=await request.json()
        
        try:
            booking=Booking(**booking_raw_data)

            # ?這串結合pydantic的用法，包含錯誤寫法記得記錄下來
			# ?「字典解構」的用法做筆記！
        
        except ValidationError as e:
            return error_response(str(e),400)


		# >3. 透過Token中的信箱資訊，取得member_id後，檢查此會員在購物車表中，是否已經有資料
			# >已有資料：將使用者的預約資料做Update!
			# >沒有資料：將使用者的預約資料直接按照格式寫入資料庫
		# >4. 寫入資料庫後，回傳對應的正確訊息
		
        email=payload.get("email")
        result=create_booking_record(email,booking)

        if result == "ok":
            return success_create_booking_response()
    
    except Exception as e:
        return error_response(str(e),500)



# >取得尚未確定下單的預定行程（也就是使用者點擊右上角預定行程時）
@router.get("/api/booking") 
async def get_booking_endpoint(token:str=Depends(oauth2_schema)):
    try:
        payload=get_current_user(token)
        if payload is None:
            return error_response("無法驗證憑證，請使用者重新登入",403)


		# >透過Token中的email資訊，取得使用者預定的景點資料並回傳
        email=payload.get("email")
        result=get_booking_record(email)


		# >如果購物車裡「沒有」資料，回傳None(前端會是null)
        if not result:
            return no_booking_data_response()


		# >如果購物車裡「有」資料
        return success_booking_data_response(result)
    
    except Exception as e:
        return error_response(str(e),500)



# >刪除目前的預定行程
@router.delete("/api/booking") 
async def delete_booking_endpoint(token:str=Depends(oauth2_schema)):
    try:
        payload=get_current_user(token)
        if payload is None:
            return error_response("無法驗證憑證，請使用者重新登入",403)
        

        email=payload.get("email")
        result=delete_booking_record(email)


        if result == "ok":
            return success_delete_booking_response()
    
    except Exception as e:
        return error_response(str(e),500)