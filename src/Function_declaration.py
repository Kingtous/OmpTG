# <OmpTG>  Copyright (C) <2021>  < Tao Jin; Jinrong Liu; >
# This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
# This is free software, and you are welcome to redistribute it
# under certain conditions; type `show c' for details.
import os
import re as r
import sys


def getFunctionDeclaration(func_list):
    '''

    :param func_list:alf文件中所有func的集合
    :return: 每个func前的函数申明
    '''
    declaration_dict = {}
    for i in range(0, len(func_list)):
        func_data = func_list[i]
        flag_1 = 'label'
        label_start_place = func_data.find(flag_1)
        label_start_place = func_data.find(flag_1, label_start_place + 4)  # 找到第二个"label"
        label_end_place = 0
        for j in range(0, label_start_place):  # 找到第二个"label"前的第一个"{"
            if func_data[label_start_place - j] == '{':
                label_end_place = label_start_place - j
                break
        flag_2 = '"'
        name_start_place = func_data.find(flag_2)
        name_end_place = func_data.find(flag_2, name_start_place + 1)
        declaration_name = func_data[name_start_place + 1:name_end_place]
        declaration_dict[declaration_name] = func_data[0:label_end_place]
        func_list[i] = func_data[label_end_place:]

    return declaration_dict
