import pymysql

config = {
    "host": "localhost",
    "user": "root",
    "password": "123456",
    "db": "datademo"
}  # 连接服务器的信息

# create connection
conn = pymysql.connect(**config)  # 两个*表示是用字典解释参数(适用于有关键字的参数)，一个*表示是用元组解释(适用于无关键字的参数)

# create operator
cur = conn.cursor()

def add_user(username, password,phone,mail):
    # sql commands
    sql = "INSERT INTO users(username, passwd) VALUES ('%s','%s')" %(username,password)
    # execute(sql)
    cur.execute(sql)
    # commit
    conn.commit()  # 对数据库内容有改变，需要commit()

def is_existed(username,password):
    sql="SELECT * FROM users WHERE username ='%s' and passwd ='%s'" %(username,password)
    cur.execute(sql)
    result = cur.fetchall()
    if (len(result) == 0):
        return False
    else:
        return True
def getpasswd(username,email,phone):
    sql="SELECT passwd FROM users WHERE username ='%s' and mail ='%s' and phone='%s'" %(username,email,phone)
    cur.execute(sql)
    result = cur.fetchall()
    print(result)
    if (len(result) == 0):
        return False
    else:
        return True,result

