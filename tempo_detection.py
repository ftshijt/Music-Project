# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 17:05:47 2019

@author: GS-qbr
"""

import librosa
import numpy as np
import matplotlib.pyplot as plt
import librosa.display
import math
from sklearn.cluster import KMeans


if __name__ == '__main__':
    
    filepath = 'test.mp3'    
    y, sr = librosa.load(filepath,sr=None) #sr:采样率
    
    # pitch detection
    n_fft_input = 2048
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr, n_fft=n_fft_input)
    
    n_frame = np.shape(magnitudes)[1]
    pitch = np.zeros(n_frame)
    pitch2frames = []   #记录每个音持续了多少个frame
    begin_index = 0
    temp = 0
    for t in range(n_frame):
        index = magnitudes[:, t].argmax()
        pitch[t] = pitches[index, t]
        
        if np.abs(pitch[begin_index] - pitch[t]) > pitch[begin_index] * 0.3:    #当前frame为一个新的音  
            pitch2frames.append(temp)
            temp = 1    # 记录当前音的次数
            begin_index = t
        else:   #当前frame与begin_index指向的音为同一个
            temp = temp + 1
    pitch2frames.append(temp)   #把数组最后的结果压入
    
    time_per_frame = (n_fft_input/4) / sr
    pitch2time = np.zeros(len(pitch2frames))    #记录每个音持续了多长时间
    for index in range(len(pitch2time)):
        pitch2time[index] = pitch2frames[index] * time_per_frame
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    