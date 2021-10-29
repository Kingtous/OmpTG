# <OmpTG>  Copyright (C) <2021>  < Tao Jin; Jinrong Liu; >
# This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
# This is free software, and you are welcome to redistribute it
# under certain conditions; type `show c' for details.
import os
import re as r


def readALF(Data):
    '''

    :param Data:alf文件名
    :return: alf文件（一个长字符串）
    '''
    alfdata = ''
    data_path = Data
    data = open(data_path, 'r')
    # body=open(data_path+ '.txt', 'w')
    line = data.readline()
    # 直到读取完文件
    while line:
        if line[-1] != '\n':
            alfdata = alfdata + line
        else:
            alfdata = alfdata + line[:-1]
        # 读取一行文件，包括换行符
        line = data.readline()

    data.close()

    return alfdata
