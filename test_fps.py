# -*- coding: utf-8 -*-
"""
Created on Wed Oct 27 22:55:24 2021

@author: User
"""
'''
import cv2
# current camera
cap = cv2.VideoCapture('./data/videos/push_up_1.MOV')
count = 0
while (cap.isOpened()):
    ret, frame = cap.read()
    cv2.imshow('frame', frame)
    key = cv2.waitKey(1)
    # ESC
    if key == 27:
       break
    count = count + 1
    print(count)
cap.release()
cv2.destroyAllWindows()
'''

import torch

print(torch.cuda.is_available())
print(torch.backends.cudnn.is_available())
print(torch.cuda.device_count())
print(torch.cuda.get_device_name(0))

    