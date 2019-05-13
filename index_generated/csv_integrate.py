# -*- coding: utf-8 -*-
"""
@author: zhangtg
"""


import os
import csv
import pandas as pd
import warnings
warnings.filterwarnings("ignore") #忽略警告，使输出不掺杂警告内容


current_path = os.path.abspath('.')   #表示当前所处的文件夹的绝对路径  


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
     
    
def create_csv(file_name):
    with open(current_path + '/adjusted_csv/' + file_name + '.csv', 'w+', newline="") as f:
        csv_write = csv.writer(f)
        csv_head = ["StudioTestName",
                    "RecordName",
                    "ParticipantName",
                    "singleMediaName",
                    "Music_score_reading_completeness",
                    "Bass_part_reading_completeness",
                    "Left_and_right_hand_integration_ability",
                    "all_recommended_time",
                    "Rhythmic_stability",
                    "bar_difficulty_ave",
                    "Visual_stability",
                    #'media_difficulty', #只有一个数据，就不进行记录
                    "Spectral_analysis_ability3"
                    ]
        csv_write.writerow(csv_head)
        
        
#向csv文件里面写入数据
def write_csv(file_name, content):
    with open(current_path + '/adjusted_csv/' + file_name + '.csv', 'a+', newline="") as f:
        csv_write = csv.writer(f)
        csv_write.writerow(content)
    

if __name__=='__main__':
    #防止多次运行在文件中出现重复的路径
    if os.path.isfile("report_csv_file.txt"):
        os.remove("report_csv_file.txt")
        
    #将所有待分析的csv文件路径存到一个txt文件夹里面
    csv_path = ".\generate_csv"
    Traversal_file(csv_path, "report_csv_file.txt")
    
    all_index = ["Music_score_reading_completeness",
            "Bass_part_reading_completeness",
            "Left_and_right_hand_integration_ability",
            "all_recommended_time",
            "Rhythmic_stability",
            "bar_difficulty_ave",
            "Visual_stability",
            "Spectral_analysis_ability3"
            ]
    

    t_csv = open("report_csv_file.txt")
    csv_line = t_csv.readline()
    while csv_line:
        #提取出文件名，便于后面使用
        t_list = csv_line.split('\\')
        test_record = t_list[len(t_list)-1][:-5]
        record_kind = test_record[-1:]
        
        #读入csv文件
        current_csv = pd.read_csv(csv_line[:-1])
        
        #创建新的csv文件
        create_csv(test_record)
        
        #对读入的tsv文件的singleMediaName列进行去重，筛选出所有的谱子名称
        raw_MediaName = current_csv['singleMediaName']
        MediaName = raw_MediaName.drop_duplicates(keep='first')
        
        for i in range(0, len(MediaName)):
            singleMediaName = MediaName.iloc[i]
            content = [current_csv.loc[1, 'StudioTestName'], 
                       current_csv.loc[1, 'RecordName'],
                       current_csv.loc[1, 'ParticipantName'],
                       singleMediaName
                       ]
            
            if (singleMediaName == 0 or singleMediaName == 'all'):
                continue
            
            #在原数据中筛选出含有singleMediaName的行
            report_csv_MediaName = current_csv[current_csv['singleMediaName'].isin([singleMediaName])]
            report_csv_MediaName.fillna(0, inplace = True) #处理NaN值，直接在原数据中进行修改
            
            #查找指标对应的数据
            for single_index in all_index:
                index = report_csv_MediaName[report_csv_MediaName.IndexCategory == single_index].index.tolist()
                if (len(index) == 0):
                    content.append(0)
                    continue
                content.append(report_csv_MediaName.loc[index[0],'IndexData'])
            
            write_csv(test_record, content)
        csv_line = t_csv.readline()
    t_csv.close()