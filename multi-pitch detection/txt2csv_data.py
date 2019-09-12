import csv
import os

def instrumentdic(inst_file_path):
    #返回instrument字典，数据结构为int:"str"
    dic={}
    with open(inst_file_path)as file:
        datas=file.readlines()
    for data in datas:
        line=data.strip() #去掉头尾的空格与回车
        line=line.split(" ")
        num=int(line[0])
        inst=""
        for i in range(len(line)):
            if(i==0):
                continue
            else:
                inst+=line[i]+" "
        dic[num]=inst
    return dic

instdic=instrumentdic('./instrumentdic.txt')

def create_csv(file_name):
    with open(file_name, 'w+', newline="") as f:
        csv_write = csv.writer(f)
        csv_head = ["track",
                    "instrument",
                    "start_time",
                    "end_time",
                    "note_type",
                    "note_strength"
                    ]
        csv_write.writerow(csv_head)


def tet2csv_data(file_path, store_path):
    if_null = True
    create_csv(store_path)
    TPQ = 0
    track=0 # 若只有1个track则显示0
    instrument="" # 乐器种类
    single_tick_time = 0 # 单位为s
    with open(store_path, 'a+', newline='') as csv_f:
        csv_write = csv.writer(csv_f)
        raw_row = []
        with open(file_path) as txt_f:
            line = txt_f.readline()
            while line:
                # 遇到空行
                if (line[0] == '\n'):
                    line = txt_f.readline()
                    continue
                if (line[-2]==' ' and line[-1]=='\n'):
                    line = line[:-2] # 去掉最后的' '与'\n'
                else:
                    line = line[:-1]
                # print(line, end = '')
                # 提取TPQ
                if (line[0:3]=="TPQ"):
                    print(line)
                    TPQ = int(line[4:])
                # 去掉无意义行
                if (line[0] == 'T' or line[0] == '_'):
                    line = txt_f.readline()
                    continue
                # 根据'\t'分割
                # all_data对应的数据有两种
                # 一种是非midi事件
                # 另一种是midi事件，为开始时间、事件间隔数、轨道数、事件内容
                all_data = line.split('\t')
                # print(all_data)

                # 对于头信息进行先行的判断
                # 把事件种类提取出来
                event_type = all_data[3][0:2]
                # 如果是非MIDI事件
                if event_type == "ff":
                    part_data = all_data[3].split(' ')
                    if part_data[1] == '51':
                        num_16 = ''
                        for i in part_data[3:]:
                            if (len(i)==1): # 为单独的数字加0
                                num_16 += '0'
                            num_16 += i
                        num_10 = int(num_16,16)
                        print('num_16', num_16)
                        print('num_10', num_10)
                        single_tick_time = num_10/(TPQ*1000*1000)
                        print(TPQ)
                        print('single_tick_time', single_tick_time)
                    elif part_data[1] == '4':
                        instrument = part_data[3:]
                        inst=""
                        for i in part_data[3:]:
                            inst+=chr(int(i,16))
                        #print(instrument)
                        if(inst[:4]=="Inst"):
                            instrument=instdic[int(inst[5:])]
                        else:
                            instrument=inst
                        #print(instrument)
                else: # 如果是MIDI事件
                    part_data = all_data[3].split(' ')
                    if (part_data[0][0]=='9'): # 如果是按下音符的事件
                        # print(part_data)
                        row = []
                        # "track" 0
                        row.append(str(track))
                        # "instrument" 1
                        row.append(str(instrument))
                        # "start_time" 2
                        start_time = float(all_data[0])*single_tick_time
                        row.append(str(start_time))
                        # "end_time" 3 该数据为0，之后会被修正覆盖
                        row.append('0')
                        # "note_type" 4
                        row.append(str(part_data[1]))
                        # "note_strength 5
                        row.append(str(part_data[2]))

                        raw_row.append(row)
                        # csv_write.writerow(row)
                    elif (part_data[0][0]=='8'):
                        count = 0
                        for row in raw_row:
                            if (str(part_data[1]) == row[4]):
                                if (str(part_data[2]) == row[5]):
                                    # 修改end_time
                                    end_time = float(all_data[0]) * single_tick_time
                                    row[3] = str(end_time)
                                    csv_write.writerow(row)
                                    if_null = False
                                    raw_row.pop(count)
                            count += 1

                line = txt_f.readline()
    if (if_null):
        os.remove(store_path)
    # print(tick)

if __name__ == '__main__':
    for f in os.listdir('./样例/标记数据(txt)'):
        if f[-3:] != 'txt':
            continue
        file1 = os.path.join('./样例/标记数据(txt)', f)
        file2 = './样例/标记数据(csv)'+file1[14:-3]+'csv'
        print(file1)
        print(file2)
        tet2csv_data(file1, file2)
    # tet2csv_data('./样例/标记数据(txt)/1a0b97ea56d84ab9b74bbf9e8104bd93.txt', './样例/标记数据(csv)/1a0b97ea56d84ab9b74bbf9e8104bd93.csv')