import mysql.connector
import os
import json
import re

db=mysql.connector.connect(
    user="root",
    password=os.getenv("MYSQL_PASSWORD"),
    host="localhost",
    database="Taipei_Day_Trip"
)

mycursor=db.cursor()

# 1/ 開啟檔案
with open("taipei-attractions.json","r",encoding="utf-8") as file:
    data=json.load(file)

data=data["result"]["results"]


# 2/ 將捷運資料整理後，寫入資料庫
mrt_data=[]

for x in range(len(data)):        # 針對58筆資料，透過迴圈，將每個景點的捷運站抓出來，並在不重複的前提下，組成一個新的，紀錄捷運站站名的列表
    station=data[x]["MRT"]
    if station not in mrt_data:
        mrt_data.append(station)  # mrt_data裡，總共33筆資料，['新北投', '雙連', '士林', '劍潭'....]


for station in mrt_data:
    mycursor.execute("insert into station(mrt) values(%s)",(station,))


# 2.5/ 將每一站的資料變成字典，好讓後面景點資料可以對照，取得id數值
station_dict={} 

for x in range(len(mrt_data)):
    station_dict[mrt_data[x]]=x+1


# 3/ 將景點資料整理後，寫入資料庫
for x in range(len(data)): 
    
    name=data[x]["name"]
    category=data[x]["CAT"]
    description=data[x]["description"]

    address=data[x]["address"] 
    cleaned_address=address.replace(" ","")  # 因原始資料的地址中間有空格（臺北市  北投區中山路、光明路沿線），所以我們多一步來處理

    transport=data[x]["direction"]
    station_id=station_dict[data[x]["MRT"]]         # 這邊原本的值是是"新北投"，但透過字典station_dict比對後，取得到id數值
    lat=data[x]["latitude"]
    lng=data[x]["longitude"]

    mycursor.execute("insert into attraction(name,category,description,address,transport,station_id,lat,lng) values(%s,%s,%s,%s,%s,%s,%s,%s)",(name,category,description,cleaned_address,transport,station_id,lat,lng))

    # 4/ 將景點的照片資料整理後，寫入資料庫
    attraction_id=x+1

    images=data[x]["file"] 

    rule=re.compile(r'(https?://\S+?\.(?:jpg|png))', re.I)
    cleaned_images=rule.findall(images)  #leaned_images，會是比對後的所有網址，所形成得一個『列表』

    for image in cleaned_images:
        mycursor.execute("insert into url(attraction_id,image) values(%s,%s)",(attraction_id,image))


db.commit() 