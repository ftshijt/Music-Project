# -*- coding: utf-8 -*-
"""
@author: zhangtg
"""

from PIL import Image
import os
import numpy as np
import pandas as pd


#遍历文件夹，传入关键词
def Traversal_file(file_path, txt_name):
    #遍历file_path下所有文件，包括子目录
    txt_file = open(txt_name, "a+")
    files = os.listdir(file_path)
    for fi in files:
        fi_d = os.path.join(file_path, fi)
        if os.path.isdir(fi_d):
            Traversal_file(fi_d, txt_name)  #递归 
        else:
            result = os.path.join(file_path, fi_d)
#            print(os.path.join(file_path, fi_d)[:-4])
            txt_file.write(result+'\n')
    txt_file.close


#给入图片的名称，返回对应的coordinate_info文件路径
def search_img_path(img_name):
    img = open("image_file.txt")
    img_line = img.readline()
    while img_line:
        #寻找符合条件的路径名
        if img_line.find(img_name)!=-1 and img_line.find('coordinate_info')!=-1:
            img.close()
            return img_line
        img_line = img.readline()
    img.close()


#乐谱阅读完成度（衡量学生整体的乐谱完成情况）
#技术实现：所有含有眼睛焦点的小节数除以所有小节数
#def Music_score_reading_completeness(key, file_path, img_path):
    

#低音声部阅读完成度（衡量学生低音声部乐谱的完成情况）
#技术实现：所有低音声部含有眼睛焦点的小节数除以所有低音声部小节数
#def Bass_part_reading_completeness(key, file_path, img_path):


#视奏稳定性（乐谱掌控能力）

    
#节奏稳定性（匀速视奏能力）

    
#左右手统合能力
#def Left_and_right_hand_integration_ability(key, file_path, img_path):
    
    
    
#主函数
if __name__=='__main__':
    #防止多次运行在文件中出现重复的路径
    if os.path.isfile("image_file.txt"):
        os.remove("image_file.txt")
    if os.path.isfile("eye_tracking_file.txt"):
        os.remove("eye_tracking_file.txt")
        
    #将所有的图片和tsv文件路径存到一个txt文件夹里面
    image_path = "E:\images_cut_finished"
    eye_tracking_path = "E:\sjt-eye-tracking-project"
    Traversal_file(image_path, "image_file.txt")
    Traversal_file(eye_tracking_path, "eye_tracking_file.txt")
    
    #对于tsv文件进行遍历
    #先筛选出所有被测试者的姓名
    StudioTestName = {'B test4':[],
                      'Btest_new3':[],
                      'Btest_new6':[],
                      'C test3':[],
                      'C test4':[],
                      'C test5':[],
                      'C test6':[],
                      'French_test1':[],
                      'French_test3':[],
                      'French_test4':[],
                      'French_test5':[],
                      }
    
    for key, value in StudioTestName.items():
        #查找对应的tsv和图片文件
        tsv = open("eye_tracking_file.txt")
        tsv_line = tsv.readline()
        while tsv_line:
            if tsv_line.find(key) != -1:
#                print (key)
#                print (tsv_line)
                Music_score_reading_completeness(key, tsv_line[:-1])
                Bass_part_reading_completeness(key, tsv_line[:-1])
                Left_and_right_hand_integration_ability(key, tsv_line[:-1])
                break
            tsv_line = tsv.readline()
        tsv.close()
    
    
#    tsv = open("eye_tracking_file.txt")
#    tsv_line = tsv.readline()
#    while tsv_line:
#        print (tsv_line)
#        读入tsv，并且存到dict里面
#        train = pd.read_csv(tsv_line[:-1], sep='\t', header=0, error_bad_lines = False)
#        print (train)
#        
#        抽取测试者的名字，作为分析的单位(先行手动输入)
#        name = train.loc[1, 'StudioTestName']
#        if name in train.keys():
#            continue
#        else:
#            StudioTestName[train.loc[1, 'StudioTestName']] = []
#            print(name)
#            
#        tsv_line = tsv.readline()
#    tsv.close()