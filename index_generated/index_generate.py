# -*- coding: utf-8 -*-
"""
@author: zhangtg
"""

# =============================================================================
# 已发现bug：有些眼动数据里的图片不存在，如LB1_1，目前直接raise进行异常处理，但这样程序无法继续正常运行，目前仅测试B test4
# 后期改进方向：函数结构大致一样，后期进行合并，精简代码，方便维护
# =============================================================================

import os
import csv
import pandas as pd
import warnings
import numpy as np
import index_generate_utils
from scipy.stats import pearsonr
warnings.filterwarnings("ignore") #忽略警告，使输出不掺杂警告内容


current_path = os.path.abspath('.')   #表示当前所处的文件夹的绝对路径  


#针对每一份tsv文件创立对应的输出文件
def create_csv(file_name):
    with open(current_path + '/generate_csv/' + file_name + '.csv', 'w+', newline="") as f:
        csv_write = csv.writer(f)
        csv_head = ["StudioTestName",
                    "singleMediaName",
                    "IndexCategory",
                    "IndexData"]
        csv_write.writerow(csv_head)

#向csv文件里面写入数据
def write_csv(file_name, content):
    with open(current_path + '/generate_csv/' + file_name + '.csv', 'a+', newline="") as f:
        csv_write = csv.writer(f)
        csv_write.writerow(content)


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


#给入图片的名称，返回对应的coordinate_info文件路径
def search_img_path(img_name):
    if img_name == 'blank': #blank无需处理
        return 0
    img = open("image_file.txt")
    img_line = img.readline()
    while img_line:
        #寻找符合条件的路径名
        if img_line.find(img_name)!=-1 and img_line.find('coordinate_info')!=-1:
            img.close()
            return img_line
        img_line = img.readline()
    img.close()
    #运行到这里说明未找到
    raise KeyError(img_name) #错误处理，传入图片名称找不到对应的文件


#乐谱阅读完成度（衡量学生整体的乐谱完成情况）
#技术实现：所有含有眼睛焦点的小节数除以所有小节数
def Music_score_reading_completeness(StudioTestName, file_path, file_name):
    eye_data = pd.read_csv(file_path, sep='\t', header=0, low_memory=False) #读入传入的tsv文件
    eye_data.fillna(0, inplace = True) #处理NaN值，直接在原数据中进行修改
    
    #对读入的tsv文件的MediaName列进行去重，筛选出所有的谱子名称
    raw_MediaName = eye_data['MediaName']
    MediaName = raw_MediaName.drop_duplicates(keep='first')  
    
    for i in range(0, len(MediaName)):
        #针对每一个谱子，查找对应的coordinate_info.csv文件
        singleMediaName = MediaName.iloc[i]
        
        if singleMediaName == 0:  #在处理原数据的时候把所有的NaN赋为了0
            continue
        else:
            img_path = search_img_path(singleMediaName[:-4]) #所有的后缀都是.jpg或者.PNG，长度一致
            if img_path == 0: #查找blank的返回值
                continue
            img_path = img_path[:-1] #去掉字符串结尾的'/n'
            
             #针对特定谱子的行，结合coordinate_info.csv文件判断含有眼睛焦点的小节数
            img_data = pd.read_csv(img_path)
            all_bar = img_data.shape[0]
            
            #在原眼动数据中筛选出含有singleMediaName的行
            eye_data_certain_MediaName = eye_data[eye_data['MediaName'].isin([singleMediaName])]
            
            #对FixedIndex进行去重
            eye_data_certain_MediaName_FixationIndex = eye_data_certain_MediaName.drop_duplicates(subset=['FixationIndex'], keep='first') 
            
            #判断特定的用含有眼睛焦点的小节数
            fixed_bar = 0
            for j in range(0, len(img_data)): #遍历每一个小节(分为高音和低音部分)
                for indexs in eye_data_certain_MediaName_FixationIndex.index:                    
                    if (img_data.ix[j, 'x_left']<=eye_data_certain_MediaName_FixationIndex.ix[indexs, 'FixationPointX (MCSpx)'] and 
                        img_data.ix[j, 'y_left']<=eye_data_certain_MediaName_FixationIndex.ix[indexs, 'FixationPointY (MCSpx)'] and
                        img_data.ix[j, 'x_right']>=eye_data_certain_MediaName_FixationIndex.ix[indexs, 'FixationPointX (MCSpx)'] and
                        img_data.ix[j, 'y_right']>=eye_data_certain_MediaName_FixationIndex.ix[indexs, 'FixationPointY (MCSpx)']):
                        #如果视线的焦点在该小节内
                        fixed_bar += 1
                        break
                    
            #用含有眼睛焦点的小节数除以所有的小节数，并且输出到csv文件
            content = [StudioTestName, singleMediaName, "Music_score_reading_completeness", fixed_bar / all_bar]
            write_csv(file_name, content)
    

#低音声部阅读完成度（衡量学生低音声部乐谱的完成情况）
#技术实现：所有低音声部含有眼睛焦点的小节数除以所有低音声部小节数
def Bass_part_reading_completeness(StudioTestName, file_path, file_name):
    eye_data = pd.read_csv(file_path, sep='\t', header=0, low_memory=False) #读入传入的tsv文件
    eye_data.fillna(0, inplace = True) #处理NaN值，直接在原数据中进行修改
    
    #对读入的tsv文件的MediaName列进行去重，筛选出所有的谱子名称
    raw_MediaName = eye_data['MediaName']
    MediaName = raw_MediaName.drop_duplicates(keep='first')  
    
    for i in range(0, len(MediaName)):
        #针对每一个谱子，查找对应的coordinate_info.csv文件
        singleMediaName = MediaName.iloc[i]
        
        if singleMediaName == 0:  #在处理原数据的时候把所有的NaN赋为了0
            continue
        else:
            img_path = search_img_path(singleMediaName[:-4]) #所有的后缀都是.jpg或者.PNG，长度一致
            if img_path == 0: #查找blank的返回值
                continue
            img_path = img_path[:-1] #去掉字符串结尾的'/n'
            
             #针对特定谱子的行，结合coordinate_info.csv文件判断含有眼睛焦点的小节数
            img_data = pd.read_csv(img_path)
            all_bass_bar = img_data.shape[0] / 2
            
            #在原眼动数据中筛选出含有singleMediaName的行
            eye_data_certain_MediaName = eye_data[eye_data['MediaName'].isin([singleMediaName])]
            
            #对FixedIndex进行去重
            eye_data_certain_MediaName_FixationIndex = eye_data_certain_MediaName.drop_duplicates(subset=['FixationIndex'], keep='first') 
            
            #判断特定的用含有眼睛焦点的小节数
            fixed_bar = 0
            for j in range(1, len(img_data), 2): #遍历每一个低音部分，以2为跨度
                for indexs in eye_data_certain_MediaName_FixationIndex.index:                    
                    if (img_data.ix[j, 'x_left']<=eye_data_certain_MediaName_FixationIndex.ix[indexs, 'FixationPointX (MCSpx)'] and 
                        img_data.ix[j, 'y_left']<=eye_data_certain_MediaName_FixationIndex.ix[indexs, 'FixationPointY (MCSpx)'] and
                        img_data.ix[j, 'x_right']>=eye_data_certain_MediaName_FixationIndex.ix[indexs, 'FixationPointX (MCSpx)'] and
                        img_data.ix[j, 'y_right']>=eye_data_certain_MediaName_FixationIndex.ix[indexs, 'FixationPointY (MCSpx)']):
                        #如果视线的焦点在该小节内
                        fixed_bar += 1
                        break
            
            content = [StudioTestName, singleMediaName, "Bass_part_reading_completeness", fixed_bar / all_bass_bar]
            write_csv(file_name, content)

#视奏稳定性（乐谱掌控能力）、节奏稳定性（匀速视奏能力）、图片与测试的难度（黑色像素比例）
def Visual_stability_and_rhythmic_stability(StudioTestName, file_path, file_name):
    eye_data = pd.read_csv(file_path, sep='\t', header=0, low_memory=False) #读入传入的tsv文件
    eye_data.fillna(0, inplace = True) #处理NaN值，直接在原数据中进行修改
    
    #对读入的tsv文件的MediaName列进行去重，筛选出所有的谱子名称
    raw_MediaName = eye_data['MediaName']
    MediaName = raw_MediaName.drop_duplicates(keep='first')  
    
    #记录每个图片的难度
    media_difficulty = []
    
    for i in range(0, len(MediaName)):
        #针对每一个谱子，查找对应的coordinate_info.csv文件
        singleMediaName = MediaName.iloc[i]
        
        if singleMediaName == 0:  #在处理原数据的时候把所有的NaN赋为了0
            continue
        else:
            img_path = search_img_path(singleMediaName[:-4]) #所有的后缀都是.jpg或者.PNG，长度一致
            if img_path == 0: #查找blank的返回值
                continue
            img_path = img_path[:-1] #去掉字符串结尾的'/n'
            
             #针对特定谱子的行，结合coordinate_info.csv文件判断含有眼睛焦点的小节数
            img_data = pd.read_csv(img_path)
            all_bar = img_data.shape[0]
            
            #在原眼动数据中筛选出含有singleMediaName的行
            eye_data_certain_MediaName = eye_data[eye_data['MediaName'].isin([singleMediaName])]
            
            #记录每一小节的凝视时数
            bar_time = [0 for t in range(int(all_bar/2))]
            #记录每一小节低音高音部分difficulty_overall之和
            bar_difficulty = [0 for t in range(int(all_bar/2))]
            
            for j in range(0, len(img_data)): #遍历每一个小节(分为高音和低音部分)
                bar_index = int(j/2)
                for indexs in eye_data_certain_MediaName.index:                    
                    if (img_data.ix[j, 'x_left']<=eye_data_certain_MediaName.ix[indexs, 'FixationPointX (MCSpx)'] and 
                        img_data.ix[j, 'y_left']<=eye_data_certain_MediaName.ix[indexs, 'FixationPointY (MCSpx)'] and
                        img_data.ix[j, 'x_right']>=eye_data_certain_MediaName.ix[indexs, 'FixationPointX (MCSpx)'] and
                        img_data.ix[j, 'y_right']>=eye_data_certain_MediaName.ix[indexs, 'FixationPointY (MCSpx)']):
                        #如果视线的焦点在该小节内
                        #计算小节数
                        bar_time[bar_index] = eye_data_certain_MediaName.ix[indexs, 'GazeEventDuration']
                        break
                #在遍历coordinate_info.csv文件
                bar_difficulty[bar_index] += img_data.ix[j, 'difficulty_overall']
            
            median = index_generate_utils.mediannum(bar_time)
            all_recommended_time = int(all_bar/2)*median
            content = [StudioTestName, singleMediaName, "all_recommended_time", all_recommended_time]
            write_csv(file_name, content)
            
            all_actual_time = 0
            for j in range(len(bar_time)):
                all_actual_time += bar_time[j]
            difference = abs(all_actual_time - all_recommended_time)
            content = [StudioTestName, singleMediaName, "Rhythmic_stability", difference / all_recommended_time]
            write_csv(file_name, content)
            
            #根据乐谱每一小节的难度对总演奏长度进行切分
            all_difficulty = sum(bar_difficulty)
            single_recommended_time = []
            for j in range(int(all_bar/2)):
                single_recommended_time.append(all_recommended_time * bar_difficulty[j] / all_difficulty)
            
            #对所有bar的难度进行平均
            bar_difficulty_ave = all_difficulty / len(bar_difficulty)
            content = [StudioTestName, singleMediaName, "bar_difficulty_ave", bar_difficulty_ave]
            write_csv(file_name, content)
            media_difficulty.append(bar_difficulty_ave)
            
            #与演奏者的实际结果序列计算pearson系数
            pearson = pearsonr(single_recommended_time, bar_time)[0]
            print(pearson)
#            recommended_and_actual_time = [single_recommended_time, bar_time]
#            pearson = np.corrcoef(recommended_and_actual_time)[0][1]  #计算相关矩阵并提取皮尔森系数
            scaled_pearson = (pearson + 1) * 50  #将系数的范围转移到 0-100 区间
            content = [StudioTestName, singleMediaName, "Visual_stability", scaled_pearson]
            write_csv(file_name, content)
            
    #以图片为单位进行难度平均并写入
    media_difficulty_ave = sum(media_difficulty) / len(media_difficulty)
    content = [StudioTestName, "all", "media_difficulty", media_difficulty_ave]
    write_csv(file_name, content)
            
    
#左右手统合能力
def Left_and_right_hand_integration_ability(StudioTestName, file_path, file_name):
    eye_data = pd.read_csv(file_path, sep='\t', header=0, low_memory=False) #读入传入的tsv文件
    eye_data.fillna(0, inplace = True) #处理NaN值，直接在原数据中进行修改
    
    #对读入的tsv文件的MediaName列进行去重，筛选出所有的谱子名称
    raw_MediaName = eye_data['MediaName']
    MediaName = raw_MediaName.drop_duplicates(keep='first')  
    
    for i in range(0, len(MediaName)):
        #针对每一个谱子，查找对应的coordinate_info.csv文件
        singleMediaName = MediaName.iloc[i]
        
        if singleMediaName == 0:  #在处理原数据的时候把所有的NaN赋为了0
            continue
        else:
            img_path = search_img_path(singleMediaName[:-4]) #所有的后缀都是.jpg或者.PNG，长度一致
            if img_path == 0: #查找blank的返回值
                continue
            img_path = img_path[:-1] #去掉字符串结尾的'/n'
            
             #针对特定谱子的行，结合coordinate_info.csv文件判断含有眼睛焦点的小节数
            img_data = pd.read_csv(img_path)
            all_two_bar = img_data.shape[0] / 2 #小节的个数（每个小节包含低音高音）
            
            #在原眼动数据中筛选出含有singleMediaName的行
            eye_data_certain_MediaName = eye_data[eye_data['MediaName'].isin([singleMediaName])]
            
            #对FixedIndex进行去重
            eye_data_certain_MediaName_FixationIndex = eye_data_certain_MediaName.drop_duplicates(subset=['FixationIndex'], keep='first') 
            
            handover_times = 0 #计算总共视线切换的次数
            fomer_hand = 0 #0为初始值，-1左手低音，1右手高音
            for j in range(0, len(img_data)): #遍历每一个小节(分为高音和低音部分)
                for indexs in eye_data_certain_MediaName_FixationIndex.index:                    
                    if (img_data.ix[j, 'x_left']<=eye_data_certain_MediaName_FixationIndex.ix[indexs, 'FixationPointX (MCSpx)'] and 
                        img_data.ix[j, 'y_left']<=eye_data_certain_MediaName_FixationIndex.ix[indexs, 'FixationPointY (MCSpx)'] and
                        img_data.ix[j, 'x_right']>=eye_data_certain_MediaName_FixationIndex.ix[indexs, 'FixationPointX (MCSpx)'] and
                        img_data.ix[j, 'y_right']>=eye_data_certain_MediaName_FixationIndex.ix[indexs, 'FixationPointY (MCSpx)']):
                        #如果视线的焦点在该小节内
                        if fomer_hand == 0:#第一次聚焦到谱子
                            if img_data.ix[j, 'part_id'] == 0:#左手高音声部
                                fomer_hand = -1
                            else:  #右手低音声部
                                fomer_hand = 1
                        elif (fomer_hand == -1 and img_data.ix[j, 'part_id'] == 0): #视线未变化
                            continue
                        elif (fomer_hand == 1 and img_data.ix[j, 'part_id'] == 1): #视线未变化
                            continue
                        handover_times += 1
                    
            content = [StudioTestName, singleMediaName, 
                       "Left_and_right_hand_integration_ability", 
                       handover_times / all_two_bar]
            write_csv(file_name, content)
    
    
def Spectral_analysis_ability3_difference_between_treble_and_bass(StudioTestName, file_path, file_name):
    eye_data = pd.read_csv(file_path, sep='\t', header=0, low_memory=False) #读入传入的tsv文件
    eye_data.fillna(0, inplace = True) #处理NaN值，直接在原数据中进行修改
    
    #对读入的tsv文件的MediaName列进行去重，筛选出所有的谱子名称
    raw_MediaName = eye_data['MediaName']
    MediaName = raw_MediaName.drop_duplicates(keep='first')  
    
    for i in range(0, len(MediaName)):
        #针对每一个谱子，查找对应的coordinate_info.csv文件
        singleMediaName = MediaName.iloc[i]
        
        if singleMediaName == 0:  #在处理原数据的时候把所有的NaN赋为了0
            continue
        else:
            img_path = search_img_path(singleMediaName[:-4]) #所有的后缀都是.jpg或者.PNG，长度一致
            if img_path == 0: #查找blank的返回值
                continue
            img_path = img_path[:-1] #去掉字符串结尾的'/n'
            
             #针对特定谱子的行，结合coordinate_info.csv文件判断含有眼睛焦点的小节数
            img_data = pd.read_csv(img_path)
            all_bar = img_data.shape[0]
            
            #在原眼动数据中筛选出含有singleMediaName的行
            eye_data_certain_MediaName = eye_data[eye_data['MediaName'].isin([singleMediaName])]
            
            #记录每一小节的凝视时数(区分高音低音声部)
            bar_time = [0 for t in range(int(all_bar))]
            
            for j in range(0, len(img_data)): #遍历每一个小节(分为高音和低音部分)
                for indexs in eye_data_certain_MediaName.index:                    
                    if (img_data.ix[j, 'x_left']<=eye_data_certain_MediaName.ix[indexs, 'FixationPointX (MCSpx)'] and 
                        img_data.ix[j, 'y_left']<=eye_data_certain_MediaName.ix[indexs, 'FixationPointY (MCSpx)'] and
                        img_data.ix[j, 'x_right']>=eye_data_certain_MediaName.ix[indexs, 'FixationPointX (MCSpx)'] and
                        img_data.ix[j, 'y_right']>=eye_data_certain_MediaName.ix[indexs, 'FixationPointY (MCSpx)']):
                        #如果视线的焦点在该小节内
                        #计算凝视时间
                        bar_time[j] = eye_data_certain_MediaName.ix[indexs, 'GazeEventDuration']
                        break
            
            sum_high_time = 0
            sum_low_time = 0
            for j in range(len(bar_time)):
                if j % 2 == 0:
                    sum_high_time += bar_time[j]
                else:
                    sum_low_time += bar_time[j]
            median = index_generate_utils.mediannum(bar_time) #注意这里的中位数是区分高音低音部分的
            difference_rate = abs(sum_high_time - sum_low_time) / median
            content = [StudioTestName, singleMediaName, "Spectral_analysis_ability3", difference_rate]
            write_csv(file_name, content)
    
    
#主函数
if __name__=='__main__':
    #防止多次运行在文件中出现重复的路径
    if os.path.isfile("image_file.txt"):
        os.remove("image_file.txt")
    if os.path.isfile("eye_tracking_file.txt"):
        os.remove("eye_tracking_file.txt")
        
    #将所有的图片和tsv文件路径存到一个txt文件夹里面
    image_path = "..\..\images_cut_finished"
    eye_tracking_path = "..\..\sjt-eye-tracking-project"
    Traversal_file(image_path, "image_file.txt")
    Traversal_file(eye_tracking_path, "eye_tracking_file.txt")
    
    #对于tsv文件进行遍历
    #先筛选出所有被测试的名称
    StudioTestName = [#'B test4',
                      'Btest_new3',
                      'Btest_new6',
                      'C test3',
                      'C test4',
                      'C test5',
                      'C test6',
                      'French_test1',
                      'French_test2',
                      'French_test3',
                      'French_test4',
                      'French_test5'
                      ]
    
    for test_name in StudioTestName:
        #查找对应的tsv和图片文件
        tsv = open("eye_tracking_file.txt")
        tsv_line = tsv.readline()
        while tsv_line:
            index = tsv_line.find(test_name)
            if index != -1: #找到包含对应测试名称的tsv文件
                #截取测试的名称与记录名称并创立csv文件
                test_record = tsv_line[index:len(tsv_line)-5]
                create_csv(test_record)
                
                #进行指标的计算
#                Music_score_reading_completeness(test_name, tsv_line[:-1], test_record)
#                Bass_part_reading_completeness(test_name, tsv_line[:-1], test_record)
#                Left_and_right_hand_integration_ability(test_name, tsv_line[:-1], test_record)
                Visual_stability_and_rhythmic_stability(test_name, tsv_line[:-1], test_record)
#                Spectral_analysis_ability3_difference_between_treble_and_bass(test_name, tsv_line[:-1], test_record)
            tsv_line = tsv.readline()
        tsv.close()
    
    
#    tsv = open("eye_tracking_file.txt")
#    tsv_line = tsv.readline()
#    while tsv_line:
#        print (tsv_line)
#        读入tsv，并且存到dict里面
#        eye_data = pd.read_csv(tsv_line[:-1], sep='\t', header=0, error_bad_lines = False)
#        print (eye_data)
#        
#        抽取测试名称，作为分析的单位(先行手动输入)
#        name = eye_data.loc[1, 'StudioTestName']
#        if name in eye_data.keys():
#            continue
#        else:
#            StudioTestName[eye_data.loc[1, 'StudioTestName']] = []
#            print(name)
#            
#        tsv_line = tsv.readline()
#    tsv.close()