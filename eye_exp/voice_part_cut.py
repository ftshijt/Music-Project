# -*- coding: utf-8 -*-
"""
@author: GS_qbr
"""
from PIL import Image
from PIL import ImageDraw
import cv2 as cv    
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

def Voice_part_cut(pic_id):
    pic_path = 'bar_cut'+str(pic_id)+'.png'
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
    
    if(len(five_lines_index) != 10):
        print('There is sth. wrong with count array in voice_part_cut, please check!')
    
    upper_section_last_line_index = five_lines_index[4]     # 对分割完的某一小节来说，一共分为两大行（左手、右手），先找到上半部分（右手）的五线谱的最后一条线
    
    for i in range(upper_section_last_line_index, len(count)):
        if count[i] == 0 or count[i] == 1:
            voice_part_cut_index = i
            break;
    
    # 4. 找准位置后进行切割
    box=(0,0,width,voice_part_cut_index)
    region=cut_img.crop(box) #此时，region是一个新的图像对象。
    region_arr = 255 - np.array(region)
    region = Image.fromarray(region_arr.astype("uint8"))
    name = "voice_part_cut_"+str(pic_id)+"_0.png"
    region.save(name)  
    print('The upper voice part split complete')
    
    box=(0,voice_part_cut_index,width,len(count))
    region=cut_img.crop(box) #此时，region是一个新的图像对象。
    region_arr = 255 - np.array(region)
    region = Image.fromarray(region_arr.astype("uint8"))
    name = "voice_part_cut_"+str(pic_id)+"_1.png"
    region.save(name)  
    print('The lower voice part split complete')

if __name__ == '__main__': 
    Voice_part_cut(0)
    Voice_part_cut(1)
























