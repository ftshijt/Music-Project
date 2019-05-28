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
import warnings
import copy
warnings.filterwarnings("ignore") #忽略警告，使输出不掺杂警告内容


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
        return "MSRC"
    elif (name == "Bass_part_reading_completeness"):
        return "BPRC"
    elif (name == "Left_and_right_hand_integration_ability"):
        return "LRIA"
    elif (name == "all_recommended_time"):
        return "总推荐时间"
    elif (name == "bar_difficulty_ave"):
        return "小节难度平均值"
    elif (name == "media_difficulty"):
        return "图片总体难度"
    elif (name == "Rhythmic_stability"):
        return "RS"
    elif (name == "Visual_stability"):
        return "VS"
    elif (name == "Spectral_analysis_ability3"):
        return "SAA3"
    
    
#把同一个谱子的不同小节数据合在一起，计算平均值，返回dict
def CombineBar(MediaName, IndexData):
    new_MediaName = copy.deepcopy(MediaName)
    count = 0
    for name in MediaName:
        #返回第一个数字的位置
        first_num = len(name)-1
        for i in range(len(name)):
            if (ord(name[i]) >= ord('0') and ord(name[i]) <= ord('9')):
                first_num = i
                break
        #返回第一个‘.’的位置
        first_point = name.index('.')
        split_location = min(first_num, first_point)
        new_MediaName[count] = MediaName[count][:split_location]
        count += 1
    #对名字进行去重
    duplicate_name = []
    for name in new_MediaName:
        if name not in duplicate_name:
            duplicate_name.append(name)
    duplicate_data = []
    #对相同谱子不同小节的数据求平均值
    for name in duplicate_name:
        sum = 0
        t_count = 0
        media_count = 0
        for t_name in new_MediaName:
            if t_name == name:
                sum += IndexData[t_count]
                media_count += 1
            t_count += 1
        ave = sum / media_count
        duplicate_data.append(ave)
    return dict(zip(duplicate_name,duplicate_data))



 
    

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
    all_index = {'Music_score_reading_completeness':{'1':[],'2':[],'3':[],'4':[],'5':[]},
                 'Bass_part_reading_completeness':{'1':[],'2':[],'3':[],'4':[],'5':[]},
                 'Left_and_right_hand_integration_ability':{'1':[],'2':[],'3':[],'4':[],'5':[]},
                 'all_recommended_time':{'1':[],'2':[],'3':[],'4':[],'5':[]},
                 'Rhythmic_stability':{'1':[],'2':[],'3':[],'4':[],'5':[]},
                 'bar_difficulty_ave':{'1':[],'2':[],'3':[],'4':[],'5':[]},
                 'Visual_stability':{'1':[],'2':[],'3':[],'4':[],'5':[]},
                 'media_difficulty':{'1':[],'2':[],'3':[],'4':[],'5':[]},
                 'Spectral_analysis_ability3':{'1':[],'2':[],'3':[],'4':[],'5':[]}
                 }
    
    csv = open("report_csv_file.txt")
    csv_line = csv.readline()
    while csv_line:
        #提取出文件名，便于后面使用
        t_list = csv_line.split('\\')
        test_record = t_list[len(t_list)-1][:-5]
        record_kind = test_record[-5:-4]
        
        #读入csv文件
        current_csv = pd.read_csv(csv_line[:-1])
        
        #对读入的tsv文件的MediaName列进行去重，筛选出所有的谱子名称
        raw_IndexCategory = current_csv['IndexCategory']
        IndexCategory = raw_IndexCategory.drop_duplicates(keep='first')
        
        for i in range(0, len(IndexCategory)):
            singleIndexCategory = IndexCategory.iloc[i]
            
            #在原数据中筛选出含有singleIndexCategory的行
            report_csv_IndexCategory = current_csv[current_csv['IndexCategory'].isin([singleIndexCategory])]
            report_csv_IndexCategory.fillna(0, inplace = True) #处理NaN值，直接在原数据中进行修改
            
            #将数据计算出平均数储存到all_index的对应位置
            IndexData = report_csv_IndexCategory['IndexData']
            all_index[singleIndexCategory][record_kind].append(np.mean(IndexData))
            
        csv_line = csv.readline()
    csv.close()
    
    #对all_index中的数据进行排序
    for key, values in all_index.items():
        for kind in ['1','2','3','4','5']:
            all_index[key][kind].sort()
    
    #以测试为单位生成可视化报告并加入排名
    #遍历csv文件
    csv = open("report_csv_file.txt")
    csv_line = csv.readline()
    while csv_line:
        #提取出文件名，便于后面使用
        t_list = csv_line.split('\\')
        test_record = t_list[len(t_list)-1][:-5]
        record_kind = test_record[-5:-4]
        
        #读入csv文件
        current_csv = pd.read_csv(csv_line[:-1])
        
        #对读入的tsv文件的MediaName列进行去重，筛选出所有的谱子名称
        raw_IndexCategory = current_csv['IndexCategory']
        IndexCategory = raw_IndexCategory.drop_duplicates(keep='first')
        
        with PdfPages('.\generate_radar_chart\\'+test_record+'.pdf') as pdf:
            radar_name = []
            radar_rank = []
            for i in range(0, len(IndexCategory)):
                singleIndexCategory = IndexCategory.iloc[i]
                
                if (singleIndexCategory == 'media_difficulty'
                        or singleIndexCategory == 'bar_difficulty_ave'
                        or singleIndexCategory == 'all_recommended_time'):
                    continue #非个人能力评估
                
                #在原数据中筛选出含有singleIndexCategory的行
                report_csv_IndexCategory = current_csv[current_csv['IndexCategory'].isin([singleIndexCategory])]
                report_csv_IndexCategory.fillna(0, inplace = True) #处理NaN值，直接在原数据中进行修改
                
                #进行可视化
                #提取数据，计算排名
                MediaName = report_csv_IndexCategory['singleMediaName']
                IndexData = report_csv_IndexCategory['IndexData']
                IndexData_ave = np.mean(IndexData)
                order = all_index[singleIndexCategory][record_kind].index(IndexData_ave)
                rank = order / len(all_index[singleIndexCategory][record_kind]) * 100

                if (singleIndexCategory == 'Spectral_analysis_ability3'):
                    rank = 100 - rank

                radar_name.append(English2Chinese(singleIndexCategory))
                radar_rank.append(rank)
				
            plt.rcParams['font.sans-serif'] = ['KaiTi']  # 显示中文
            labels = np.array(radar_name) # 标签
            dataLenth = len(radar_name)  # 数据长度
            data_radar = np.array(radar_rank) # 数据
            angles = np.linspace(0, 2*np.pi, dataLenth, endpoint=False)  # 分割圆周长
            data_radar = np.concatenate((data_radar, [data_radar[0]]))  # 闭合
            angles = np.concatenate((angles, [angles[0]]))  # 闭合
            plt.polar(angles, data_radar, 'bo-', linewidth=1)  # 做极坐标系
            plt.thetagrids(angles * 180/np.pi, labels)  # 做标签
            plt.fill(angles, data_radar, facecolor='r', alpha=0.25)# 填充
            plt.ylim(0, 100)
            plt.title(u'能力报告')
            plt.tight_layout()
            pdf.savefig(bbox_inches = 'tight')
            plt.close()
            
        csv_line = csv.readline()
    csv.close()