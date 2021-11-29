#!/usr/bin/env python3
# coding=utf-8
# -- coding: UTF-8 --

import sys
import json
import pyodbc
#import blinker
import os
import random
import time
from flask import Flask, jsonify, request
from flask_cors import cross_origin
from flask_mail import Mail
from flask_mail import Message
from threading import Thread
#from celery import Celery
from catch_keypoints import catch_keypoints, catch_video_keypoints
from similarity import load_json_keypoints, compareRatio

app = Flask(__name__)

app.config.update(
    #  hotmail的設置
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PROT=587,
    MAIL_USE_TLS=True, 
    MAIL_USERNAME='projectar2567@gmail.com',
    MAIL_PASSWORD='-z-z-z-r-5-6-7-9'
)

mail = Mail(app)

'''
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') 
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD') 
'''
'''
print(app.config['MAIL_USERNAME'] )
print(app.config['MAIL_PASSWORD'])
'''

#底下有加@cross_origin()的路由，CORS才算有打開    
'''
代碼訊息:
    0:註冊成功
    1:已存在相同帳號email
    2:已存在相同用戶名稱
    3:與資連庫連接發生未預期錯誤
    4:該email不存在
    5:該密碼錯誤
    6:登入成功
    7:更改資料成功
    8:SQL語法發生問題
'''

@app.route('/SignUp', methods=['POST'])
@cross_origin()
def SignUp():
    
    #接收註冊表單資料
    data = json.loads(request.get_data())
    Name = data["Name"]
    Email = data["Email"]
    Passwd = data["Passwd"]
    
    print(Name)
    print(Email)
    print(Passwd)
    #連接資料庫
    server = 'arproject.database.windows.net'
    database = 'ARWorkOutDataBase'
    username = 'Ivan'
    password = 'Project110'   
    driver= '{ODBC Driver 17 for SQL Server}'
    try:
        with pyodbc.connect('DRIVER='+driver+';CHARSET=UTF8;SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                print("資料庫連接成功")     
            
            #檢查是否已存在之帳號
            #SQL指令用cursor去執行
            cursor.execute("SELECT * FROM UserData WHERE Name = ?;",(Name))
            if cursor.rowcount == 0 :
                #檢查是否已存在之email
                cursor.execute("SELECT * FROM UserData WHERE Email = ?;",(Email))
                if cursor.rowcount == 0 :
                    #註冊
                    #回傳成功訊息並分配UserID
                    cursor.execute("SELECT * FROM UserData")
                    UserID = cursor.rowcount+1  
                    #新增用戶
                    cursor.execute("INSERT INTO UserData (Name, Email, Passwd, UserID) VALUES (?, ?, ?, ?);", (Name, Email, Passwd, UserID))
                    return_message = "0"
                    print("註冊成功!")
                else:
                    return_message = "1"
                    print("email已存在!")
            else:
                return_message = "2"
                print("name已存在!")
    except Exception as ex:
        return_message = "3"
        print(ex.message)
                    
    conn.close()          
    return return_message
          
        
@app.route('/Login', methods=['POST'])  
@cross_origin()
def SignIn():
    #接收登入資料
    data = json.loads(request.get_data())
    Email = data['Email']
    Passwd = data['Passwd']
    
    server = 'arproject.database.windows.net'
    database = 'ARWorkOutDataBase'
    username = 'Ivan'
    password = 'Project110'   
    driver= '{ODBC Driver 17 for SQL Server}'
    
    try:        
        with pyodbc.connect('DRIVER='+driver+';CHARSET=UTF8;SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                print("資料庫連接成功")        
                cursor.execute("SELECT * FROM UserData WHERE Email = ?;",(Email))
                #檢查email是否存在
                if cursor.rowcount == 0 :
                    return_message = "4"
                    print("email不存在!")
                else:                
                    cursor.execute("SELECT * FROM UserData WHERE Passwd = ? AND Email = ?;",(Passwd,Email))
                    if cursor.rowcount == 0 :
                        #密碼錯了
                        return_message = "5"
                        print("密碼錯誤!")
                    else:
                        return_message = "6"
                        print("登入成功!")
    except Exception as ex:
        return_message = "3"
        print(ex.message)
    
    conn.close()
    return return_message

@app.route('/Query', methods=['POST'])  
@cross_origin()
def Query():
    #接收用戶email資料
    data = json.loads(request.get_data())
    Email = data['Email']
    
    server = 'arproject.database.windows.net'
    database = 'ARWorkOutDataBase'
    username = 'Ivan'
    password = 'Project110'   
    driver= '{ODBC Driver 17 for SQL Server}'
    
    try:        
        with pyodbc.connect('DRIVER='+driver+';CHARSET=UTF8;SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                print("資料庫連接成功")        
                cursor.execute("SELECT * FROM UserData WHERE Email = ?;",(Email))
                #檢查email是否存在
                if cursor.rowcount == 0 :                    
                    print("email不存在!")
                else:                
                   rv = cursor.fetchall()
                   payload = []
                   content = {}
                   for result in rv:
                       content = {'Name':result[0], 'Email':result[1], 'Passwd':result[2], 'UserID':result[3]}
                       #payload.append(content)
    except Exception as ex:        
        print(ex.message)
    
    conn.close()
    return jsonify(content)

@app.route('/ChangeUserData', methods=['POST'])
@cross_origin()
def ChangeUserData():
    data = json.loads(request.get_data())
    Name = data['Name']
    Email = data['Email']
    Passwd = data['Passwd']
    print(Name)
    #接受使用者變更資料請求
    
    server = 'arproject.database.windows.net'
    database = 'ARWorkOutDataBase'
    username = 'Ivan'
    password = 'Project110'   
    driver= '{ODBC Driver 17 for SQL Server}'
    
    try:        
        with pyodbc.connect('DRIVER='+driver+';CHARSET=UTF8;SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                print("資料庫連接成功")        
                try:
                    #更改姓名和密碼
                    #只更改密碼
                    if Name == None  or Name == "" :
                        cursor.execute("UPDATE UserData SET  Passwd = ? WHERE Email = ?;",(Passwd,Email))
                        
                    #只更改名字
                    elif Passwd == None or Passwd == "" :
                        cursor.execute("UPDATE UserData SET  Name = ? WHERE Email = ?;",(Name,Email))
                    #兩個都改
                    else:
                        cursor.execute("UPDATE UserData SET  Name = ?,Passwd = ? WHERE Email = ?;",(Name,Passwd,Email))
                    
                    return_message = "7"
                except Exception as ex:
                    return_message = "8"
                    print(ex.message)                
    except Exception as ex:   
        return_message = "3"
        print(ex.message)
    
    conn.close()
    return return_message

@app.route('/ChangePasswd', methods=['POST'])
@cross_origin()
def ChangePasswd():
    data = json.loads(request.get_data())
    Email = data['Email']
    Passwd = data['Passwd']
    
    #接受使用者變更資料請求
    
    server = 'arproject.database.windows.net'
    database = 'ARWorkOutDataBase'
    username = 'Ivan'
    password = 'Project110'   
    driver= '{ODBC Driver 17 for SQL Server}'
    
    try:        
        with pyodbc.connect('DRIVER='+driver+';CHARSET=UTF8;SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                print("資料庫連接成功")                 
               
                try:
                    #更改密碼
                    cursor.execute("UPDATE UserData SET  Passwd = ? WHERE Email = ?;",(Passwd,Email))
                    return_message = "7"
                except Exception as ex:
                    return_message = "8"
                    print(ex.message)                
    except Exception as ex:   
        return_message = "3"
        print(ex.message)
    
    conn.close()
    return return_message

@app.route('/SendMail', methods=['POST'])
@cross_origin()
def SendMail():
    #接收傳過來的email
    data = json.loads(request.get_data())
    Email = data['Email']
    
    #檢查email是否存在
    server = 'arproject.database.windows.net'
    database = 'ARWorkOutDataBase'
    username = 'Ivan'
    password = 'Project110'   
    driver= '{ODBC Driver 17 for SQL Server}'
    
    try:        
        with pyodbc.connect('DRIVER='+driver+';CHARSET=UTF8;SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                print("資料庫連接成功")  
                cursor.execute("SELECT * FROM UserData WHERE Email = ?;",(Email))
                if cursor.rowcount == 0 :  
                    print("email不存在!")
                    return_message = "4"    
                    return return_message 
    except Exception as ex:   
        return_message = "3"
        print(ex.message)
        return return_message        
    
    conn.close()
    #產生驗證碼
    CertificationCode = random.randint(100000,999999)
    #寄驗證信
    #  主旨
    msg_title = '逢甲大學畢業專題'
    
    #  寄件者，若參數有設置就不需再另外設置
    msg_sender = 'projectar2567@gmail.com'
    
    #  收件者，格式為list，否則報錯
    msg_recipients = []
    msg_recipients.append(Email)
    print(msg_recipients)
    
    #  郵件內容
    msg_body = '親愛的客戶您好，以下是您的驗證碼:\n\n驗證碼為'+str(CertificationCode)+'\n\nFlask Server SMTP 肢體辨識專題mail發信測試'
    
    msg = Message(msg_title,         
                  sender=msg_sender,
                  recipients=msg_recipients)
    msg.body = msg_body
    
    #  使用多線程
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return str(CertificationCode)

@app.route('/Upload/Image', methods=['POST','GET'])
@cross_origin()
def uploadImage():
    time_receive = time.time()
    try:        
        # 接收圖片
        upload_file = request.files['file']
        # 獲取圖片名
        file_name = upload_file.filename
        # 圖片路徑
        file_path="data/images"
        if upload_file:
            # 地址拼接
            file_paths = os.path.join(file_path, file_name)
            # 保存接收的圖片至指定路徑
            upload_file.save(file_paths)
            print("saving completed")
    except:
        send = {"message":"upload_false", "rate":"0", "isPostSuccess":"false", "suggestion":"None"}
        return jsonify(send)
    time_analyze = time.time()
    # 分析圖片
    print("start analyzing...")
    print(file_name)
    keypoints, image = catch_keypoints(file_name)
    print(keypoints)
    
    df1 = load_json_keypoints("data/output_jsons/mypose_1.jpg/0_keypoints.json")
    df2 = load_json_keypoints("data/output_jsons/" + file_name + "/0_keypoints.json")
    rate = compareRatio(df1, df2)
    print(str(rate))
    
    time_send =time.time()
    
    send = {"message":"hello", "rate":"0", "isPostSuccess":"false", "suggestion":"None"}
    send["rate"] = str(rate)
    if rate != None:
        send["isPostSuccess"] = "true"
    print(jsonify(send))
    print("%d, %d"%((time_analyze - time_receive), (time_send - time_analyze)))
    return jsonify(send)

@app.route('/Upload/Video', methods=['POST'])
@cross_origin()
def uploadVideo():
    # 接收檔案
    upload_file = request.files['file']
    # 獲取檔案名
    file_name = upload_file.filename
    # 檔案路徑
    file_path="data/videos"
    if upload_file:
        # 地址拼接
        file_paths = os.path.join(file_path, file_name)
        # 保存接收的影片至指定路徑
        upload_file.save(file_paths)
        print("saving completed")
    
    result = catch_video_keypoints(file_name)
    if result == True:
        return "success"
    else:
        return "The video is upload failed", 500

@app.route('/Upload/AroundImage', methods=['POST'])
@cross_origin()
def uploadImageAround():
    for i in range(4):
        # 接收圖片
        upload_file = request.files['file']
        # 獲取圖片名
        file_name = upload_file.filename
        # 獲取資料夾名
        temp = str(file_name).split("_")
        file_dir = temp[0] + "_" + temp[1]
        # 圖片路徑
        file_path="data/images" + file_dir
        if upload_file:
            # 地址拼接
            file_paths = os.path.join(file_path, file_name)
            # 保存接收的圖片至指定路徑
            upload_file.save(file_paths)
            print("Image%d have saved" % i)
    
    return "success"

@app.route('/')
def test():
    return "test"

    

def send_async_email(app, msg):
    #  下面有說明
    with app.app_context():
        mail.send(msg)


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=3000)
    sys.exit()
