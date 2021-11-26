#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 19 10:55:44 2021

@author: winston
"""

import json
import pandas as pd
import math

#load keypoints json as dataframe 
def load_json_keypoints(file):
    #讀入json
    try:
        with open(file) as obj:
            data = json.load(obj)
    except Exception as e:
        print(e)
    
    #篩選資料，以下為取出第一個人的keypoints
    people = data['people'][0]
    keypoints = people["pose_keypoints_2d"]
    
    #製作dataframe
    f = {"x":[], "y":[], "c":[]}
    df = pd.DataFrame(f)
    
    #keypoints中有75筆資料
    #每三筆一組，分別是x座標、y座標、檢測置信度；共25組，對應25個關鍵點
    index = 0
    for i in range(0, int(len(keypoints)/3)):
        new = pd.DataFrame.from_dict({"x": [keypoints[index]],
                                      "y": [keypoints[index+1]],
                                      "c": [keypoints[index+2]]})
        df = df.append(new, ignore_index = True)
        index += 3
        
    return df

def load_np_ndarray(input):
    if input is None:
        return None
    #製作dataframe
    input_df = pd.DataFrame(input[0])
    f = {"x":[], "y":[], "c":[]}
    df = pd.DataFrame(f)
    
    #keypoints中有75筆資料
    #每三筆一組，分別是x座標、y座標、檢測置信度；共25組，對應25個關鍵點
    for i in range(0, 25):
        new = pd.DataFrame.from_dict({"x": [input_df[0].iloc[i]],
                                      "y": [input_df[1].iloc[i]],
                                      "c": [input_df[2].iloc[i]]})
        df = df.append(new, ignore_index = True)
        
    return df

#the similarity between two keypoints
def calculateRatioWith2Points(df1, df2, p1, p2):
    #算出在正常座標平面中ˋ，這一段骨架分別在兩張圖片中對x軸的弧度(夾角) 
    #由於圖片分析完的y軸遞增方向與正常座標平面的y軸遞增方向相反，因此y座標部分倒過來減
    radian1 = math.atan2((df1['y'].iloc[p2] - df1['y'].iloc[p1]),\
                         (df1['x'].iloc[p1] - df1['x'].iloc[p2]))
    radian2 = math.atan2((df2['y'].iloc[p2] - df2['y'].iloc[p1]),\
                         (df2['x'].iloc[p1] - df2['x'].iloc[p2]))
    #cos取值介於-1~1。若兩骨架重合，cos值會是1；骨架垂直，cos值會是0；骨架方向相反，為-1
    #不同人、不同照片骨架長度會有不同，因此只要求找出兩骨架交叉最小夾角，再依夾角大小分級
    cos = math.cos(radian1 - radian2)
    #cos = -1相似度為-100%，cos = 0相似度為0%，cos = 1相似度為100%
    #標準化為0 ~ 100%
    ratio = cos * 100
    #ratio = (cos * 100 + 100) / 2
    #print(ratio)
    return ratio

#the similarity between two limbs from different body
def calculateLimb(df1, df2, list):
    #存放這一肢體每段骨架的相似度
    ratioList = []
    #遍歷肢體上每一點，兩點為一組(一段骨架)，計算相似度並加入以上list
    for i in range(len(list)-1):
        ratio = calculateRatioWith2Points(df1, df2, list[i], list[i+1])
        ratioList.append(ratio)
    #ratioList中每段骨架相似度取平均，即為此一肢體之相似度
    sum = 0
    for x in ratioList:
        sum += x
    ratio = sum / len(ratioList)
    #print(ratio)
    return ratio

#the similarity between two poses
def compareRatio(df1, df2):
    #存放各肢體之相似度
    ratioList = []
    #計算各肢體相似度
    ratioList.append(calculateLimb(df1, df2, [0, 1, 8]))     #body & head
    ratioList.append(calculateLimb(df1, df2, [2, 3, 4]))     #right hand
    ratioList.append(calculateLimb(df1, df2, [5, 6, 7]))     #left hand
    ratioList.append(calculateLimb(df1, df2, [9, 10, 11]))   #right leg
    ratioList.append(calculateLimb(df1, df2, [12, 13, 14]))  #left leg
    #各肢體相似度取平均
    sum = 0
    for x in ratioList:
        sum += x
    result = sum / len(ratioList)
    if result < 0:
        result = 0
    return result

def suggest(df1, df2):
    suggestion = ""
    return suggestion

fileName1 = "C1.jpg"
fileName2 = "C2.jpg"
     
'''
df1 = load_json_keypoints(".\\data\\output_jsons\\" + fileName1 + "\\0_keypoints.json")
df2 = load_json_keypoints(".\\data\\output_jsons\\" + fileName2 + "\\0_keypoints.json")
print("相似度為:"+str(compareRatio(df1, df2)))
'''


