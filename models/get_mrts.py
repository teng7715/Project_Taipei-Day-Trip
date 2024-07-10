from models.database import cnxpool


def get_mrts():
    try:
        with cnxpool.get_connection() as db:
            with db.cursor() as mycursor:

                select_query="""
                select station.mrt,count(*) as num_station_with_attraction 
                from attraction 
                inner join station on attraction.station_id=station.id 
                group by station.mrt order by num_station_with_attraction DESC
                """

                mycursor.execute(select_query)
                data=mycursor.fetchall()  
                # > data裡的內容為[('新北投', 6), ('關渡', 4),....]，Mysql已幫忙排序資料

                cleaned_data=[station[0] for station in data]

                return cleaned_data
       
    except Exception as e:
        raise e