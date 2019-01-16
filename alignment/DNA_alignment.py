import numpy as np
from scipy import *
from pylab import *
import librosa
import matplotlib.pyplot as plt
from librosa import display
import math


def cost_function(vec1, vec2):
    # vec1 = vec1 + 80
    # vec2 = vec2 + 80
    return np.sqrt(np.sum(np.square(vec1 - vec2)))


def force_align(test, template):
    test_length = test.shape[1]
    template_length = template.shape[1]
    cost_map = np.zeros((template_length, test_length))
    path_map = np.zeros((template_length, test_length))
    path_map[0][0] = -1

    # 可以跳任意步长
    for i in range(0, template_length):
        for j in range(0, test_length):
            if i == j and i == 0:
                continue
            cost = cost_function(test[:, j], template[:, i])
            costs = np.zeros(3)
            if i > 0:
                costs[0] = cost + cost_map[i - 1][j]
            else:
                costs[0] = float("inf")
            if j > 0:
                costs[2] = cost + cost_map[i][j - 1]
            else:
                costs[2] = float("inf")
            if j > 0 and i > 0:
                costs[1] = cost + cost_map[i - 1][j - 1]
            else:
                costs[1] = float("inf")

            cost_index = np.where(costs == np.min(costs))[0][0]
            cost_map[i][j] = costs[cost_index]
            path_map[i][j] = cost_index

    print(path_map)
    print(cost_map)
    result_list = []
    current_index = template_length - 1
    for j in range(0, test_length):
        index = int(test_length - j - 1)

        result_list.append(current_index)
        while path_map[current_index][index] == 0:
            current_index -= 1
        if path_map[current_index][index] == 1:
            current_index -= 1
        else:
            continue
    print(result_list)
    print(cost_map[-1][-1])


if __name__ == "__main__":
    # test data
    y, sr = librosa.load("e_2-15.wav")
    y = librosa.resample(y, sr, 16000)
    CQT = librosa.amplitude_to_db(np.abs(librosa.cqt(y, sr=sr, hop_length=1600)), ref=np.max)

    # template data
    y, sr = librosa.load("test-15.wav")
    y = librosa.resample(y, sr, 16000)
    CQT_test = librosa.amplitude_to_db(np.abs(librosa.cqt(y, sr=sr, hop_length=1600)), ref=np.max)
    print(CQT.shape)
    print(CQT_test.shape)
    print("force_align")
    force_align(CQT, CQT_test)


