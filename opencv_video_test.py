# -*- coding: utf-8 -*-
"""
Created on Fri Oct  8 14:43:02 2021

@author: User
"""

import numpy as np
import cv2
import os
import sys
from sys import platform

fileName = "push_up_1.MOV"
front_fileName = fileName.split('.', 1)[0]

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
params["write_json"] = "data/output_jsons/" + front_fileName + "/"
params["display"] = 0

try:
    # Starting OpenPose
    opWrapper = op.WrapperPython()
    opWrapper.configure(params)
    opWrapper.start()
    # Process Image
    datum = op.Datum()
    cap = cv2.VideoCapture("./data/videos/"+fileName)
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
            datum.cvInputData = frame
            datum.name=str(count) #for each frame the count is prefixed for the output json file name. This way we get individual file for each frame.
            opWrapper.emplaceAndPop(op.VectorDatum([datum]))

            opframe=datum.cvOutputData
            height, width, layers = opframe.shape
            if video == None:
                fourcc = cv2.VideoWriter_fourcc('M', 'P', '4', 'V')
                video = cv2.VideoWriter('./data/output_videos/output_' + front_fileName + '.mp4', fourcc, fps, (width, height))
            video.write(opframe)
            print("Frame_%d is completed."%count)
            #cv2.imshow("OpenPose 1.7.0 - Tutorial Python API", datum.cvOutputData)
            #cv2.waitKey(0)
        else:
            break
    cv2.destroyAllWindows()
    video.release()
    

except Exception as e:
    print(e)
    sys.exit(-1)

print("ALL COMPLETED!!!")