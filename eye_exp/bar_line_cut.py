# -*- coding: utf-8 -*-
"""
Created on Jan 29 23:45:08 2019

@author: GS_qbr
"""
from PIL import Image
from PIL import ImageDraw
import cv2 as cv    
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

def Bar_line_cut(rootFolderName, pic_id):
    pic_path = 'line_cut'+str(pic_id)+'.png'
    img_arr = cv.imread(pic_path,0)
    cut_img = Image.fromarray((255 - img_arr).astype("uint8"))
    
    # 1. 得到二值化后的图片
    threshold, img_twovalues = cv.threshold(img_arr, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    
    # 2. 图片水平投影
    img_projection = img_twovalues.copy()       # 实现数组的深copy
    (height,width)=img_projection.shape
     
    count = [0 for z in range(0, height)] 
     
    for j in range(0,height):  
        for i in range(0,width):  
            if  img_projection[j,i]==0: 
                count[j]+=1 
    for j in range(0,height):  
        for i in range(0,count[j]):   
            img_projection[j,i]=0    
    
    # 3. 对每个分割完的部分单独处理，按小节线分割(小节线的特点：从第一行五线谱到最后一行五线谱)
    five_lines_index = []  #五线谱的线所在的位置
    for i in range(len(count)):
        if count[i] > width * 2/3:
            five_lines_index.append(i)
    
    five_lines_begin = five_lines_index[0]  #五线谱开始的行
    five_lines_end = five_lines_index[9]    #五线谱结束的行
    height_five_lines = five_lines_end - five_lines_begin
    
    bar_line_index = []     #小节线所在位置
    for j in range(width):
        count_five_lines = 0
        for i in range(five_lines_begin, five_lines_end):
            if img_twovalues[i][j] == 0:
                count_five_lines = count_five_lines + 1
        if count_five_lines == height_five_lines:
            bar_line_index.append(j)
    
    for i in range(len(bar_line_index)):
        if i != len(bar_line_index) - 1:
            box=(bar_line_index[i],0,bar_line_index[i+1],height)
            region=cut_img.crop(box) #此时，region是一个新的图像对象。
            region_arr = 255 - np.array(region)
            region = Image.fromarray(region_arr.astype("uint8"))
            name = rootFolderName+"bar_cut"+str(i)+".png"
            region.save(name)  
            print('NO.{} bar split complete'.format(i+1))
    
    return i+1

if __name__ == '__main__': 
    Bar_line_cut(0)

        
    