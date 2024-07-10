from models.database import cnxpool


# >函式：透過Token中的email資訊，取得使用者所有歷史訂單記錄並回傳
def get_member_order_history(email:str):
	try:
		with cnxpool.get_connection() as db:
			with db.cursor(dictionary=True) as mycursor:
				select_query="""
				select
					(select image from url where url.attraction_id=attraction.id order by id limit 1) as image,
					orders.number as order_number,
					attraction.name as attraction_name,
					attraction.address,
					orders.order_date as date,
					orders.order_time as time,
					orders.contact_name,
					orders.contact_email,
					orders.contact_phone,
					orders.price,
					orders.paid as status
				from orders 
				inner join attraction on attraction.id=orders.attraction_id
				inner join member on member.id = orders.member_id
				where member.email=%s
				order by orders.time DESC
				"""

				mycursor.execute(select_query,(email,))
				order_history_data=mycursor.fetchall()
				
				return order_history_data
	
	except Exception as e:
		raise e