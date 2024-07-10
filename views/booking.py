from fastapi.responses import JSONResponse 


# >函式：用來『回傳購物車資料建立成功』
def success_create_booking_response():
	response={"ok":True}
	return JSONResponse(content=response,status_code=200,media_type="application/json; charset=utf-8")



# >函式：『沒有購物車資料時』，回傳None
def no_booking_data_response():
	response={"data":None}
	return JSONResponse(content=response,status_code=200,media_type="application/json; charset=utf-8")



# >函式：『有購物車資料時』，回傳購物車資訊
def success_booking_data_response(booking_data):
	response={
		"data":{
			"attraction":{
				"id":booking_data["id"],
				"name":booking_data["name"],
				"address":booking_data["address"],
				"image":booking_data["image"],
			},
			"date":booking_data["reservation_date"].isoformat(),
			"time":booking_data["reservation_time"],
			"price":booking_data["price"]
		}
	}
	return JSONResponse(content=response,status_code=200,media_type="application/json; charset=utf-8")



# >函式：用來『回傳購物車資料刪除成功』
def success_delete_booking_response():
	response={"ok":True}
	return JSONResponse(content=response,status_code=200,media_type="application/json; charset=utf-8")