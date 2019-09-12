import os
import pandas as pd
import numpy as np

np.set_printoptions(linewidth=400) # 防止numpy数组str后自动换行

if __name__ == '__main__':
    sr = 16000
    n_fft = 256
    hop_length = 96
    wide = n_fft / sr
    stride = hop_length / sr
    for f in os.listdir('./标记数据(csv)'):
        if f[-3:] != 'csv':
            continue
        file1 = os.path.join('./标记数据(csv)', f)
        df = pd.read_csv(file1, sep=',')
        # 寻找最大的时间
        max_time = np.max(df['end_time'])
        if (np.isnan(max_time)):
            continue
        print(file1[12:-3])
        file2 = './标记数据/'+file1[12:-3]+'txt'
        with open(file2, 'w+') as f_txt:
            start = 0
            end = wide
            while (end < max_time):
                # 一共有128种音符，定义一个一维向量
                note = np.zeros(128)
                context = [0]
                for row in df.head().itertuples():
                    if (row.end_time>start or row.start_time<end):
                        note_order = int(row.note_type, 16)
                        note[note_order] = 1
                f_txt.write(str(note)+'\n')
                start += stride
                end += stride
