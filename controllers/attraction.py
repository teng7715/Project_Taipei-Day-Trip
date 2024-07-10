from fastapi import APIRouter
from models.get_attractions import get_attractions
from models.get_one_attraction import get_one_attraction
from views.attraction import success_attractions_response, success_one_attraction_response
from views.error_response import error_response


router=APIRouter(tags=['Attraction'])


# >Attraction API
@router.get("/api/attraction/{attractionId}")
async def get_attractions_endpoint(attractionId:int):
	try:
		data=get_one_attraction(attractionId)
		return success_one_attraction_response(data)
	
	except ValueError as e:
		return error_response(str(e),400)
	except Exception as e:
		return error_response(str(e),500)



@router.get("/api/attractions")
async def get_attractions_endpoint(page:int=0,keyword:str=None):
	try:
		data=get_attractions(page,keyword)
		return success_attractions_response(data["next_page"],data["data"])

	except Exception as e:
		return error_response(str(e),500)