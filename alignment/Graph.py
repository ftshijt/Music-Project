#encoding=utf-8

import wave
import struct
from scipy import *
from pylab import *
import librosa
import matplotlib.pyplot as plt
from librosa import display


# 读取wav文件，我这儿读了个自己用python写的音阶的wav
filename = 'test.wav'
wavefile = wave.open(filename, 'r')  # open for writing

plt.figure(figsize=(2,1))
#
# # 读取wav文件的四种信息的函数。期中numframes表示一共读取了几个frames，在后面要用到滴。
# nchannels = wavefile.getnchannels()
# sample_width = wavefile.getsampwidth()
# framerate = wavefile.getframerate()
# numframes = wavefile.getnframes()
#
# print("channel", nchannels)
# print("sample_width", sample_width)
# print("framerate", framerate)
# print("numframes", numframes)
#
# # 建一个y的数列，用来保存后面读的每个frame的amplitude。
# y = zeros(numframes)
#
# # for循环，readframe(1)每次读一个frame，取其前两位，是左声道的信息。右声道就是后两位啦。
# # unpack是struct里的一个函数，用法详见http://docs.python.org/library/struct.html。简单说来就是把＃packed的string转换成原来的数据，无论是什么样的数据都返回一个tuple。这里返回的是长度为一的一个
# # tuple，所以我们取它的第零位。
# for i in range(numframes):
#     val = wavefile.readframes(1)
#     left = val[0:2]
#     # right = val[2:4]
#     v = struct.unpack('h', left)[0]
#     y[i] = v
#
# # framerate就是44100，文件初读取的值。然后本程序最关键的一步！specgram！实在太简单了。。。
# Fs = framerate
# specgram(y, NFFT=1024, Fs=Fs, noverlap=900)
# print(specgram)
# show()
y, sr = librosa.load("test-15.wav")
y = librosa.resample(y, sr, 22050)
# print(y.shape)
# print(sr)
# S = librosa.feature.melspectrogram(y=y, n_mels=128, n_fft=1024, hop_length=160)
# print(S.shape)
# C = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=128)
# plt.figure()
# display.specshow(C, y_axis='chroma')
# print(C.shape)
# plt.colorbar()
# plt.title('Chromagram')
# plt.show()

CQT = librosa.amplitude_to_db(np.abs(librosa.cqt(y, sr=sr, hop_length=320)), ref=np.max)
plt.subplot(2,1,1)
librosa.display.specshow(CQT, y_axis='cqt_note')
plt.colorbar(format='%+2.0f dB')
plt.title('Constant-Q power spectrogram (note)')



y, sr = librosa.load("e_2-15.wav")
y = librosa.resample(y, sr, 22050)
# print(y.shape)
# print(sr)
# S = librosa.feature.melspectrogram(y=y, n_mels=128, n_fft=1024, hop_length=160)
# print(S.shape)
# C = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=128)
# plt.figure()
# display.specshow(C, y_axis='chroma')
# print(C.shape)
# plt.colorbar()
# plt.title('Chromagram')
# plt.show()

CQT_test = librosa.amplitude_to_db(np.abs(librosa.cqt(y, sr=sr, hop_length=320)), ref=np.max)
plt.subplot(2,1,2)
librosa.display.specshow(CQT_test, y_axis='cqt_note')
plt.colorbar(format='%+2.0f dB')
plt.title('Constant-Q power spectrogram (note)')
plt.show()

print(CQT_test.shape)
print(CQT.shape)