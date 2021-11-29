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
from sys import platform
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
        sys.path.append('./../openpose/build/python');
        # If you run `make install` (default path is `/usr/local/python` for Ubuntu), you can also access the OpenPose/python module from there. This will install OpenPose and the python library at your desired installation path. Ensure that this is in your python path in order to use it.
        # sys.path.append('/usr/local/python')
        from openpose import pyopenpose as op
except ImportError as e:
    print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
    raise e
    
# Custom Params (refer to include/openpose/flags.hpp for more parameters)
params = dict()
params["model_folder"] = "./../openpose/models/"
params["write_json"] = "data/output_jsons/" + front_fileName + "/"
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

#df1 = pd.DataFrame([])
#df1 = load_json_keypoints("./data/output_jsons/output_json_1/1_keypoints.json")
df1 = load_json_keypoints("./data/output_jsons/mypose_2.jpg/0_keypoints.json")
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
            start = time.time()
            vframe = cv2.rotate(vframe, cv2.ROTATE_90_CLOCKWISE)            
            datum.cvInputData = vframe
            opWrapper.emplaceAndPop(op.VectorDatum([datum]))
            opframe=datum.cvOutputData
            end = time.time()
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
            start2 = time.time()
            ret, buffer = cv2.imencode('.jpg', opframe)            
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            end2 = time.time()
            print("camera1:%f"%(end-start))
            print("camera2:%f"%(end2-start2))
     

def get_output_video(fileName):  #傳入原檔案名(無骨架)
    front_fileName = fileName.split('.', 1)[0]
    
    #影片輸出
    while True:
        cap = cv2.VideoCapture("./data/output_videos/output_" + front_fileName + ".mp4")
        count = 1
        while (cap.isOpened()):
            print(count)
            global df1
            df1 = load_json_keypoints('./data/output_jsons/' + front_fileName + '/' + str(count) + '_keypoints.json')
            #global keypoints_list
            #df1 = keypoints_list[count - 1]
            '''
            df2 = load_json_keypoints("./data/output_jsons/output_json_1/1_keypoints.json")
            global cmp 
            cmp = str(compareRatio(df1, df2))
            '''
            success, vframe = cap.read()
            if not success:
                break
            else:
                #flipframe = cv2.flip(opframe, 1)
                start = time.time()
                ret, buffer = cv2.imencode('.jpg', vframe)       
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                end = time.time()
                print("video:%f"%(end-start))
                count = count + 1
    
@app.route('/get_ratio', methods=['GET'])
def get_ratio():        
    return cmp

@app.route('/get_app_ratio', methods=['POST', 'GET'])
def get_scene():
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
    keypoints, image = catch_keypoints(file_name)
        

@app.route('/camera_feed')
def camera_feed():
    #接收鏡頭路由
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/video_feed')
def video_feed():
    #接收影片路由
    return Response(get_output_video('VIDEO0068.mp4'), mimetype='multipart/x-mixed-replace; boundary=frame')

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

@app.route('/')
def index():
   return render_template('html/index.html', suggestions=cmp)

if __name__ == '__main__':
    torch.cuda.empty_cache()
    app.run(debug=False, host='0.0.0.0', port=3000)