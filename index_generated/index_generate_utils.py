# -*- coding: utf-8 -*-
"""
@author: zhangtg
"""

#计算中位数
def mediannum(listnum):
    #先去除为0的项
    for item in listnum[:]:
        if item == 0:
            listnum.remove(item)
    #返回中位数
    if len(listnum) == 0:
        return 0
    return sorted(listnum)[int(len(listnum) / 2)]