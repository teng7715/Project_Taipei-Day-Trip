from models.database import cnxpool
from models.pydantic import Booking


def create_booking_record(email: str, booking: Booking):
    try:
        with cnxpool.get_connection() as db:
             with db.cursor() as mycursor:
                mycursor.execute("select id from member where email=%s",(email,))
                member_id=mycursor.fetchone() # >透過Token中的信箱資訊，取得此會員的id

                mycursor.execute("select * from cart where member_id=%s",(member_id[0],))
                member_reserv=mycursor.fetchone() # >用會員id，取得此會員先前的預約資訊，沒有則是None

                # > 如果先前有預約資料，更新資訊
                if member_reserv:

                    update_query="""
                    update cart
                    set attraction_id=%s,reservation_date=%s,reservation_time=%s,price=%s
                    where member_id=%s;
                    """

                    update_values=(
                        booking.attractionId,booking.date,booking.time,booking.price,
                        member_id[0]
                    )

                    mycursor.execute(update_query,update_values)

                # >如果先前沒有預約資料，直接寫入    
                if not member_reserv:

                    insert_query="""
                    insert into cart(member_id,attraction_id,reservation_date,reservation_time,price) 
                    values(%s,%s,%s,%s,%s)
                    """

                    booking_values=(member_id[0],booking.attractionId,booking.date,booking.time,booking.price)

                    mycursor.execute(insert_query,booking_values)
            
                db.commit()
                return "ok"
            
    except Exception as e:
        raise e



def get_booking_record(email: str):
    try:
        with cnxpool.get_connection() as db:
            with db.cursor(dictionary=True) as mycursor:
                insert_query="""
                select
                    attraction.id,
                    attraction.name,
                    attraction.address,
                    (select image from url where url.attraction_id=attraction.id order by id limit 1) as image,
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
                booking_data=mycursor.fetchone()
                # >如果沒有預定資料，會是None(前端收到null)，有的話則是類似：(22, '袖珍博物館', '臺北市中山區..', datetime.date(2024, 7, 1), 'morning', 2000, 'pic/11000762.jpg')

                return booking_data

    except Exception as e:
        raise e



def delete_booking_record(email: str):
    try:
        with cnxpool.get_connection() as db:
            with db.cursor() as mycursor:

                # ?這邊記得多看幾次，反正delete cart，表示要從cart表格中刪除資料，from cart表示操作的主要表格是 cart
                delete_query="""  
                delete cart from cart   
                inner join member on member.id=cart.member_id
                where member.email=%s;
                """

                mycursor.execute(delete_query,(email,))
                db.commit()
                return "ok"

    except Exception as e:
        raise e
