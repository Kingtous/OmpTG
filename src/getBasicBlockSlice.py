# <OmpTG>  Copyright (C) <2021>  < Tao Jin; Jinrong Liu; >
# This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
# This is free software, and you are welcome to redistribute it
# under certain conditions; type `show c' for details.
# getBasicBlockSlice
import os
import re as r  # 正则表达式库
import sys


def getBasicBlockSlice(basicblock_sum_list, type):
    '''
    将一个Func分为若干个basicblock
    :param basicblock_sum_list:一个Func（包含若干个Basicblock）
    :param type: 两种模式：w/b
    :return: 该Func里所有Basicblock的字典集合
    '''
    if type == 'w':

        for basicblock in basicblock_sum_list:
            basicblock_dictionary = {}  # 创建字典
            start_flag = 'return'  # 先查找"return"节点
            return_start_place = basicblock.find(start_flag)
            partial_code_beforreturn = basicblock[:return_start_place - 1]
            reverse_partial_code_beforreturn = partial_code_beforreturn[::-1]  # 字符串反转找到最前的"label"
            reverse_label_start_place = reverse_partial_code_beforreturn.find('lebal')
            for j in range(reverse_label_start_place, len(reverse_partial_code_beforreturn)):
                if reverse_partial_code_beforreturn[j] == '{':
                    reverse_label_start_place = j
                    break
            return_start_place = len(partial_code_beforreturn) - len(
                reverse_partial_code_beforreturn[:reverse_label_start_place]) - 1

            temp_end_place = basicblock.find('return', return_start_place)
            bracket_num = 1
            for i in range(temp_end_place + 5, len(basicblock)):
                if basicblock[i] == '{':
                    bracket_num += 1
                elif basicblock[i] == '}':
                    bracket_num -= 1
                    if bracket_num == -1:
                        return_end_place = i
                        break

            # return语句结束部分 将return语句写入字典
            basicblock_dictionary['return'] = basicblock[return_start_place:return_end_place]
            # 将return节点去除
            basicblock_main_part = basicblock[:return_start_place]
            basicblock_start_place = 0
            basicblock_end_place = 0
            basicblocklabel_start_place = basicblock_main_part.find("label")
            while basicblocklabel_start_place != -1:  # 每有一个"label"就含有一个basiblock
                basicblock_temp = ''
                basicblock_temp = findPosFromPoint(basicblock_main_part, basicblock_start_place)
                basicblock_start_place = basicblock_main_part.find(basicblock_temp, basicblock_start_place)
                basicblock_end_place = basicblock_main_part.find(basicblock_temp, basicblock_start_place) + len(
                    basicblock_temp)
                basicblock_temp = findPosFromPoint(basicblock_main_part, basicblock_end_place)
                basicblock_end_place = basicblock_main_part.find(basicblock_temp, basicblock_end_place) + len(
                    basicblock_temp)
                basicblock_temp = basicblock_main_part[basicblock_start_place:basicblock_end_place + 1]
                basicblock_start_place = basicblock_end_place
                basicblock_name = (r.search('bb\d*', basicblock_temp)).group()
                name_start_place = basicblock_temp.find(basicblock_name)
                name_end_place = basicblock_temp.find('"', name_start_place)
                basicblock_name_part = basicblock_temp[name_start_place:name_end_place]
                basicblock_realname = ''
                basicblock_number = 0  # 查找basicblock序号
                while basicblock_name_part.find(":", basicblock_number) != -1:
                    for i in range(basicblock_name_part.find(":", basicblock_number), len(basicblock_name_part)):
                        if basicblock_name_part[i] != ":":
                            basicblock_realname = basicblock_realname + basicblock_name_part[
                                                                        basicblock_number:basicblock_name_part.find(":",
                                                                                                                    basicblock_number)] + '_'
                            basicblock_number = i
                            break
                basicblock_realname = basicblock_realname + basicblock_name_part[basicblock_number:]
                basicblock_dictionary[basicblock_realname] = basicblock_temp
                basicblocklabel_start_place = basicblock_main_part.find("label", basicblock_start_place)
                # dict[(r.search('bb\d*', temp)).group()] = temp
        return basicblock_dictionary
    elif type == 'b':
        for basicblock in basicblock_sum_list:
            basicblock_dictionary = {}
            basicblock_main_part = basicblock
            task_start_place = basicblock_main_part.find('"')
            task_end_place = basicblock_main_part.find('"', task_start_place + 1)
            basicblock_dictionary[basicblock_main_part[task_start_place:task_end_place + 1]] = basicblock_main_part
        return basicblock_dictionary


def findPosFromPoint(string, startPoint):
    '''
    按照括号匹配的原则对代码切割
    :param string: 代码
    :param startPoint: 起始点
    :return: 切割出的文本
    '''
    result_text = ''
    point = startPoint
    cnt = 0
    flag = False  # 找到了
    while True:
        if (point >= len(string)):
            break
        if (flag == True):
            if (string[point] == '{'):
                cnt = cnt + 1
            elif (string[point] == '}'):
                cnt = cnt - 1
            result_text = result_text + string[point]
            # print(string[point])
            if (cnt == 0):
                break
        else:
            # 还没找到
            if (string[point] == '{'):
                flag = True
                cnt = cnt + 1
                result_text = result_text + string[point]
        point = point + 1
    return result_text
