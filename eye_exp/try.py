# -*- coding: utf-8 -*-
"""
@author: GS_qbr
"""

import os

def Traversing_dir(folder_name):    #根据后缀名,遍历文件夹删除文件
    #遍历根目录
    for root,dirs,files in os.walk(folder_name):
        for file in files:
            #文件后缀名
            extFile=os.path.splitext(file)[1]
            if extFile==".png":
                os.remove(os.path.join(root,file))    #删除文件
        for dir in dirs:
            #递归调用自身
            Traversing_dir(dir)

def Folder_check(folder_name):      #文件夹没有就新建，有就清空文件
    curPath=os.getcwd()
    targetPath=curPath+os.path.sep+folder_name
    if not os.path.exists(targetPath):
        os.makedirs(targetPath)
    else:
        Traversing_dir(folder_name)
        
        
        
        
