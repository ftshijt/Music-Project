# -*- coding: utf-8 -*-
"""
@author: zhangtg
"""


import os
import csv
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


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
            txt_file.write(fi_d+'\n')
    txt_file.close
    
    
if __name__=='__main__':
    #防止多次运行在文件中出现重复的路径
    if os.path.isfile("report_csv_file.txt"):
        os.remove("report_csv_file.txt")
        
    #将所有产生的csv文件路径存到一个txt文件夹里面
    csv_path = ".\generate_csv"
    Traversal_file(csv_path, "report_csv_file.txt")
    
    #遍历csv文件
    csv = open("report_csv_file.txt")
    csv_line = csv.readline()
    while csv_line:
        #提取出文件名，便于后面使用
        t_list = csv_line.split('\\')
        test_record = t_list[len(t_list)-1][:-5]
        
        #读入csv文件
        current_csv = pd.read_csv(csv_line[:-1])
        
        #对读入的tsv文件的MediaName列进行去重，筛选出所有的谱子名称
        raw_IndexCategory = current_csv['IndexCategory']
        IndexCategory = raw_IndexCategory.drop_duplicates(keep='first')
        
        with PdfPages('.\generate_picture\\'+test_record+'.pdf') as pdf:
            for i in range(0, len(IndexCategory)):
                singleIndexCategory = IndexCategory.iloc[i]
                
                if (singleIndexCategory == 'media_difficulty'): #只有一个数据，无需画图
                    continue
                
                #在原数据中筛选出含有singleIndexCategory的行
                report_csv_IndexCategory = current_csv[current_csv['IndexCategory'].isin([singleIndexCategory])]
                
                #进行可视化
                MediaName = report_csv_IndexCategory['singleMediaName']
                IndexData = report_csv_IndexCategory['IndexData']
                plt.plot(MediaName, IndexData)   
                plt.title(test_record+'_'+singleIndexCategory)
                plt.xlabel('MediaName')
                plt.ylabel('IndexData')
                plt.xticks(rotation=40)  #x轴名称进行旋转，使其显示完全
                pdf.savefig(bbox_inches = 'tight')
                plt.close()
                
        csv_line = csv.readline()
    csv.close()