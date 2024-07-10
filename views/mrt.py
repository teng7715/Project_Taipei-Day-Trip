from fastapi.responses import JSONResponse


# >函式：處理『捷運站資料』，要『回傳給前端』的資料內容
def success_mrts_response(data):
    response={"data":data}
    return JSONResponse(content=response, status_code=200, media_type="application/json; charset=utf-8")
