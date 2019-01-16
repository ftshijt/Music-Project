# -*- coding: utf-8 -*-
import librosa
import numpy as np
import math


def Extract_mfcc(filepath):
    y, sr = librosa.load(filepath,sr=None) #sr:采样率
    y = librosa.resample(y, sr, 16000)      #把所有的音频采样率降到16000
    mfccs = librosa.feature.mfcc(y=y, sr=sr,n_mfcc=24)
    i = 0
    print(np.shape(mfccs))

    # 通过设定绝对阈值判断音是否为静音状态
    while i < np.shape(mfccs)[0]:
        if mfccs[1,i] < 1e-10:
            mfccs = np.delete(mfccs, i, axis=1)
        else:
            i = i + 1
    return mfccs


def Euclidean_Distance(A, B):
    return np.sqrt(np.sum(np.square(A-B))) 


# 通过之前的标注，递归记录最佳的路径
def Find_best_path(path,i,j, best_path):
    if i == 0 and j == 0:
        best_path.reverse()
        return
    else:
        if path[i,j] == 1:
            best_path.append(1)
            Find_best_path(path, i, j-1, best_path)
        elif path[i,j] == 2:
            best_path.append(2)
            Find_best_path(path, i-1, j-1, best_path)
        elif path[i,j] == 3:
            best_path.append(3)
            Find_best_path(path, i-1, j, best_path)


def BestLoss_DP(y_template, y_input, compare_choice):
    row = np.shape(y_template)[1]
    column = np.shape(y_input)[1]
    dists = np.zeros(shape=(row, column))
    path = np.zeros(shape=(row, column))
    for i in range(row):
        for j in range(column):
            dists[i,j] = Euclidean_Distance(y_template[:,i], y_input[:,j])
        
    for i in range(1, column):                      #special action for 1st line
        dists[0,i] = dists[0,i-1] + dists[0,i]
        path[0,i] = 1
        
    dists[1,1] = dists[0,0] + dists[1,1]            #special action for 2nd line
    path[1,1] = 2
    for i in range(2, column):
        dists[1,i] = dists[1,i] + min(dists[1,i-1], dists[0,i-1])
        if dists[1,i-1] == min(dists[1,i-1], dists[0,i-1]):
            path[1,i] = 1
        elif dists[0,i-1] == min(dists[1,i-1], dists[0,i-1]):
            path[1,i] = 2
            
    for i in range(2, row):
        j_begin = math.ceil(i/2)                    #special action for 1st element in every line
        if i % 2 == 0:
            dists[i, j_begin] = dists[i, j_begin] + dists[i-2, j_begin-1]
            path[i, j_begin] = 3
        elif i % 2 == 1:
            dists[i, j_begin] = dists[i, j_begin] + min(dists[i-1, j_begin-1], dists[i-2, j_begin-1])
            if dists[i-1, j_begin-1] == min(dists[i-1, j_begin-1], dists[i-2, j_begin-1]):
                path[i, j_begin] = 2
            elif dists[i-2, j_begin-1] == min(dists[i-1 ,j_begin-1], dists[i-2, j_begin-1]):
                path[i, j_begin] = 3
        for j in range(j_begin+1, column):
            dists[i,j] = dists[i,j] + min(dists[i,j-1], dists[i-1,j-1], dists[i-2,j-1])
            if dists[i-1,j-1] == min(dists[i,j-1], dists[i-1,j-1], dists[i-2,j-1]):
                path[i,j] = 2   # turn right and up
            elif dists[i,j-1] == min(dists[i,j-1], dists[i-1,j-1], dists[i-2,j-1]):
                path[i,j] = 1   # turn right
            else:
                path[i,j] = 3   # turn up
                
    best_path = []
    Find_best_path(path, row-1, column-1, best_path)
    
    return dists[row-1,column-1], best_path


def Make_average_template_DTW(template, template_input, path):
    template_input_num = len(path)
    index_max = np.shape(template)[1]               #template中mfcc特征的个数
    res = np.zeros(shape=(24, index_max))
    average_num = np.ones(shape=(1, index_max))     #每个桶里mfcc特征的个数，之后算平均用
    for i in range(index_max):
        res[:,i] = template[:,i]                    #先在桶中放入原来的template,之后根据路径，将template_input放入其中
    
    for template_index in range(template_input_num):            #every template
        i = 0
        j = 0
        for path_index in range(len(path[template_index])):
            if path[template_index][path_index] == 2:
                res[:,i] = res[:,i] + template_input[template_index][:,j]
                average_num[0][i] = average_num[0][i] + 1
                i = i + 1                                       #all pointers refer to the action willing to do(所有指针指向将要操作的对象)
                j = j + 1
            elif path[template_index][path_index] == 1:
                res[:,i] = res[:,i] + template_input[template_index][:,j]
                average_num[0][i] = average_num[0][i] + 1
                j = j + 1
            else:
                res[:,i] = res[:,i] + template_input[template_index][:,j]   
                average_num[0][i] = average_num[0][i] + 1                   
                i = i + 1
                
    for index in range(index_max):
        res[:,index] = res[:,index] / average_num[0][index]
    return res


if __name__ == '__main__':
    filepath_template = 'implemented-data/test-15.wav'
    filepath_input = []
    
    for i in range(4):                                             
        url = 'implemented-data/e_'+str(i)+'-15.wav'    #将样本集存入路径
        filepath_input.append(url)
    for i in range(5):                                             
        url = 'implemented-data/fang_'+str(i)+'-15.wav'    #将样本集存入路径
        filepath_input.append(url)
    for i in range(5):
        url = 'implemented-data/gong_'+str(i)+'-15.wav'    #将样本集存入路径
        filepath_input.append(url)
    
    y_template = Extract_mfcc(filepath_template)
    #
    #
    # y_input = []
    # dists_res = []
    # for i in range(14):
    #     y_input.append(Extract_mfcc(filepath_input[i]))
    #     dists, path_tmp = BestLoss_DP(y_template, y_input[i], 'Euclidean')
    #     print(i, dists)
    #     dists_res.append(dists)
    # index_best = np.argmin(dists_res)
    # print('index_best:{}, file_path:{}'.format(index_best, filepath_input[index_best]))
















    



    
    
    
