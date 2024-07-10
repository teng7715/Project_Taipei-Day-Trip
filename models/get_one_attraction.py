from models.database import cnxpool


def get_one_attraction(attractionId:int):
    try:
        with cnxpool.get_connection() as db:
            with db.cursor() as mycursor:

                mycursor.execute("select id from attraction")
                attractions_id=mycursor.fetchall()
                attractions_id_list=[ id[0] for id in attractions_id]


                if attractionId > len(attractions_id_list):
                    raise ValueError("查無此景點喔！")

                if attractionId not in attractions_id_list:
                    raise ValueError("景點編號查詢請輸入正整數！")


                mycursor.execute("select attraction.id,attraction.name,attraction.category,attraction.description,attraction.address,attraction.transport,station.mrt,attraction.lat,attraction.lng from attraction inner join station on attraction.station_id=station.id where attraction.id=%s",(attractionId,))
                attraction_datas_list=list(mycursor.fetchone())


                column_names=[desc[0] for desc in mycursor.description]
                column_names.append("images")


                mycursor.execute("select url.image from url inner join attraction on attraction.id=url.attraction_id where attraction.id=%s",(attractionId,))
                image_datas=mycursor.fetchall()
                

                image_datas_list=[image[0] for image in image_datas]
                        
                attraction_datas_list.append(image_datas_list)

                cleaned_data=dict(zip(column_names,attraction_datas_list))
                
                return cleaned_data

    except Exception as e:
        raise e
