# >故意分開寫，希望後面切分MVC好拆一點

from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import mysql.connector
from mysql.connector import pooling
import os

from pydantic import BaseModel,EmailStr,ValidationError
from passlib.context import CryptContext
import jwt
from typing import Optional
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from typing import Literal
from pydantic import ValidationError


app=FastAPI()
app.mount("/static",StaticFiles(directory="static"),name="static")


config={
    'user':"root",
    'password': os.getenv("MYSQL_PASSWORD"),
    'host':"localhost",
    'database':"Taipei_Day_Trip",
    'raise_on_warnings': True
}


cnxpool=pooling.MySQLConnectionPool(
	pool_name="mypool",
	pool_size=5,
	**config
)


SECRET_KEY=os.getenv("JWT_SECRET_KEY")
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_DAYS=7

#####分隔線#####

# >用來驗證用戶註冊資料的模型
class MemberCreate(BaseModel):
	name:str
	email:EmailStr
	password:str


# >用來驗證用戶登入資料的模型
class LoginRequest(BaseModel):
    email:EmailStr
    password:str


# >用來驗證前端傳來的Booking資料的模型：
class Booking(BaseModel):
	attractionId:int
	date:str
	time:Literal["morning","afternoon"]
	price:int

# __我目前省略沒建立JWT token 需要用的Pydantic Model，後續可以評估是不是其實應該寫才好


#####分隔線#####

# >創建一個密碼加密上下文實例
pwd_context=CryptContext(schemes=["argon2"],deprecated="auto")


# >創建一個OAuth2PasswordBearer實例
oauth2_schema=OAuth2PasswordBearer(tokenUrl="/api/user/auth")


#####分隔線#####

# >函式：能將密碼雜湊
def hash_password(password:str):
	return pwd_context.hash(password)


# >函式：能將使用者輸入的明碼，和資料庫中的雜湊密碼，透過verify方法進行比較
def verify_password(plain_password:str, hashed_password:str):

	try:
		return pwd_context.verify(plain_password, hashed_password)

	except Exception as e: 
		print(f"Password verification failed with error:{e}")


# >函式：將使用者輸入的登入資料來與資料庫中的資料比對，進行身份驗證，如確定有此會員，就回傳使用者資料
def authenticate_user(email:str,password:str):

	try:
		db=cnxpool.get_connection()
		mycursor=db.cursor()

		mycursor.execute("select id,name,email,password from member where email=%s",(email,))
		member_data=mycursor.fetchone()

		mycursor.close()
		db.close()

		if not member_data: # >如果資料庫沒有這筆帳號資料，直接回傳False
			return False

		authenticate_result=verify_password(password,member_data[3])

		if not authenticate_result: # >如果密碼不一致，回傳False
			return False
		
		return member_data  # >如果密碼一致，會回傳此帳號的相關資料 EX:(3, 'string', 'user@example.com', '$argon2id...')

	except Exception as e: 
		print(f"Authenticate user failed with error: {e}") 
		#? raise的用法記得去搞懂，以後再來真的使用


#####分隔線#####

# >函式：用來在使用者確定登入成功後，創建新TOKEN
def create_access_token(data:dict):

	try:
		to_encode=data.copy() #?copy用法記得事後紀錄
		
		# > 過期日期設定成此刻UTC標準時間＋我們設定的過期期限七天
		expire=datetime.utcnow()+timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
		
		# > 將過期時間放進去資料當中，好等等一起被加密處理
		to_encode.update({"exp":expire})

		token=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)

		return token
	
	except Exception as e:
		print(f"Error in creating access token:{e}")



# >函式：將前端傳入的Request當中的JWT token解碼，取得會員名稱與信箱後，檢查是否有該值，如果沒有，或是token無效、過期等等，拋出401 Error
def get_current_user(token:str): 

	try:

		payload=jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)  # >如果解碼成功：會得到{"name":####,"email":####,"exp":###}的資料
		name=payload.get("name")
		email=payload.get("email")

		if not name or not email:
			return None
		
		return payload

	except InvalidTokenError:
		return None


# >函式：JWT TOKEN解密後，將得到的使用者姓名與Email作為此函式的參數，進行資料庫的比對，如確實有比對到，將會員資料回傳
def authenticate_decode_jwt(name:str,email:str):

	try:

		db=cnxpool.get_connection()
		mycursor=db.cursor()

		mycursor.execute("select id,name,email from member where name=%s and email=%s",(name,email))
		member_data=mycursor.fetchone() # > 若有取得資料，會是：(4, 'string', 'GGGG@example.com')

		return member_data

	except Exception as e:
		error_response={
			"error":True,
			"message":str(e)
		}
		return JSONResponse(content=error_response,status_code=500,media_type="application/json; charset=utf-8")
	
	finally:
		mycursor.close()
		db.close()

#####分隔線#####


# >User API
# >『註冊』一個新的會員
@app.post("/api/user")
async def register(member:MemberCreate): 
	# > 處理來自前端的註冊請求。這個函數接收MemberCreate類型的數據（包含使用者的名字、電子郵件和密碼）且會進行資料型態驗證
	
	try:

		db=cnxpool.get_connection()
		mycursor=db.cursor()

		mycursor.execute("select email from member where email=%s",(member.email,))
		existing_member=mycursor.fetchone() # > 將使用者輸入的註冊email拿去資料庫比對，看是否已有資料


		# > 如果使用者註冊的帳號（信箱）已在資料庫中，也就是此信箱已被註冊過，則反回傳error訊息給前端
		if existing_member: 
			error_response={
				"error":True,
				"message":"此Email已註冊過，請改使用其他Email"
			}
			return JSONResponse(content=error_response,status_code=400,media_type="application/json; charset=utf-8")


		# > 如果使用者輸入的帳號（信箱）在資料庫中沒有註冊過，就把他註冊的密碼拿去雜湊後，連同其他資訊放入資料庫中，並回傳成功訊息給前端
		hashed_password=hash_password(member.password)

		mycursor.execute("insert into member(name,email,password) VALUES(%s,%s,%s)",(member.name,member.email,hashed_password))
		db.commit()

		success_response={
			"ok":True
		}

		return JSONResponse(content=success_response,status_code=200,media_type="application/json; charset=utf-8")

	except Exception as e:
		error_response={
			"error":True,
			"message":str(e)
		}
		return JSONResponse(content=error_response,status_code=500,media_type="application/json; charset=utf-8")
	
	finally:
		mycursor.close()
		db.close()


# >『登入』會員帳戶。驗證使用者帳號密碼，如確定有此會員，產生Token，並回傳
@app.put("/api/user/auth")
async def login(login_request:LoginRequest):

	try:
		# >將使用者輸入的資料送入驗證用的函式，並取得回傳值。驗證成功回傳使用者資訊，失敗則為None
		authenticate_result=authenticate_user(login_request.email,login_request.password)

		# >驗證失敗，回傳錯誤訊息給前端
		if not authenticate_result:
			error_response={
				"error":True,
				"message":"登入失敗，帳號密碼錯誤"
			}
			return JSONResponse(content=error_response,status_code=400,media_type="application/json; charset=utf-8")
		
		# >驗證成功，則將『使用者姓名』跟『使用者Email』資料，做為參數傳入產生Token的函式中去加密

		token=create_access_token({"name":authenticate_result[1],"email":authenticate_result[2]})
		
		success_response={
				"token":token
			}
		return JSONResponse(content=success_response,status_code=200,media_type="application/json; charset=utf-8")

	except Exception as e:
		error_response={
			"error":True,
			"message":str(e)
		}
		return JSONResponse(content=error_response,status_code=500,media_type="application/json; charset=utf-8")


# >『取得當前的會員資訊』
@app.get("/api/user/auth")
async def check_auth(token:str=Depends(oauth2_schema)):

	#?depends的用法可能要做筆記跟多看幾遍，每次都卡卡女神
	#?反正這邊的意思是：token這個格式是字串的參數，不是直接從呼叫函式時的參數傳入，而是通過 Depends從oauth2_schema中獲得的（也就是oauth2_schema自動解析請求中的Authorization header後，取得的JWT）

	payload=get_current_user(token) # >如果解碼成功：會得到{"name":####,"email":####,"exp":###}的資料

	# >如果解碼失敗，回傳401 Error Message
	if payload is None:
		error_response={
			"error":True,
			"message":"無法驗證憑證"
		}
		return JSONResponse(content=error_response,status_code=401,media_type="application/json; charset=utf-8")

	name=payload.get("name")
	email=payload.get("email")

	# >將解碼後的會員姓名跟信箱拿去與資料庫比對，取得會員資料
	member_data=authenticate_decode_jwt(name,email)

	
	# > 與資料庫驗證後，確實有此會員，則回傳會員資料
	if member_data:	
		success_response={
			"data":{
            	"id": member_data[0],
            	"name": member_data[1],
            	"email": member_data[2]
        	}
		}
		return JSONResponse(content=success_response,status_code=200,media_type="application/json; charset=utf-8")
	else:
		# >如果沒有找到此會員的資料，回傳None
		none_response={"data":None}
		return JSONResponse(content=none_response,status_code=401,media_type="application/json; charset=utf-8")


#####分隔線#####

# >Booking API
# >建立新的預定行程
@app.post("/api/booking")
async def create_booking(request:Request,token:str=Depends(oauth2_schema)): # >API接收使用者的Token跟預定資料

	try:
		# >1. 先透過取得的Token驗證身份(確認是否登入)
			# >如果解碼成功：會得到回傳值：{"name":####,"email":####,"exp":###}
			# >如果解碼失敗，回傳403 Error Message，表示沒有登入或登入已過期等等狀態

		payload=get_current_user(token)

		if payload is None:
			error_response={
				"error":True,
				"message":"無法驗證憑證，請使用者重新登入"
			}
			return JSONResponse(content=error_response,status_code=403,media_type="application/json; charset=utf-8")
		

		# >2. 驗證前端傳來的Booking資料格式
			# >驗證成功 -> 去下一步：開始將資料寫入資料庫
			# >驗證失敗 -> 回傳錯誤訊息

		booking_data=await request.json()

		try:

			# ?這串結合pydantic的用法，包含錯誤寫法記得記錄下來
			# ?「字典解構」的用法做筆記！

			booking=Booking(**booking_data) 

		except ValidationError as e:
			error_response={
				"error": True,
                "message": str(e)
			}
			return JSONResponse(content=error_response,status_code=400,media_type="application/json; charset=utf-8")


		# >3. 透過Token中的信箱資訊，取得member_id後，檢查此會員在購物車表中，是否已經有資料
			# >已有資料：將使用者的預約資料做Update!
			# >沒有資料：將使用者的預約資料直接按照格式寫入資料庫
		# >4. 寫入資料庫後，回傳對應的正確訊息
		
		db=cnxpool.get_connection()
		mycursor=db.cursor()


		email=payload.get("email")
		mycursor.execute("select id from member where email=%s",(email,))
		member_id=mycursor.fetchone() # >透過Token中的信箱資訊，取得此會員的id

		mycursor.execute("select * from cart where member_id=%s",(member_id[0],))
		member_reserv=mycursor.fetchone() # >用會員id，取得此會員先前的預約資訊，沒有則是None

		# > 如果先前有預約資料，更新資訊
		if member_reserv:

			update_query="""
			update cart
			set attraction_id=%s,
				reservation_date=%s,
				reservation_time=%s,
    			price=%s
			where member_id=%s;
			"""

			update_values=(
				booking.attractionId,
				booking.date,
            	booking.time,
            	booking.price,
				member_id[0]
			)

			mycursor.execute(update_query,update_values)
			db.commit()
		
		# >如果先前沒有預約資料，直接寫入
		if not member_reserv:

			insert_query="""
			insert into cart(member_id,attraction_id,reservation_date,reservation_time,price) 
			values(%s,%s,%s,%s,%s)
			"""

			booking_values=(
				member_id[0],
				booking.attractionId,
				booking.date,
				booking.time,
				booking.price
			)

			mycursor.execute(insert_query,booking_values)
			db.commit()

		mycursor.close()
		db.close()

		success_response={
			"ok":True
		}
		return JSONResponse(content=success_response,status_code=200,media_type="application/json; charset=utf-8")

	except Exception as e:
		error_response={
			"error":True,
			"message":str(e)
		}
		return JSONResponse(content=error_response,status_code=500,media_type="application/json; charset=utf-8")


# >取得尚未確定下單的預定行程（也就是使用者點擊右上角預定行程時）
@app.get("/api/booking") 
async def get_booking(token:str=Depends(oauth2_schema)): 

	try:
		# >1. 先透過取得的Token驗證身份(確認是否登入)
			# >如果解碼成功：會得到回傳值：{"name":####,"email":####,"exp":###}
			# >如果解碼失敗，回傳403 Error Message，表示沒有登入或登入已過期等等狀態

		payload=get_current_user(token)

		if payload is None:
			error_response={
				"error":True,
				"message":"無法驗證憑證，請使用者重新登入"
			}
			return JSONResponse(content=error_response,status_code=403,media_type="application/json; charset=utf-8")

		# >2. 透過Token中的email資訊，取得使用者預定的景點資料並回傳

		db=cnxpool.get_connection()
		mycursor=db.cursor()

		email=payload.get("email")
		insert_query="""
		select
			attraction.id,
			attraction.name,
			attraction.address,
			(select image from url where url.attraction_id=attraction.id order by id limit 1),
			cart.reservation_date,
			cart.reservation_time,
			cart.price
		from cart
		inner join member on cart.member_id=member.id
		inner join attraction on cart.attraction_id=attraction.id
		where member.email=%s;
		"""
		# ?子查詢的部分做筆記起來

		mycursor.execute(insert_query,(email,))
		booking_data=mycursor.fetchone() # >如果沒有預定資料，會是None(前端收到null)，有的話則是類似：(22, '袖珍博物館', '臺北市中山區建國北路1段96號B1', datetime.date(2024, 7, 1), 'morning', 2000, 'pic/11000762.jpg')

		mycursor.close()
		db.close()

		# > 3.將取得到的購物車資料回傳給前端

		# >如果購物車裡「沒有」資料，回傳None(前端會是null)
		if not booking_data:
			success_response={"data":None}
			return JSONResponse(content=success_response,status_code=200,media_type="application/json; charset=utf-8")


		# >如果購物車裡「有」資料
		success_response={
			"data":{
				"attraction":{
					"id":booking_data[0],
					"name":booking_data[1],
					"address":booking_data[2],
					"image":booking_data[3],
				},
				"date":booking_data[4].isoformat(),
				"time":booking_data[5],
				"price":booking_data[6]
			}
		}
		return JSONResponse(content=success_response,status_code=200,media_type="application/json; charset=utf-8")

	except Exception as e:
		error_response={
			"error":True,
			"message":str(e)
		}
		return JSONResponse(content=error_response,status_code=500,media_type="application/json; charset=utf-8")


# >刪除目前的預定行程
@app.delete("/api/booking") 
async def delete_booking(token:str=Depends(oauth2_schema)):
	 
	try:

		# >1. 先透過取得的Token驗證身份(確認是否登入)
			# >如果解碼成功：會得到回傳值：{"name":####,"email":####,"exp":###}
			# >如果解碼失敗，回傳403 Error Message，表示沒有登入或登入已過期等等狀態

		payload=get_current_user(token)

		if payload is None:
			error_response={
				"error":True,
				"message":"無法驗證憑證，請使用者重新登入"
			}
			return JSONResponse(content=error_response,status_code=403,media_type="application/json; charset=utf-8")


		# >2. 透過Token中的email資訊，取得使用者預定的景點資料，並刪除
		
		db=cnxpool.get_connection()
		mycursor=db.cursor()

		email=payload.get("email")
		delete_query="""  
		delete cart from cart   # ?這邊記得多看幾次，反正delete cart，表示要從cart表格中刪除資料，from cart表示操作的主要表格是 cart
		inner join member on member.id=cart.member_id
		where member.email=%s;
		"""

		mycursor.execute(delete_query,(email,))
		db.commit()

		mycursor.close()
		db.close()

		success_response={
			"ok":True
		}
		return JSONResponse(content=success_response,status_code=200,media_type="application/json; charset=utf-8")

	except Exception as e:
		error_response={
			"error":True,
			"message":str(e)
		}
		return JSONResponse(content=error_response,status_code=500,media_type="application/json; charset=utf-8")



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


# >Attraction API
@app.get("/api/attractions")
async def get_attractions(request:Request,page:int=0,keyword:str=None):

	try:
		db=cnxpool.get_connection()
		mycursor=db.cursor()

		# >先處理圖片URL的資料，再跑判斷式，因為無論有沒有keyword查詢，都需要用到
		mycursor.execute("select attraction.id,url.image from url inner join attraction on attraction.id=url.attraction_id order by attraction.id")
		image_datas=mycursor.fetchall() # >裡面的資料是 [(1,'https:000848.jpg'),....]

		image_grouped_data={}  # >裡面的資料，經過下面的迴圈後，會是{"1": ["https:...","https:..."], "2": ["https:...","https:..."]...}

		for key,url in image_datas:
			if key not in image_grouped_data:
				image_grouped_data[key]=[]
			image_grouped_data[key].append(url)

		offset=page*12

		if keyword==None or keyword=="":  # >如果今天只需要針對頁碼做搜尋

			mycursor.execute("select attraction.id,attraction.name,attraction.category,attraction.description,attraction.address,attraction.transport,station.mrt,attraction.lat,attraction.lng from attraction inner join station on attraction.station_id=station.id order by attraction.id limit %s,12",(offset,))
			attraction_datas=mycursor.fetchall() 	# >裡面的資料是[(1, '新北投溫泉區', '養生溫泉'...),(2, '大稻埕碼頭',...)...]
			attraction_datas_list=[list(data) for data in attraction_datas] # >attraction_datas裡面的資料需要轉換成list格式，我們才能在裡面新增資料，加上他們的景點照片


			column_names=[desc[0] for desc in mycursor.description] # >裡面的資料是['id', 'name', 'category', 'description', ...] 
			column_names.append("images")


			for attraction in attraction_datas_list:  # >用迴圈，在每個景點列表的最後方，加上他的景點照片資料
				attraction.append(image_grouped_data[attraction[0]])
			
			cleaned_data=[dict(zip(column_names,attraction)) for attraction in attraction_datas_list]
			
			mycursor.execute("select count(id) from attraction")
			attraction_count=mycursor.fetchone()[0] # >印出來的會是Tuple-->(58,)這種形式，所以需要[0]
	

		else:  # >如果今天想要搜尋keyword

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

		
		#++後續記得優化，改成用13去處理下面的邏輯
		if attraction_count%12==0: # >如果景點數量能被12整除 EX:景點有48個，除12=4，其實在page3時，next_page就要是None了

			page_num=attraction_count/12-1
			if page < page_num:
				next_page=page+1
			else:
				next_page=None 
		
		else:
			page_num=attraction_count//12 # >如果景點數量不能被12整除，以58為例，計算後會是4，表示page0.1.2.3頁時，nextPage都要有數字

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

	finally:
		mycursor.close()
		db.close()


@app.get("/api/attraction/{attractionId}")
async def get_attraction(request:Request,attractionId:int):

	try:
		db=cnxpool.get_connection()
		mycursor=db.cursor()

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

	finally:
		mycursor.close()
		db.close()


# >MRT Station API
@app.get("/api/mrts") 
async def get_mrts(request:Request):

	try:
		db=cnxpool.get_connection()
		mycursor=db.cursor()

		mycursor.execute("select station.mrt,count(*) as num_station_with_attraction from attraction inner join station on attraction.station_id=station.id group by station.mrt order by num_station_with_attraction DESC")
		data=mycursor.fetchall()  # >data裡的內容為[('新北投', 6), ('關渡', 4), ('劍潭', 4),....]等等透過Mysql已幫忙排序的資料
		

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
	
	finally:
		mycursor.close()
		db.close()