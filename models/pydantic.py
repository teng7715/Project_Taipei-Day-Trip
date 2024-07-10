from pydantic import BaseModel, EmailStr, HttpUrl, ValidationError
from typing import Optional, Literal


# > Pydantic Models
# >驗證『用戶註冊資料』
class MemberCreate(BaseModel):
	name:str
	email:EmailStr
	password:str


# >驗證『用戶登入資料』
class LoginRequest(BaseModel):
    email:EmailStr
    password:str


# >驗證『前端傳來的Booking資料』
class Booking(BaseModel):
	attractionId:int
	date:str
	time:Literal["morning","afternoon"]
	price:int


# >驗證『前端傳來的ordeer資料』
class Attraction(BaseModel):
	id:int
	name:str
	address:str
	image:HttpUrl

class Trip(BaseModel):
	attraction:Attraction
	date:str
	time:Literal["morning","afternoon"]

class Contact(BaseModel):
	name:str
	email:EmailStr
	phone:str

class Order(BaseModel):
	price:int
	trip:Trip
	contact:Contact

class OrderRequest(BaseModel):
	prime:str
	order:Order