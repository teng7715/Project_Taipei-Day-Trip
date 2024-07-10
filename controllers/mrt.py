from fastapi import APIRouter
from models.get_mrts import get_mrts
from views.mrt import success_mrts_response
from views.error_response import error_response


router=APIRouter(tags=['MRT Station'])


# >MRT Station API
@router.get("/api/mrts") 
async def get_mrts_endpoint():
	try:
		data=get_mrts()
		return success_mrts_response(data)
		
	except Exception as e:
		return error_response(str(e),500)