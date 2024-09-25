from fastapi import *
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from controllers import mrt, attraction, user, booking, order, membercentre


app=FastAPI()
app.mount("/static",StaticFiles(directory="static"),name="static")


app.include_router(mrt.router)
app.include_router(attraction.router)
app.include_router(user.router)
app.include_router(booking.router)
app.include_router(order.router)
app.include_router(membercentre.router)


# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
	return FileResponse("./static/index.html", media_type="text/html")
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
	return FileResponse("./static/attraction.html", media_type="text/html")
@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
	return FileResponse("./static/booking.html", media_type="text/html")
@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
	return FileResponse("./static/thankyou.html", media_type="text/html")
# >新增會員中心頁面
@app.get("/membercentre", include_in_schema=False)
async def membercentre(request: Request):
	return FileResponse("./static/membercentre.html", media_type="text/html")