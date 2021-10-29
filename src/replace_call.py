# <OmpTG>  Copyright (C) <2021>  < Tao Jin; Jinrong Liu; >
# This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
# This is free software, and you are welcome to redistribute it
# under certain conditions; type `show c' for details.
import os
import re as r  # 正则表达式库
import sys
import operator


def replaceCall(basicblock_sum, funcs_sum, callfunc_sum, type):
    '''

    w：替换被call的部分
    b：记录task中call的函数名
    :param basicblock_sum: basicblock集合
    :param funcs_sum: 全部func
    :param callfunc_sum: 被调用的func集合
    :param type: w/b
    :return:
    '''

    if type == 'w':
        # 对每个basicblock中的调用的函数部分进行替换
        replace_part = ''
        for basicblock_name in basicblock_sum.keys():

            if basicblock_name != 'return':
                flag = 'label'  # 被匹配的字符串
                replace_begin_place = 0
                replace_end_place = 0
                basicblock_part = basicblock_sum[basicblock_name]
                call_label_palce = 0
                return_start_place = basicblock_part.find(flag)
                called_start_place = basicblock_part.find(flag, return_start_place + 5)  # 找到被call的部分"label"开始的位置
                prestart_place = 0
                while called_start_place != -1:  # 存在第二个label就是存在调用其他代码的部分
                    brackets_num = 2  # num为起始括号数量，进行括号匹配
                    for I in range(0, called_start_place):

                        if basicblock_part[called_start_place - I] == "{":
                            brackets_num -= 1
                            if brackets_num == 0:
                                prestart_place = called_start_place - I
                                break

                    if (basicblock_part[prestart_place:called_start_place].find("call") == -1):  # 寻找"call"

                        brackets_num = 1
                        basicblock_part = basicblock_sum[basicblock_name]
                        for j in range(0, called_start_place):

                            if basicblock_part[called_start_place - j] == '{':
                                replace_begin_place = called_start_place - j
                                break
                        for i in range(called_start_place, len(basicblock_part)):
                            if basicblock_part[i] == '{':
                                brackets_num += 1
                            elif basicblock_part[i] == '}':
                                brackets_num -= 1
                                if brackets_num == 0:
                                    replace_end_place = i
                                    brackets_num = 1
                                    break
                        # try:
                        basicblock_sum[basicblock_name] = basicblock_sum[basicblock_name][
                                                          :replace_begin_place] + replace_part + basicblock_sum[
                                                                                                     basicblock_name][
                                                                                                 replace_end_place:]
                        called_start_place = basicblock_sum[basicblock_name].find(flag, replace_end_place)
                        # except:
                        #     print("changejump"+basicblock_sum[bb]
                    else:
                        # 其他情况
                        basicblock_part = basicblock_sum[basicblock_name]
                        brackets_num = 1
                        for i in range(0, called_start_place):
                            if basicblock_part[called_start_place - i] == '{':
                                replace_begin_place = called_start_place - i
                                break
                        for i in range(called_start_place, len(basicblock_part)):
                            if basicblock_part[i] == '{':
                                brackets_num += 1
                            elif basicblock_part[i] == '}':
                                brackets_num -= 1
                                if brackets_num == 0:
                                    replace_end_place = i
                                    brackets_num = 1
                                    break
                        replace_string = basicblock_part[replace_begin_place:replace_end_place]
                        call_start_palce = replace_string.find('"')
                        call_end_palce = replace_string.find('"', call_start_palce + 1)
                        replace_string = replace_string[:call_start_palce + 1] + "callfunction" + replace_string[
                                                                                                  call_end_palce:]
                        basicblock_sum[basicblock_name] = basicblock_sum[basicblock_name][
                                                          :replace_begin_place] + replace_string + basicblock_sum[
                                                                                                       basicblock_name][
                                                                                                   replace_end_place:]
                        called_start_place = basicblock_sum[basicblock_name].find(flag, replace_end_place)



            else:

                # 将return的部分代码替换被call的部分
                brackets_num = 0
                return_start_place = 0
                return_end_place = 0
                basicblock_part = basicblock_sum[basicblock_name]
                for i in range(0, len(basicblock_part)):
                    if basicblock_part[i] == '{':
                        return_start_place = i
                        break

                for i in range(0, len(basicblock_part)):
                    if basicblock_part[i] == '{':
                        brackets_num += 1
                    elif basicblock_part[i] == '}':
                        brackets_num -= 1
                        if brackets_num == 0:
                            return_end_place = i
                            break
                replace_part = basicblock_sum['return'][return_start_place:return_end_place]
    elif type == 'b':
        # 记录task中call的函数名
        for basicblock_name in basicblock_sum.keys():
            call_func_temp = []
            call_func_temp_Reference = []
            called_func = {}  # 返回的函数名列表
            func_part = basicblock_sum[basicblock_name]  # 这个taskfunc的主体
            findCallName(func_part, called_func, call_func_temp_Reference, funcs_sum, callfunc_sum)
            for i in called_func.keys():
                call_func_temp.append(called_func[i])
            # 新旧两个被调用的函数集合进行对比
            while operator.eq(call_func_temp, call_func_temp_Reference) == False:  # 当不再有新的函数被被调用，说明遍历完成
                call_func_temp_Reference = call_func_temp
                for i in call_func_temp:
                    findCallName(funcs_sum[i], called_func, call_func_temp_Reference, funcs_sum, callfunc_sum)
                call_func_temp = []
                for i in called_func.keys():
                    call_func_temp.append(called_func[i])

        return called_func


def findCallName(func_part, called_func, reference, funcs_sum, callfunc_sum):
    '''
    寻找被调用的函数
    :param func_part: taskfunc的代码主体
    :param called_func: 返回的函数名列表（变化）
    :param reference: 函数名列表对照
    :param funcs_sum: 所有func的集合
    :param callfunc_sum: 被调用的全部func
    :return:
    '''
    callfunc_name_startplace = func_part.find('call')
    temp_Reference = []
    temp_Reference = temp_Reference + reference
    while callfunc_name_startplace != -1:
        if (func_part[callfunc_name_startplace - 1] == ' ' or func_part[callfunc_name_startplace - 1] == '{') and (
                func_part[callfunc_name_startplace + 4] == ' ' or func_part[callfunc_name_startplace + 4] == '{'):
            callfunc_name_startplace = func_part.find('"', callfunc_name_startplace)
            callfunc_name_endplace = func_part.find('"', callfunc_name_startplace + 1)
            for i in range(0, callfunc_name_startplace):
                if func_part[callfunc_name_startplace - 1 - i] == '"':
                    flag_startplace = callfunc_name_startplace - 1 - i
                    break
            for i in range(0, flag_startplace):
                if func_part[flag_startplace - 1 - i] == '"':
                    flag_endplace = flag_startplace - 1 - i
                    break
            callfunc_name = func_part[flag_endplace + 1:flag_startplace]
            callfunc_sum[callfunc_name] = func_part[callfunc_name_startplace + 1:callfunc_name_endplace]
            if (func_part[callfunc_name_startplace + 1:callfunc_name_endplace] not in temp_Reference) and (
                    func_part[callfunc_name_startplace + 1:callfunc_name_endplace] in funcs_sum.keys()):
                called_func[callfunc_name] = func_part[callfunc_name_startplace + 1:callfunc_name_endplace]
                temp_Reference.append(func_part[callfunc_name_startplace + 1:callfunc_name_endplace])
            callfunc_name_startplace = func_part.find('call', callfunc_name_endplace)


def findLabel(string):
    '''
    寻找该段代码对应的函数名（""内的为函数名）
    :param string: 代码
    :return: 函数名
    '''
    flag_1 = '"'
    flag_2 = ':'

    start_place = string.find(flag_1)
    end_place = string.find(flag_2, start_place + 1)
    result = string[start_place + 1:end_place]

    return result
