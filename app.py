from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
from starlette.middleware.cors import CORSMiddleware
import mysql.connector
import os


db=mysql.connector.connect(
	user="root",
	password=os.getenv("MYSQL_PASSWORD"), 
	host="localhost",
	database="Taipei_Day_Trip"
)


mycursor=db.cursor()

app=FastAPI()

##這邊同源政策的設定，到時候真的上線，要再改一下！
app.add_middleware(CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
)

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


# API
@app.get("/api/attractions")
async def get_attractions(request:Request,page:int=0,keyword:str=None):

	try:

		#先處理圖片URL的資料，再跑判斷式，因為無論有沒有keyword查詢，都需要用到
		mycursor.execute("select attraction.id,url.image from url inner join attraction on attraction.id=url.attraction_id order by attraction.id")
		image_datas=mycursor.fetchall() #裡面的資料是 [(1,'https:000848.jpg'),....]

		image_grouped_data={}  #裡面的資料，經過下面的迴圈後，會是{"1": ["https:...","https:..."], "2": ["https:...","https:..."]...}

		for key,url in image_datas:
			if key not in image_grouped_data:
				image_grouped_data[key]=[]
			image_grouped_data[key].append(url)

		offset=page*12

		if keyword==None or keyword=="":  #如果今天只需要針對頁碼做搜尋

			mycursor.execute("select attraction.id,attraction.name,attraction.category,attraction.description,attraction.address,attraction.transport,station.mrt,attraction.lat,attraction.lng from attraction inner join station on attraction.station_id=station.id order by attraction.id limit %s,12",(offset,))
			attraction_datas=mycursor.fetchall() 	#裡面的資料是[(1, '新北投溫泉區', '養生溫泉'...),(2, '大稻埕碼頭',...)...]
			attraction_datas_list=[list(data) for data in attraction_datas] #attraction_datas裡面的資料需要轉換成list格式，我們才能在裡面新增資料，加上他們的景點照片


			column_names=[desc[0] for desc in mycursor.description] #裡面的資料是['id', 'name', 'category', 'description', ...] 
			column_names.append("images")


			for attraction in attraction_datas_list:  #用迴圈，在每個景點列表的最後方，加上他的景點照片資料
				attraction.append(image_grouped_data[attraction[0]])
			
			cleaned_data=[dict(zip(column_names,attraction)) for attraction in attraction_datas_list]
			
			mycursor.execute("select count(id) from attraction")
			attraction_count=mycursor.fetchone()[0] #印出來的會是Tuple-->(58,)這種形式，所以需要[0]
	

		else:  #如果今天想要搜尋keyword

			keyword_param=f"%{keyword}%"
			mycursor.execute("select attraction.id,attraction.name,attraction.category,attraction.description,attraction.address,attraction.transport,station.mrt,attraction.lat,attraction.lng from attraction inner join station on attraction.station_id=station.id where attraction.name like %s or station.mrt like %s order by attraction.id limit %s,12",(keyword_param,keyword_param,offset))
			attraction_datas=mycursor.fetchall() 							
			attraction_datas_list=[list(data) for data in attraction_datas]

			column_names=[desc[0] for desc in mycursor.description] 		
			column_names.append("images")

			for attraction in attraction_datas_list:  						
				attraction.append(image_grouped_data[attraction[0]])

			cleaned_data=[dict(zip(column_names,attraction)) for attraction in attraction_datas_list]

			mycursor.execute("select count(attraction.id) from attraction inner join station on attraction.station_id=station.id where attraction.name like %s or station.mrt like %s",(keyword_param,keyword_param))
			attraction_count=mycursor.fetchone()[0]


		# page 0 是1-12    			limit 0,12 -->略過0筆資料後，取出12筆 
		# page 1 是13-24   			limit 12,12 -->略過12筆資料後，取出12筆
		# page 2 是25-36   			limit 24,12 -->略過24筆資料後，取出12筆
		# page 3 是37-48   			limit 36,12 -->略過36筆資料後，取出12筆
		# page 4 是49-58 (不滿12筆)  limit 48,12 -->略過48筆資料後，取出12筆(但有不滿12筆的問題嗚嗚--->好像沒差？他就是取出10筆資料)
		# page 5 NONO資料沒這麼多筆   limit 60,12 -->略過60筆資料後，取出12筆-->SQL撈出上也不會怎樣或異常，他只是會跟你說沒資料，所以也沒東西給你而已

		
		if attraction_count%12==0: #如果景點數量能被12整除 EX:景點有48個，除12=4，其實在page3時，next_page就要是None了

			page_num=attraction_count/12-1
			if page < page_num:
				next_page=page+1
			else:
				next_page=None 
		
		else:
			page_num=attraction_count//12 #如果景點數量不能被12整除，以58為例，計算後會是4，表示page0.1.2.3頁時，nextPage都要有數字

			if page < page_num:
				next_page=page+1
			else:
				next_page=None 
		

		success_response={
			"nextPage":next_page,
			"data":cleaned_data
		}

		return JSONResponse(content=success_response,status_code=200,media_type="application/json; charset=utf-8")
		

	except Exception as e:
		error_response={
			"error":True,
			"message":str(e)
		}
		return JSONResponse(content=error_response,status_code=500,media_type="application/json; charset=utf-8")


@app.get("/api/attraction/{attractionId}")
async def get_attraction(request:Request,attractionId:int):

	try:
		mycursor.execute("select id from attraction")
		attractions_id=mycursor.fetchall()
		attractions_id_list=[ id[0] for id in attractions_id]

		if attractionId > len(attractions_id_list):
			return JSONResponse(content={"error":True,"message":"查無此景點喔！"},status_code=400,media_type="application/json; charset=utf-8")

		if attractionId not in attractions_id_list:
			return JSONResponse(content={"error":True,"message":"景點編號查詢請輸入正整數！"},status_code=400,media_type="application/json; charset=utf-8")

		mycursor.execute("select attraction.id,attraction.name,attraction.category,attraction.description,attraction.address,attraction.transport,station.mrt,attraction.lat,attraction.lng from attraction inner join station on attraction.station_id=station.id where attraction.id=%s",(attractionId,))
		attraction_datas_list=list(mycursor.fetchone())

		column_names=[desc[0] for desc in mycursor.description]
		column_names.append("images")

		mycursor.execute("select url.image from url inner join attraction on attraction.id=url.attraction_id where attraction.id=%s",(attractionId,))
		image_datas=mycursor.fetchall()
		image_datas_list=[image[0] for image in image_datas]
				
		attraction_datas_list.append(image_datas_list)

		cleaned_data=dict(zip(column_names,attraction_datas_list))

		success_response={
			"data":cleaned_data
		}

		return JSONResponse(content=success_response,status_code=200,media_type="application/json; charset=utf-8")

	except Exception as e:
		error_response={
			"error":True,
			"message":str(e)
		}
		return JSONResponse(content=error_response,status_code=500,media_type="application/json; charset=utf-8")


@app.get("/api/mrts") 
async def get_mrts(request:Request):
	
	try:
		mycursor.execute("select station.mrt,count(*) as num_station_with_attraction from attraction inner join station on attraction.station_id=station.id group by station.mrt order by num_station_with_attraction DESC")
		data=mycursor.fetchall()  #data裡的內容為[('新北投', 6), ('關渡', 4), ('劍潭', 4),....]等等透過Mysql已幫忙排序的資料

		cleaned_data=[station[0] for station in data]

		success_response={
			"data":cleaned_data
		}
		return JSONResponse(content=success_response,status_code=200,media_type="application/json; charset=utf-8")

	except Exception as e:
		error_response={
			"error":True,
			"message":str(e)
		}
		return JSONResponse(content=error_response,status_code=500,media_type="application/json; charset=utf-8")
	