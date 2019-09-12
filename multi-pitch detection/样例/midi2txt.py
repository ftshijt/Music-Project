#!/usr/bin/python3
import os
from music21 import converter, instrument, note, chord, stream

def get_nodes(file_path):
    stream = converter.parse(file_path)

    # 获取乐器
    print('parts:')
    parts = instrument.partitionByInstrument(stream)
    # 输出所有乐器
    for i in parts:
        print(i)

    # 音调信息
    print('notes:')
    note_list = []
    notes = parts.parts[0].recurse()
    for i in notes:
        print(i)
        if isinstance(i, note.Note):
            # 音调
            print(i.pitch)
            note_list.append(str(i.pitch))
        elif isinstance(i, chord.Chord):
            print(i.normalOrder)
            note_list.append('.'.join(
                map(str,
                    i.normalOrder)
            ))
        print('---\n')

    for i in note_list:
        print(i)
    return note_list


def create_music(prediction):
    # 音符之间是有间距的,每次加上一个值，表示间隔时间
    # 间隔越小，节奏越快
    offset = 0
    output_notes = []

    # 生成Note和Chord
    for data in prediction:
        if '.' in data or str(data).isdigit():
            # 和弦
            note_list = []
            for i in data.split('.'):
                new_note = note.Note(int(i))
                new_note.storedInstrument = instrument.Piano()
                # new_note.storedInstrument = instrument.Guitar()
                note_list.append(new_note)
            new_chord = chord.Chord(note_list)
            new_chord.offset = offset
            output_notes.append(new_chord)
        else:
            print('d:', data)
            new_note = note.Note(data)
            new_note.offset = offset
            new_note.storedInstrument = instrument.Piano()
            # new_note.storedInstrument = instrument.Guitar()
            output_notes.append(new_note)
            # 每次 迭代增加偏移，这样不会覆盖和迭代

        offset += .5
    # 创建流写入文件
    mini_stream = stream.Stream(output_notes)
    mini_stream.write('midi', fp='out4.mid')




if __name__ == '__main__':
    # for f in os.listdir('./训练原数据(mid)'):
    #     if f[-3:] != 'mid':
    #         continue
    #     file1 = os.path.join('./训练原数据(mid)', f)
    #     file2 = './标记数据'+file1[12:-3]+'txt'
    #     note_list = get_nodes(file1)
    #     print(note_list)
    #     create_music(note_list)

    note_list = get_nodes(r'./训练原数据(mid)/1a0b35079fd7d1e6d007e59f923643f4.mid')
    print(note_list)
    create_music(note_list)
