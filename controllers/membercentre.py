from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from models.hash_and_verify import get_current_user
from models.membercentre import get_member_order_history
from views.membercentre import no_order_history_response, success_order_history_response
from views.error_response import error_response


router=APIRouter(tags=['Member Centre'])


# >創建一個OAuth2PasswordBearer實例
oauth2_schema=OAuth2PasswordBearer(tokenUrl="/api/user/auth")


# >用來取得歷史訂單記錄
@router.get("/api/membercentre")
async def get_member_order_history_endpoint(token:str=Depends(oauth2_schema)):
	try:
		payload=get_current_user(token)
		if payload is None:
			return error_response("無法驗證憑證，請使用者重新登入",403)
		

		email=payload.get("email")
		result=get_member_order_history(email)


		# >如果從來「沒有」歷史訂單資料，回傳None(前端會是null)
		if not result:
			return no_order_history_response()


		# >如果購物車裡「有」資料，做整理後，回傳給前端
		for item in result:
			item["date"]=item["date"].isoformat()
		
		return success_order_history_response(result)

	except Exception as e:
		return error_response(str(e),500)