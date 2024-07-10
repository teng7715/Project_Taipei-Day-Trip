import os
from models.database import cnxpool
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from jwt.exceptions import InvalidTokenError


SECRET_KEY=os.getenv("JWT_SECRET_KEY")
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_DAYS=7


# >創建一個密碼加密上下文實例
pwd_context=CryptContext(schemes=["argon2"],deprecated="auto")


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
		with cnxpool.get_connection() as db:
			with db.cursor() as mycursor:
				
				mycursor.execute("select id,name,email,password from member where email=%s",(email,))
				member_data=mycursor.fetchone()
				
				if not member_data: # >如果資料庫沒有這筆帳號資料，直接回傳False
					return False
				
				authenticate_result=verify_password(password,member_data[3])
				
				if not authenticate_result: # >如果密碼不一致，回傳False
					return False
				
				return member_data  # >如果密碼一致，會回傳此帳號的相關資料 EX:(3, 'string', 'user@example.com', '$argon2id...')

	except Exception as e: 
		print(f"Authenticate user failed with error: {e}")
		raise e



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



# >函式：將前端傳入的Request當中的JWT token解碼，取得會員名稱與信箱後，檢查是否有該值，如果沒有，或是token無效、過期等等，回傳None
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
		with cnxpool.get_connection() as db:
			with db.cursor() as mycursor:
				
				mycursor.execute("select id,name,email from member where name=%s and email=%s",(name,email))
				member_data=mycursor.fetchone() # > 若有取得資料，會是：(4, 'string', 'GGGG@example.com')
				
				return member_data

	except Exception as e:
		print(f"Error in authenticating decode jwt: {e}")