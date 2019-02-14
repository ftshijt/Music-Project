# -*- coding: utf-8 -*-
"""
Created on Jan 29 14:48:16 2019

@author: GS_qbr
"""

from PIL import Image
from PIL import ImageDraw
import cv2 as cv    
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import os

def Traversing_dir(folder_name):    #根据后缀名,遍历文件夹删除文件
    #遍历根目录
    for root,dirs,files in os.walk(folder_name):
        for file in files:
            #文件后缀名
            extFile=os.path.splitext(file)[1]
            if extFile==".png":
                os.remove(os.path.join(root,file))    #删除文件
        for dir in dirs:
            #递归调用自身
            Traversing_dir(dir)

def Folder_check(folder_name):      #文件夹没有就新建，有就清空文件
    curPath=os.getcwd()
    targetPath=curPath+os.path.sep+folder_name
    if not os.path.exists(targetPath):
        os.makedirs(targetPath)
    else:
        Traversing_dir(folder_name)
        
def Overall_split(pic_name):
    '''
    funtion:    图片水平投影，对两行乐谱进行整体分割
                函数运行过程中，生成img_projection.png(水平投影的可视化)
                                   line_cut(i).png(最终分割的图片)
    parameters:
        img_twovalues: 二值化后的图像numpy矩阵
        cut_img: 最终实施切割的图像对象（Image类型）
    return:
        i+1 : 总共分割成几部分
    '''
    pic_path = 'image/'+pic_name+'.png'
    img_arr = cv.imread(pic_path,0)
    cut_img = Image.fromarray((255 - img_arr).astype("uint8"))
    
    # 1. 得到二值化后的图片
    threshold, img_twovalues = cv.threshold(img_arr, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    
    # 2. 图片水平投影，对两行乐谱进行整体分割
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
     
    count_nonzero_index = np.array(count).nonzero()[0]  #建立高度投影有值的索引
    
    key_index = []
    for i in range(1, np.shape(count_nonzero_index)[0]):
        if(count_nonzero_index[i] != count_nonzero_index[i-1]+1):
            key_index.append(i)
            print(i, count_nonzero_index[i])
    if(len(key_index) == 0):    # 针对只有一行谱子的情况
        key_index.append(count_nonzero_index[0])
        
    index_continue = []         #得到一段一段连续有值的高度分割的索引
    for i in range(np.shape(key_index)[0]):
        if i == 0:
            tmp = (0, key_index[0]-1)
            index_continue.append(tmp)        
        else:    
            tmp = (key_index[i-1], key_index[i]-1)
            index_continue.append(tmp)
    tmp = (key_index[i], np.shape(count_nonzero_index)[0] - 1)
    index_continue.append(tmp)
    
    index_continue_delete = []
    height_min = int(height/8)
    for i in range(len(index_continue)):
        if count_nonzero_index[index_continue[i][1]] - count_nonzero_index[index_continue[i][0]] < height_min:
            index_continue_delete.append(i)
    count_delete = 0
    for i in range(len(index_continue_delete)):
        index_continue.remove(index_continue[index_continue_delete[i]-count_delete])    # 删的时候因为元素个数在减少，索引值也要跟着变
        count_delete = count_delete + 1
    
    img_split_array = []
    for i in range(len(index_continue)):
        box=(0,count_nonzero_index[index_continue[i][0]],width,count_nonzero_index[index_continue[i][1]])
        region=cut_img.crop(box) #此时，region是一个新的图像对象。
        region_arr = 255 - np.array(region)
        img_split_array.append(region_arr)
        region = Image.fromarray(region_arr.astype("uint8"))
        name = pic_name+"/line_cut"+str(i)+".png"
        region.save(name)  
        print('NO.{} section split complete'.format(i+1))
        
        cv.line(img_arr, (0,count_nonzero_index[index_continue[i][0]]), (1669, count_nonzero_index[index_continue[i][0]]), (0,0,255), 1) 
        cv.line(img_arr, (0,count_nonzero_index[index_continue[i][1]]), (1669, count_nonzero_index[index_continue[i][1]]), (0,0,255), 1)
    cv.imwrite(pic_name+'/img_split.png', img_arr) 
    
    plt.imsave(pic_name+'/img_projection.png',img_projection)
    
    return i+1

def Bar_line_cut(rootFolderName, pic_id):
    pic_path = rootFolderName+'/line_cut'+str(pic_id)+'.png'
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
#    five_lines_index = []  #五线谱的线所在的位置
#    for i in range(len(count)):
#        if count[i] > width * 2/3:
#            five_lines_index.append(i)
    five_lines_index = np.array(count).argsort()[-10:][::-1]
    
    if(len(five_lines_index) != 10):
        print('There is sth. wrong with count array in voice_part_cut, please check!')
        return
    
    five_lines_begin = np.min(five_lines_index)  #五线谱开始的行
    five_lines_end = np.max(five_lines_index)    #五线谱结束的行
    height_five_lines = five_lines_end - five_lines_begin
    
    
    bar_line_index = []     #小节线所在位置
    for j in range(width):
        count_five_lines = 0
        for i in range(five_lines_begin, five_lines_end):
            if img_twovalues[i][j] == 0:
                count_five_lines = count_five_lines + 1
        if count_five_lines == height_five_lines:
            bar_line_index.append(j)

    
#    # 检测休止线，并去除
#    pause_index = len(bar_line_index)
#    for i in range(len(bar_line_index)-2):
#        if bar_line_index[i] + 1 == bar_line_index[i+1] and bar_line_index[i+1] == bar_line_index[i+2]:
#            pause_index = i
#            break;
#    bar_line_index = bar_line_index[0:pause_index]
#        
#    print(pause_index)
    
    bar_id = 0
    for i in range(len(bar_line_index)-1):
        if bar_line_index[i+1] - bar_line_index[i] >= 15:
            box=(bar_line_index[i],0,bar_line_index[i+1],height)
            region=cut_img.crop(box) #此时，region是一个新的图像对象。
            region_arr = 255 - np.array(region)
            region = Image.fromarray(region_arr.astype("uint8"))
            name = rootFolderName+"/bar_cut_"+str(pic_id)+"_"+str(bar_id)+".png"
            region.save(name)  
            print('NO.{} bar split complete'.format( bar_id+1 ))
            bar_id = bar_id + 1
    return bar_id

def Voice_part_cut(rootFolderName, overrall_id, pic_id, height_total, width_total):
    pic_path = rootFolderName+'/bar_cut_'+str(overrall_id)+'_'+str(pic_id)+'.png'
    
    print(pic_path)
    
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
#    five_lines_index = []  #五线谱的线所在的位置
#    for i in range(len(count)):
#        if count[i] > width * 4/5:
#            five_lines_index.append(i)
    five_lines_index = np.array(count).argsort()[-10:][::-1]
    five_lines_index = np.sort(five_lines_index)
    
    if(len(five_lines_index) != 10):
        print('There is sth. wrong with count array in voice_part_cut, please check!')
        return
    
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
    name = rootFolderName+"/result/voice_part_cut_"+str(overrall_id)+'_'+str(pic_id)+"_0.png"
    region.save(name)  
    difficuly_upper = np.sum(((255 - np.array(region))/255).astype('int'))
    density_upper = round(difficuly_upper / (height * width), 4)
    density_upper_overall = round(difficuly_upper / (height_total * width_total), 4)
    print('The upper voice part split complete, difficulty:{:.4}%, difficulty_overall:{:.4}%'.format( density_upper * 100 , density_upper_overall * 100))
    
    box=(0,voice_part_cut_index,width,len(count))
    region=cut_img.crop(box) #此时，region是一个新的图像对象。
    region_arr = 255 - np.array(region)
    region = Image.fromarray(region_arr.astype("uint8"))
    name = rootFolderName+"/result/voice_part_cut_"+str(overrall_id)+'_'+str(pic_id)+"_1.png"
    region.save(name)  
    difficuly_lower = np.sum(((255 - np.array(region))/255).astype('int'))
    density_lower = round(difficuly_lower / (height * width), 3)
    density_lower_overall = round(difficuly_lower / (height_total * width_total), 4)
    print('The lower voice part split complete, difficulty:{:.4}%, difficulty_overall:{:.4}%'.format( density_lower * 100 , density_lower_overall * 100))

def Cut_into_voive_part(pic_name):
    Folder_check(pic_name)
    Folder_check(pic_name+'/result')
    overall_num = Overall_split(pic_name)   # 返回有多少图片要放入bar切割

    (height, width) = cv.imread('image/'+pic_name+'.png',0).shape
     
    for overrall_id in range(overall_num):
        bar_num = Bar_line_cut(pic_name, overrall_id)
        for bar_id in range(bar_num):
            Voice_part_cut(pic_name, overrall_id, bar_id, height, width)
    return overall_num, bar_num   #返回这两个值，后期代码遍历结果用

if __name__ == '__main__':
    pic_name = os.listdir('image')
    for i in range(len(pic_name)):
        print('**********************'+pic_name[i]+'************************')
        pic_name[i] = pic_name[i][:-4] 
        Cut_into_voive_part(pic_name[i])
    
        
    

    
            

   













