from mysql.connector import pooling
import os


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