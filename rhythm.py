# -*- coding: utf-8 -*-
"""
Created on Sun Jul 21 22:39:32 2019

@author: yaolinli
"""

import librosa
from pygame import *
import matplotlib.pyplot as plt
import librosa.display

'读取音频'
y, sr = librosa.load('music1.wav', sr=16000)
#y, sr = librosa.load('music.mp3',sr=None)
maxframe = max(y)

'''
'设置一个阈值，暴力去除部分噪音'
for idx, yi in enumerate(y):
    if abs(yi) < maxframe/5:
        y[idx] = 0
'''

'检测每个音符的起始点'
onsets_frames = librosa.onset.onset_detect(y)
'将获得的帧号转换成对应的时间点'
onsets_times = librosa.frames_to_time(onsets_frames)



oenv = librosa.onset.onset_strength(y=y)
onsets_bt = librosa.onset.onset_backtrack(onsets_frames, oenv)
onsets_bt_times = librosa.frames_to_time(onsets_bt)

'画频谱图'
D = librosa.stft(y)
librosa.display.specshow(librosa.amplitude_to_db(D))
#plt.vlines(onsets_frames, 0, sr, color='r', linestyle='--')
plt.vlines(onsets_bt, 0, sr, color='b', linestyle='--')
plt.show()

'可视化'
'''
librosa.display.waveplot(y)
plt.vlines(onsets_times, -maxframe, maxframe, color='r', linestyle='--')
plt.show()
'''
librosa.display.waveplot(y)
plt.vlines(onsets_bt_times, -maxframe, maxframe, color='b', linestyle='--')
plt.show()

for i, t in enumerate(onsets_bt_times):
    print('第%d个音符的开始时间:'%i, t)
    