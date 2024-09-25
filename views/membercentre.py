from fastapi.responses import JSONResponse



# >函式：『沒有歷史訂單資料』時，回傳None
def no_order_history_response():
	response={"data":None}
	return JSONResponse(content=response,status_code=200,media_type="application/json; charset=utf-8")



# >函式：『回傳歷史訂單資料』
def success_order_history_response(cleaned_data):
	response={"data":cleaned_data}
	return JSONResponse(content=response,status_code=200,media_type="application/json; charset=utf-8")