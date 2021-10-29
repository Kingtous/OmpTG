# <OmpTG>  Copyright (C) <2021>  < Tao Jin; Jinrong Liu; >
# This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
# This is free software, and you are welcome to redistribute it
# under certain conditions; type `show c' for details.
import os
import re as r
import sys


def getFunc(Data):
    '''
    将alf文件中的Func逐个取出
    :param Data: alf文件
    :return: 若干个func的集合
    '''

    func_list = []
    # 建立空列表
    num = 1;  # num为括号个数
    func_flag = 'func'  # 被匹配的字符串
    start_place = Data.find(func_flag)  # start_place为需要截取的第一个func的起始位置
    while Data[start_place + 4] != ' ':
        start_place = Data.find(func_flag, start_place + 4)
    while start_place != -1:  # 如果起始位置不为-1，则字符串内还有func
        i = start_place
        for i in range(start_place, len(Data) + 1):  # 从本func的起始位置开始匹配“{}”个数
            if num != 0:  # 如果num不为0，则一直往后匹配括号
                if Data[i] == '{':
                    num += 1
                elif Data[i] == '}':
                    num -= 1  # 对于num，有“{”加1，有“}”减1
            else:  # 此时num为0，代表func内的全部内容到此为止
                num = 1;  # num归为1，供下次使用
                break  # 跳出for循环

        end_place = i - 1  # end_place为本func包含内容的最后一位的位置
        list_items = '{ ' + Data[start_place:end_place] + '}'  # 将本次匹配的func提取为list_items
        func_list.append(list_items)  # 列表添加元素
        start_place = Data.find(func_flag, end_place)  # start_place重新定位到下一个func的起始位置
        while start_place != -1 and Data[start_place + 4] != ' ':
            start_place = Data.find(func_flag, start_place + 4)
    return func_list


