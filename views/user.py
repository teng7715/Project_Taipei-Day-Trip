from fastapi.responses import JSONResponse


# >函式：用來『回傳註冊成功』
def success_register_response():
	response={"ok":True}
	return JSONResponse(content=response,status_code=200,media_type="application/json; charset=utf-8")



# >函式：用來『回傳驗證通過後，後端生成的Token』
def success_token_response(token):
	response={"token":token}
	return JSONResponse(content=response,status_code=200,media_type="application/json; charset=utf-8")



# >函式：用來『回傳會員資料』
def success_member_data_response(id,name,email):
	response={
		"data":{
			"id": id,
			"name": name,
			"email": email
		}
	}
	return JSONResponse(content=response,status_code=200,media_type="application/json; charset=utf-8")



# >函式：用來『沒有找到此會員的資料時』，回傳None
def error_member_data_response():
	response={"data":None}
	return JSONResponse(content=response,status_code=401,media_type="application/json; charset=utf-8")