from models.database import cnxpool
from models.hash_and_verify import hash_password


def register(member): 
    try:
        with cnxpool.get_connection() as db:
            with db.cursor() as mycursor:

                # > 將使用者輸入的註冊email拿去資料庫比對，看是否已有資料
                mycursor.execute("select email from member where email=%s",(member.email,))
                existing_member=mycursor.fetchone()


                # > 如果使用者註冊的帳號（信箱）已在資料庫中，也就是此信箱已被註冊過，回傳"Already_registered"訊息給前端
                if existing_member: 
                    return "Already_registered"

                # > 如果使用者輸入的帳號（信箱）在資料庫中沒有註冊過，就把他註冊的密碼拿去雜湊後，連同其他資訊放入資料庫中，並回傳成功訊息給前端
                hashed_password=hash_password(member.password)

                mycursor.execute("insert into member(name,email,password) VALUES(%s,%s,%s)",(member.name,member.email,hashed_password))
                db.commit()

                return "ok"
            
    except Exception as e:
        raise e