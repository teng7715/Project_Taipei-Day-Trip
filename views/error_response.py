from fastapi.responses import JSONResponse 


# >函式：用來『回傳錯誤訊息』的通用格式
def error_response(message,code_num):
    response={
			"error":True,
			"message":message
	}
    return JSONResponse(content=response, status_code=code_num, media_type="application/json; charset=utf-8")