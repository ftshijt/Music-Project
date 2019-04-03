# -*- coding: utf-8 -*-
"""
@author: zhangtg
"""


import os
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from pylab import mpl


mpl.rcParams['font.sans-serif'] = ['FangSong'] # 指定默认字体
mpl.rcParams['axes.unicode_minus'] = False # 解决保存图像是负号'-'显示为方块的问题


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
    
    
#将英文名转化为中文名
def English2Chinese(name):
    if (name == "Music_score_reading_completeness"):
        return "乐谱阅读完成度"
    elif (name == "Bass_part_reading_completeness"):
        return "低音声部阅读完成度"
    elif (name == "Left_and_right_hand_integration_ability"):
        return "左右手统合能力"
    elif (name == "all_recommended_time"):
        return "总推荐时间"
    elif (name == "bar_difficulty_ave"):
        return "小节难度平均值"
    elif (name == "media_difficulty"):
        return "图片总体难度"
    elif (name == "Rhythmic_stability"):
        return "节奏稳定性"
    elif (name == "Visual_stability"):
        return "视奏稳定性"
    elif (name == "Spectral_analysis_ability3"):
        return "高音、低音谱号的差异"
    return error
    

if __name__=='__main__':
    #防止多次运行在文件中出现重复的路径
    if os.path.isfile("report_csv_file.txt"):
        os.remove("report_csv_file.txt")
        
    #将所有产生的csv文件路径存到一个txt文件夹里面
    csv_path = ".\generate_csv"
    Traversal_file(csv_path, "report_csv_file.txt")
    
    #先将所有csv文件里面的数据读入并且保存到内存，以便于计算排名（超过多少测试）
    all_data = {}
    csv = open("report_csv_file.txt")
    csv_line = csv.readline()
    while csv_line:
        #提取出测试名和记录名，便于后面使用
        t_list = csv_line.split('\\')
        test = t_list[len(t_list)-1][:-13]
        record = t_list[len(t_list)-1][-12:-5]
        
        #读入csv文件
        current_csv = pd.read_csv(csv_line[:-1])
        
        #检测test是否存在
        if not test in all_data.keys():  #如果不存在，则创立空字典
            all_data[test] = {}
        
        #往test里面存对应record的数据
        all_data[test][record] = current_csv
        csv_line = csv.readline()
    csv.close()
    
    #将各项指标的平均值以测试为单位去计算出来
    all_index = {'Music_score_reading_completeness':[],
                 'Bass_part_reading_completeness':[],
                 'Left_and_right_hand_integration_ability':[],
                 'all_recommended_time':[],
                 'Rhythmic_stability':[],
                 'bar_difficulty_ave':[],
                 'Visual_stability':[],
                 'media_difficulty':[],
                 'Spectral_analysis_ability3':[]}
    
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
        
        for i in range(0, len(IndexCategory)):
            singleIndexCategory = IndexCategory.iloc[i]
            
            #在原数据中筛选出含有singleIndexCategory的行
            report_csv_IndexCategory = current_csv[current_csv['IndexCategory'].isin([singleIndexCategory])]
            
            #进行可视化
            IndexData = report_csv_IndexCategory['IndexData']
            all_index[singleIndexCategory].append(np.mean(IndexData))
            
        csv_line = csv.readline()
    csv.close()
    
    #对all_index中的数据进行排序
    for key, values in all_index.items():
        all_index[key].sort()
    
    #以测试为单位生成可视化报告并加入排名
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
                #提取数据，计算排名
                MediaName = report_csv_IndexCategory['singleMediaName']
                IndexData = report_csv_IndexCategory['IndexData']
                IndexData_ave = np.mean(IndexData)
                order = all_index[singleIndexCategory].index(IndexData_ave)
                rank = order / len(all_index[singleIndexCategory]) * 100
                
                #画出左侧折线图
                plt.subplot(121)
                plt.plot(MediaName, IndexData)   
                plt.title(English2Chinese(singleIndexCategory))
                for x, y in zip(MediaName, IndexData):  #在转折点上显示数值
                    plt.text(x, y, str('%.3f' % y), ha='center', va='bottom', fontsize=10.5)
                plt.xlabel('图片名称')
                plt.ylabel('指标数据')
                plt.xticks(rotation=40)  #x轴名称进行旋转，使其显示完全
                
                #画出右侧信息
                plt.subplot(122)
                #画饼图（数据，数据对应的标签，百分数保留两位小数点）
                plt.pie([rank, 100 - rank], labels = ['超过的测试', '未超过的测试'], autopct='%1.2f%%') 
                plt.title("能力报告")
                
                #保存图片
                pdf.savefig(bbox_inches = 'tight')
                plt.close()
                
        csv_line = csv.readline()
    csv.close()