#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 12 16:59:41 2021

@author: winston
"""

# From Python
# It requires OpenCV installed for Python
import sys
import cv2
import os
from sys import platform
import argparse
from pathlib import Path
import numpy as np

def catch_keypoints(imageName):
    # 製作儲存圖片路徑
    Path("data/output_images").mkdir(parents=True, exist_ok=True)
    Path("data/output_jsons").mkdir(parents=True, exist_ok=True)
    imageDir = "data/images/" + imageName
    try:
        # Import Openpose (Windows/Ubuntu/OSX)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        try:
            # Windows Import
            if platform == "win32":
                # Change these variables to point to the correct folder (Release/x64 etc.)
                sys.path.append(dir_path + '\\openpose\\build\\python\\openpose\\Release');
                os.environ['PATH'] +=  dir_path + '\\openpose\\build\\x64\\Release;' + dir_path + '\\openpose\\build\\bin;'
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
    
        # Flags
        parser = argparse.ArgumentParser()
        parser.add_argument("--image_path", default=imageDir, help="Process an image. Read all standard formats (jpg, png, bmp, etc.).")
        parser.add_argument("--video", default=imageDir, help="Process an image. Read all standard formats (jpg, png, bmp, etc.).")
        args = parser.parse_known_args()
    
        # Custom Params (refer to include/openpose/flags.hpp for more parameters)
        params = dict()
        params["model_folder"] = "./openpose/models/"
        params["write_json"] = "data/output_jsons/" + imageName
        params["write_images"] = "data/output_images/" + imageName
    
        # Add others in path?
        for i in range(0, len(args[1])):
            curr_item = args[1][i]
            if i != len(args[1])-1: next_item = args[1][i+1]
            else: next_item = "1"
            if "--" in curr_item and "--" in next_item:
                key = curr_item.replace('-','')
                if key not in params:  params[key] = "1"
            elif "--" in curr_item and "--" not in next_item:
                key = curr_item.replace('-','')
                if key not in params: params[key] = next_item

        # Construct it from system arguments
        # op.init_argv(args[1])
        # oppython = op.OpenposePython()
    
        # Starting OpenPose
        opWrapper = op.WrapperPython()
        opWrapper.configure(params)
        opWrapper.start()
    
        # Process Image
        datum = op.Datum()
        imageToProcess = cv2.imread(args[0].image_path)
        datum.cvInputData = imageToProcess
        opWrapper.emplaceAndPop(op.VectorDatum([datum]))
    
        # Display Image
        return datum.poseKeypoints, datum.cvOutputData
        
    except Exception as e:
        print(e)
        sys.exit(-1)

def catch_video_keypoints(videoName):
    # 製作儲存圖片路徑
    if(os.path.isfile('./data/output_videos/output_' + videoName)):
        return
    Path("data/output_images").mkdir(parents=True, exist_ok=True)
    Path("data/output_jsons").mkdir(parents=True, exist_ok=True)
    Path("data/output_videos").mkdir(parents=True, exist_ok=True)
    videoDir = "data/videos/" + videoName
    front_videoName = videoName.split('.', 1)[0]
    try:
        # Import Openpose (Windows/Ubuntu/OSX)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        try:
            # Windows Import
            if platform == "win32":
                # Change these variables to point to the correct folder (Release/x64 etc.)
                sys.path.append(dir_path + '\\openpose\\build\\python\\openpose\\Release');
                os.environ['PATH'] +=  dir_path + '\\openpose\\build\\x64\\Release;' + dir_path + '\\openpose\\build\\bin;'
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
        params["write_json"] = "data/output_jsons/" + front_videoName
        params["display"] = 0
    
        try:
            # Starting OpenPose
            opWrapper = op.WrapperPython()
            opWrapper.configure(params)
            opWrapper.start()
            # Process Image
            datum = op.Datum()
            cap = cv2.VideoCapture("./data/videos/" + videoName)
            #video_output_name = "output_video.avi"
            #out = cv2.VideoCapture("./data/output_videos/" + video_output_name)
            #cap = cv2.VideoCapture(0)
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            video=None
            count=0 #PREFIX FOR JSON output file
            while (cap.isOpened()):
                count=count+1
                hasframe, frame= cap.read()
        
                if hasframe== True:
                    #frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                    datum.cvInputData = frame
                    datum.name=str(count) #for each frame the count is prefixed for the output json file name. This way we get individual file for each frame.
                    opWrapper.emplaceAndPop(op.VectorDatum([datum]))
        
                    opframe=datum.cvOutputData
                    height, width, layers = opframe.shape
                    if video == None:
                        fourcc = cv2.VideoWriter_fourcc('M', 'P', '4', 'V')
                        video = cv2.VideoWriter('./data/output_videos/output_' + front_videoName +'.mp4', fourcc, fps, (width, height))
                    video.write(opframe)
                    print("Frame_%d has been completed."%count)
                else:
                    break
            cv2.destroyAllWindows()  
            video.release()
        
        except Exception as e:
            print(e)
            sys.exit(-1)
        
        print("ALL COMPLETED!!!")
        return True
        
    except Exception as e:
        print(e)
        sys.exit(-1)


def testPrint():
    print("success")  

'''
keypoints, image = catch_keypoints("RH.JPG")
print(keypoints)
'''

result = catch_video_keypoints('video_0006.mp4')



