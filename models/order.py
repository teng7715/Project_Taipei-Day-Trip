import os
from models.database import cnxpool
from datetime import datetime
import random
from models.pydantic import OrderRequest
import httpx
import asyncio


Partner_Key= os.getenv("PARTNER_KEY")


# >函式：透過 datetime 和 random 隨機產生訂單編號
def generate_order_number():

	now=datetime.now()
	timestamp=int(now.timestamp()*1000)
	random_number=random.randint(1000,9999)

	order_number=f"{timestamp}{random_number}"

	return order_number



# >函式：依據前端傳來的數據資料，1. 在資料庫中建立一條未支付的訂單記錄＋同時消除購物車中這筆資料 2. 調用 TapPay Pay By Prime API 3.將支付成功/失敗結果紀錄到資料庫
async def create_new_order(email: str, order: OrderRequest):
    try:
        with cnxpool.get_connection() as db:
             with db.cursor() as mycursor:

                mycursor.execute("select id from member where email=%s",(email,))
                member_id=mycursor.fetchone()[0] # >透過Token中的信箱資訊，取得此會員的id
                
                order_number=generate_order_number() # >透過generate_order_number取得生成的訂單編號


                # >在資料庫中建立一條未支付的訂單記錄＋同時消除購物車中這筆資料
                insert_query="""
                insert into orders
                (number, member_id, attraction_id, order_date, order_time, price, contact_name, contact_email, contact_phone)
                values(%s,%s,%s,%s,%s,%s,%s,%s,%s);
                """

                order_values=(
                    order_number,member_id, order.order.trip.attraction.id,
                    order.order.trip.date, order.order.trip.time, order.order.price,
                    order.order.contact.name, order.order.contact.email, order.order.contact.phone,
                )

                delete_query="""
                delete from cart
                where member_id=%s and attraction_id=%s and reservation_date=%s and reservation_time=%s;
                """

                delete_values=(member_id, order.order.trip.attraction.id, order.order.trip.date, order.order.trip.time)

                mycursor.execute(insert_query,order_values)
                mycursor.execute(delete_query,delete_values)
                db.commit()


                # >在創建未支付的訂單記錄後，呼叫處理TapPay Pay By Prime API的函式

                result=await process_payment(order, order_number)
                

                # >如果支付成功，將支付記錄保存到數據庫中，將訂單記錄標記為已支付，並將訂單號返回給前端。
                # >如果支付失敗，將支付記錄保存到數據庫中，保留訂單記錄為未支付以便未來操作，並將訂單號返回給前端。
		
                if result["status"]==0:
                    mycursor.execute("insert into payment(orders_number,result) values(%s,'success')",(order_number,))
                    payment_message="付款成功"
                else:
                    mycursor.execute("insert into payment(orders_number,result) values(%s,'fail')",(order_number,))
                    payment_message="付款失敗"
                db.commit()

                return {"order_number":order_number, "payment_status":result["status"], "payment_message":payment_message}

    except Exception as e:
        raise e



# >函式：連線到TapPay Pay By Prime API
async def process_payment(order:OrderRequest, order_number:str):

    tappay_url="https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"
    tappay_headers={
        "Content-Type":"application/json",
        "x-api-key": Partner_Key
    }
    
    tappay_data={
        "prime": order.prime,
        "partner_key": Partner_Key,
        "merchant_id": "teng7715_NCCC",
        "details":"Taipei-Day-Trip-Order-Test",
        "order_number":order_number,
        "amount": order.order.price, 
        "cardholder": {
            "phone_number": order.order.contact.phone,
            "name": order.order.contact.name,
            "email": order.order.contact.email
        }
    }
    
    async with httpx.AsyncClient() as client:
        response=await client.post(tappay_url, headers=tappay_headers, json=tappay_data)
        result=response.json()
    
    return result



# >函式：根據訂單編號，向後端資料庫取得訂單資訊
def get_one_order_details(orderNumber: str):
    try:
        with cnxpool.get_connection() as db:
            with db.cursor(dictionary=True) as mycursor:
                
                select_query="""
                select
                    orders.number, orders.price,
                    attraction.id, attraction.name, attraction.address,
                    (select image from url where url.attraction_id=attraction.id order by id limit 1) as image,
                    orders.order_date, orders.order_time,
                    orders.contact_name, orders.contact_email, orders.contact_phone,
                    orders.paid
                from orders inner join attraction on attraction.id=orders.attraction_id
                where orders.number=%s
                """

                mycursor.execute(select_query,(orderNumber,))
                order_data=mycursor.fetchone()

                return order_data
            
    except Exception as e:
        raise e