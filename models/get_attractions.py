from models.database import cnxpool

def get_attractions(page:int,keyword:str):
    try:
        with cnxpool.get_connection() as db:
            with db.cursor() as mycursor:

                # >先處理圖片URL的資料，再跑判斷式，因為無論有沒有keyword查詢，都需要用到
                select_query="""
                select attraction.id,url.image 
                from url inner join attraction on attraction.id=url.attraction_id order by attraction.id
                """

                mycursor.execute(select_query)
                image_datas=mycursor.fetchall() # >裡面的資料是 [(1,'https:000848.jpg'),....]

                image_grouped_data={}  # >裡面的資料，經過下面的迴圈後，會是{"1": ["https:...","https:..."], "2": ["https:...","https:..."]...}

                for key,url in image_datas:
                    if key not in image_grouped_data:
                        image_grouped_data[key]=[]
                    image_grouped_data[key].append(url)

                offset=page*12

                # >如果今天只需要針對頁碼做搜尋
                if keyword==None or keyword=="":  

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
            

                # >如果今天想要搜尋keyword
                else:  

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

                return {"next_page": next_page,"data": cleaned_data}

    except Exception as e:
        raise e