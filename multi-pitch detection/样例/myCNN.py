#!/usr/bin/python3
from PIL import Image
import os
import librosa
import numpy as np
import torch
import torch.nn as nn
import torch.utils.data as Data
import torch.nn.functional as F
import random
import pickle


class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Sequential(
            nn.Conv2d(in_channels=3, out_channels=16, kernel_size=5, stride=3, padding=2),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2),
        )
        self.conv2 = nn.Sequential(
            nn.Conv2d(in_channels=16, out_channels=32, kernel_size=5, stride=2, padding=2),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2),
        )
        self.hidden = nn.Linear(12 * 12 * 32, 128)
        self.out = nn.Sequential(
            nn.Linear(128, 4),
        )

    def forward(self, X):
        X = self.conv1(X)
        X = self.conv2(X)
        X = X.view(X.size(0), -1)  #将前面多维度的tensor展平成一维
        V = self.hidden(X)  #展成128维的向量
        X = self.out(V)  #获得四位向量
        return X, V


class Solver(object):
    def train(self, X, y):
        loader = Data.DataLoader(dataset=Data.TensorDataset(X, y),
                                 batch_size=50,
                                 shuffle=True,
                                 num_workers=4)

        self.net = CNN()
        self.optimizer = torch.optim.Adam(self.net.parameters(), lr=0.0001)
        self.loss_func = nn.CrossEntropyLoss()

        for epoch in range(100):
            for step, (batch_X, batch_y) in enumerate(loader):
                out, V = self.net(batch_X)
                loss = self.loss_func(out, batch_y)
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
                if step % 50 == 0:
                    print("loss =", loss.data.numpy())
            with open('model%d.txt' % (epoch+1), 'wb') as f: #将模型保存下来
                pickle.dump(self.net, f)

    def score(self, X, y):
        out, V = self.net(X)
        predict = torch.argmax(F.softmax(out, dim=1), dim=1)
        pred_y = predict.data.numpy().squeeze()
        print("Acc = %.6f" % (np.mean(pred_y == y)))


def get_data(file1, file2):
    # 提取wav文件的特征
    y, sr = librosa.load(file1, sr=16000)
    spec = np.abs(librosa.stft(y, n_fft=256, win_length=256, hop_length=96))

    # 读取wav文件对应的音符序列
    f2 = open(file2)
    chart = []
    line = f2.readline()
    while (line):
        t_line = line[1:-3]
        result = t_line.split('. ')
        chart.append(np.array(result))
        line = f2.readline()
    f2.close()

    # wav文件后面可能会有空白的部分，用为0向量去填补chart
    delta = spec.shape[1] - len(chart)
    if (delta > 0):
        for i in range(delta):
            chart.append(np.zeros(128))
    # else:
    #     for i in range(abs(delta)):
    #         chart.append(np.zeros(1, ))

    # 对spec进行转置
    spec_t = spec.T

    # 随机抽取100个进行训练
    A = 0;  # 最小随机数
    B = spec_t.shape[0]-1  # 最大随机数
    COUNT = 100
    resultList = random.sample(range(A, B + 1), COUNT)
    spec_t_result = np.zeros(shape=(COUNT,129))
    chart_result = np.zeros(shape=(COUNT,128))
    count = 0
    for i in resultList:
        spec_t_result[count]=spec_t[i]
        chart_result[count]=chart[i]
        count+=1

    return spec_t_result, chart_result


if __name__ == '__main__':
    X_train, X_test, y_train, y_test = [], [], [], []
    for f in os.listdir('./训练原数据(wav)'):
        if f[-3:] != 'wav':
            continue
        file1 = os.path.join('./训练原数据(wav)', f)
        file2 = './标记数据'+file1[12:-3]+'txt'

        if (not os.path.exists(file2)):
            continue
        print(file1)
        print(file2)

        file_X, file_y = get_data(file1, file2)
        t_random = random.random()
        print(t_random)
        if t_random <= 0.6:  #随机按照比例选取训练集和测试集
            print('train\n-----')
            X_train.append(file_X)
            y_train.append(file_y)
        else:
            print('test\n-----')
            X_test.append(file_X)
            y_test.append(file_y)

    X_train = torch.FloatTensor(X_train)
    y_train = torch.LongTensor(y_train)
    X_test = torch.FloatTensor(X_test)
    y_test = np.array(y_test)

    solver = Solver()
    solver.train(X_train, y_train)
    solver.score(X_test, y_test)