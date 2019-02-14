import os
import csv


skip_info = ['\ufeffExportDate', 'StudioVersionRec', 'StudioProjectName',
               'RecordingDate', 'PresentationSequence', 'FixationFilter',
               'SegmentName', 'SegmentStart', 'SegmentEnd', 'SegmentDuration', 'SceneName',
               'SceneSegmentStart', 'SceneSegmentEnd', 'SceneSegmentDuration',
               'MouseEventIndex', 'MouseEvent', 'MouseEventX (ADCSpx)',
               'MouseEventY (ADCSpx)', 'MouseEventX (MCSpx)', 'MouseEventY (MCSpx)',
               'KeyPressEventIndex', 'KeyPressEvent', '']


def UsefulDetermine(file_pre, file_name):
    preffix = "../data/eye-tracking/"
    with open(file_pre + file_name, "r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter="\t")
        writer = csv.writer(open(preffix + file_name, "w", encoding="utf-8", newline=''))
        title = next(reader)
        skip = []
        out = []
        for i in range(len(title)):
            if title[i] in skip_info:
                skip.append(i)
            else:
                out.append(title[i])
        writer.writerow(out)
        for row in reader:
            useful_info = []
            for i in range(len(row)):
                if i not in skip:
                    useful_info.append(row[i])
            writer.writerow(useful_info)





#精简现有数据（原始导出格式存在很多冗余）
if __name__ == "__main__":
    data = os.listdir("../../sjt-eye-tracking-project")
    for part in data:
        print(part)
        if part[-1] == "x" or part in finished:
            continue
        UsefulDetermine("../../sjt-eye-tracking-project/", part)
