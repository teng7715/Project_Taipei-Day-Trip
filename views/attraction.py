from fastapi.responses import JSONResponse 


# >函式：處理『所有景點資料』，要『回傳給前端』的資料內容
def success_attractions_response(next_page,cleaned_data):
	response={
		"nextPage":next_page,
		"data":cleaned_data
	}
	return JSONResponse(content=response,status_code=200,media_type="application/json; charset=utf-8")



# >函式：處理『特定景點資料』，要『回傳給前端』的資料內容
def success_one_attraction_response(data):
    response={"data":data}
    return JSONResponse(content=response, status_code=200, media_type="application/json; charset=utf-8")