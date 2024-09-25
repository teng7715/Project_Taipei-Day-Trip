from fastapi.responses import JSONResponse 


# >函式：用來『回傳訂單已成立等訂單資料，與付款狀態』
def success_create_order_response(data):
	response={
		"data": {
			"number": data["order_number"],
			"payment": {
			"status": data["payment_status"],
			"message": data["payment_message"]
			}
		}
	}
	return JSONResponse(content=response,status_code=200,media_type="application/json; charset=utf-8")



# >函式：『沒有此筆訂單資料時』，回傳None
def no_order_data_response():
	response={"data":None}
	return JSONResponse(content=response,status_code=200,media_type="application/json; charset=utf-8")



# >函式：『有此筆訂單資料時』，回傳訂單資訊
def success_one_order_data_response(order_data):
	response={
		"data": {
			"number": order_data["number"],
			"price": order_data["price"],
			"trip": {
			"attraction": {
				"id": order_data["id"],
				"name": order_data["name"],
				"address": order_data["address"],
				"image": order_data["image"]
			},
			"date": order_data["order_date"].isoformat(),
			"time": order_data["order_time"]
			},
			"contact": {
			"name": order_data["contact_name"],
			"email": order_data["contact_email"],
			"phone": order_data["contact_phone"]
			},
			"status": order_data["paid"]
		}
	}
	return JSONResponse(content=response,status_code=200,media_type="application/json; charset=utf-8")