import os
import re as r
# <OmpTG>  Copyright (C) <2021>  < Tao Jin; Jinrong Liu; >
# This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
# This is free software, and you are welcome to redistribute it
# under certain conditions; type `show c' for details.
import sys


def deleteNote(func_list):
    '''

    :param func_list: 所有Func的集合（含注释）
    :return: 所有Func的集合（不含注释）
    '''
    for i in range(0, len(func_list)):
        func_data = func_list[i]
        start_flag = '/*'
        end_flag = '*/'
        start_place = 0
        end_place = 0
        start_place = func_data.find(start_flag)
        while start_place != -1:
            end_place = func_data.find(end_flag, start_place)
            func_data = func_data[:start_place] + func_data[end_place + 2:]
            start_place = func_data.find(start_flag, end_place)
        start_place = func_data.find(start_flag)
        while start_place != -1:
            end_place = func_data.find(end_flag, start_place)
            func_data = func_data[:start_place] + func_data[end_place + 2:]
            start_place = func_data.find(start_flag, end_place)

        func_list[i] = func_data
