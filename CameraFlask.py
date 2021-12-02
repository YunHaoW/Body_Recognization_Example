#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''from flask import Flask, render_template, Response
import cv2

app = Flask(__name__)
camera = cv2.VideoCapture(0)

def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=3000)這裡的code是測試用'''
#===============================================================================
from flask import Flask, render_template, Response, jsonify, request
import cv2
import numpy as np
import os
import sys
import time
import pandas as pd
import torch
import pyodbc
import json
import random
import io
from PIL import Image
from flask import Flask, jsonify, request
from flask_cors import cross_origin
from flask_mail import Mail
from flask_mail import Message
from sys import platform
from threading import Thread
#from numba import jit
from catch_keypoints import catch_keypoints, catch_video_keypoints
from similarity import load_json_keypoints, load_np_ndarray, compareRatio

app = Flask(__name__)
camera = cv2.VideoCapture(0)
fileName = "test.mp4"
front_fileName = fileName.split('.', 1)[0]

# Import Openpose (Windows/Ubuntu/OSX)
dir_path = os.path.dirname(os.path.realpath(__file__))
try:
    # Windows Import
    if platform == "win32":
        # Change these variables to point to the correct folder (Release/x64 etc.)
        sys.path.append(dir_path + '\\openpose\\build\\python\\openpose\\Release');
        os.environ['PATH'] +=  dir_path + '\\openpose\\build\\x64\\Release;' + dir_path + '\\openpose\\build\\bin;'
        #torch.cuda.set_device(1)
        #available_gpus = [torch.cuda.device(i) for i in range(torch.cuda.device_count())]
        #print(available_gpus)
        #os.environ["CUDA_VISIBLE_DEVICES"]='0'
        print(torch.cuda.is_available())
        print(torch.cuda.device_count())
        #print(torch.cuda.get_device_name(0))
        import pyopenpose as op
    else:
        # Change these variables to point to the correct folder (Release/x64 etc.)
        sys.path.append('./openpose/build/python');
        # If you run `make install` (default path is `/usr/local/python` for Ubuntu), you can also access the OpenPose/python module from there. This will install OpenPose and the python library at your desired installation path. Ensure that this is in your python path in order to use it.
        # sys.path.append('/usr/local/python')
        from openpose import pyopenpose as op
except ImportError as e:
    print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
    raise e
    
# Custom Params (refer to include/openpose/flags.hpp for more parameters)
params = dict()
params["model_folder"] = "./openpose/models/"
#params["write_json"] = "data/output_jsons/" + front_fileName + "/"
#params["write_images"] = "data/output_images/" + front_fileName + "/"
params["display"] = 0

# Starting OpenPose
opWrapper = op.WrapperPython()
opWrapper.configure(params)
opWrapper.start()
# Process Image
datum = op.Datum()

opframe = None

#####################
#比較的動作
fileName1 = "push_up_1.MOV"
global videoName 
videoName = ""

#df1 = pd.DataFrame([])
#df1 = load_json_keypoints("./data/output_jsons/output_json_1/1_keypoints.json")
df1 = load_json_keypoints("./data/output_jsons/RH.JPG/0_keypoints.json")
'''
keypoints_list = []
front_fileName = "VIDEO0068"
if len(keypoints_list) == 0:
    DIR = './data/output_jsons/' + front_fileName
    frame_amount = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])
    for i in range(1, frame_amount + 1):
        keypoints_list.append(load_json_keypoints(DIR + '/' + str(i) + '_keypoints.json'))
    print("Completed")
'''    
        
#鏡頭的data frame
df2 = pd.DataFrame([])

#相似度
cmp = "0"


def gen_frames():
    #鏡頭輸出
    while True:
        success, vframe = camera.read()
        if not success:
            break
        else:
            #start = time.time()
            vframe = cv2.rotate(vframe, cv2.ROTATE_90_CLOCKWISE)            
            datum.cvInputData = vframe
            opWrapper.emplaceAndPop(op.VectorDatum([datum]))
            opframe=datum.cvOutputData
            #end = time.time()
            '''
            print(datum.poseKeypoints)
            print("===================================")
            '''
            
            if datum.poseKeypoints is not None:
                df2 = load_np_ndarray(datum.poseKeypoints)
                print("=======================================")
                # print("相似度為"+str(compareRatio(df1, df2)))
                #print(df2)
                print("=======================================")
                global cmp
                cmp = str(compareRatio(df1, df2))
                    
            #flipframe = cv2.flip(opframe, 1)
            #start2 = time.time()
            ret, buffer = cv2.imencode('.jpg', opframe)            
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            #end2 = time.time()
            #print("camera1:%f"%(end-start))
            #print("camera2:%f"%(end2-start2))
     

def get_output_video(fileName):  #傳入原檔案名(無骨架)
    front_fileName = fileName.split('.', 1)[0]
    print("目前播放"+fileName)
    #影片輸出
    while True:
        cap = cv2.VideoCapture("./data/output_videos/output_" + front_fileName + ".mp4")
        count = 1
        startTime = time.time()
        while (cap.isOpened()):
            
            global df1
            df1 = load_json_keypoints('./data/output_jsons/' + front_fileName + '/' + str(count) + '_keypoints.json')
            if df1.empty:
                break;
            
            
            #global keypoints_list
            #df1 = keypoints_list[count - 1]
            '''
            df2 = load_json_keypoints("./data/output_jsons/output_json_1/1_keypoints.json")
            global cmp 
            cmp = str(compareRatio(df1, df2))
            '''
            success, vframe = cap.read()
            nowTime = time.time()
            #if (int(nowTime - startTime)) > fpsLimit:
            if not success:
                break
            else:
            #elif count % 2 == 1:
                #flipframe = cv2.flip(opframe, 1)
                #start = time.time()
                ret, buffer = cv2.imencode('.jpg', vframe)       
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                #end = time.time()
                #print("video:%f"%(end-start))
                startTime = time.time() # reset time
            count = count + 1

@app.route('/get_ratio', methods=['GET'])
def get_ratio():        
    return cmp

@app.route('/camera_feed')
def camera_feed():
    #接收鏡頭路由
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed', methods=['POST', 'GET'])
def video_feed():
    #接收影片路由 
    if(videoName != ""):
        return Response(get_output_video(videoName), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/upload/video', methods=['POST'])
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

@app.route('/app/camera_feed', methods=['POST', 'GET'])
@cross_origin()
def app_camera_feed():
    try:
        # 接收檔案
        upload_file = request.files['file']
        # 獲取檔案名
        file_name = upload_file.filename
        # 檔案路徑
        file_path="data/images"
            
    except:
        send = {"message":"upload_false", "rate":"0", "isPostSuccess":"false", "suggestion":"None"}
        return jsonify(send)
    if upload_file:
        img = upload_file.read()
        #frame = cv2.imdecode(img)
        frame = cv2.imdecode(np.fromstring(img, np.uint8), cv2.IMREAD_COLOR)
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        datum.cvInputData = frame
        opWrapper.emplaceAndPop(op.VectorDatum([datum]))
        opframe=datum.cvOutputData
        '''
        print(datum.poseKeypoints)
        print("===================================")
        '''
        
        if datum.poseKeypoints is not None:
            df2 = load_np_ndarray(datum.poseKeypoints)
            print("=======================================")
            # print("相似度為"+str(compareRatio(df1, df2)))
            #print(df2)
            print("=======================================")
            global cmp
            cmp = str(compareRatio(df1, df2))
            
    send = {"message":"hello", "rate":"0", "isPostSuccess":"false", "suggestion":"None"}
    send["rate"] = str(cmp)
    if cmp != None:
        send["isPostSuccess"] = "true"
    print("相似度為:%s"%cmp)
    return str(cmp)

@app.route('/Upload/Image', methods=['POST'])
@cross_origin()
def uploadImage():
    #init
    torch.cuda.empty_cache()
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

@app.route('/')
def index():
   return render_template('index.html', suggestions=cmp)

@app.route('/comparison/<video>')
def comparison(video):
    global videoName
    videoName = str(video)
    print("傳送參數:" + videoName)
    time.sleep(1)
    return render_template('comparison.html', suggestion=cmp)

    
def send_async_email(app, msg):
    #  下面有說明
    with app.app_context():
        mail.send(msg)
        
if __name__ == '__main__':
    torch.cuda.empty_cache()
    app.run(debug=False, host='0.0.0.0', port=3000)