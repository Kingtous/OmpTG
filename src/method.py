# <OmpTG>  Copyright (C) <2021>  < Tao Jin; Jinrong Liu; >
# This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
# This is free software, and you are welcome to redistribute it
# under certain conditions; type `show c' for details.
import os
import re as r  # 正则表达式库
import sys, getopt
from help import ShowOptions
from readalf import readALF
from getInit import getInitialHeader
from getFunc import getFunc
from Delete_Note import deleteNote
from Function_declaration import getFunctionDeclaration
from replace_call import replaceCall
from getBasicBlockSlice import getBasicBlockSlice
from Create_every_bb import createEveryBasicBlock
from Create_every_bb import createEveryTask
from WCET_Generator import WCET_Output


def Generate_evealf(input_filename, output_filename):  # 'w':'Generate WCET for the file imported.'
    '''
    以basicblock为单位生成每个节点的WECT
    :param input_filename: 输入文件名
    :param output_filename: 输出文件名
    :return:
    '''
    try:

        Enter_File_Name = input_filename

    except:
        print('Please Input ALF file u\'d like to analyze.\nAborted.')
        sys.exit(0)

    WCET_list = {}
    call_result = {}
    if os.path.isfile(Enter_File_Name):
        # hashtag_rule = r.compile(u'(\/\*(\s|.)*?\*\/)|(\/\/.*)')
        file = open(Enter_File_Name, 'r')
        content = file.readlines()
        # Total_Function_Declarations：alf代码总的函数声明
        Total_Function_Declarations = getInitialHeader(content)
        file.close()
        # ALF_data：将代码保存为一个字符串
        ALF_data = readALF(Enter_File_Name)
        # 将DATA里的每一个func提取出来组合为一个列表（含注释）
        func_body_list = getFunc(ALF_data)
        # 将list_func的注释清除
        deleteNote(func_body_list)
        # every_func_mid_declaration: 每个Func前的函数申明
        every_func_mid_declaration = getFunctionDeclaration(func_body_list)
        func_name_sum = []
        for i in range(0, len(func_body_list)):
            func_name_sum.append(findLabel(func_body_list[i]))
        filesname = []
        for i in range(0, len(func_body_list)):
            temp = []
            temp.append(func_body_list[i])

            basicblock_set = getBasicBlockSlice(temp, 'w')

            replaceCall(basicblock_set, func_name_sum, call_result, 'w')

            createEveryBasicBlock(basicblock_set, every_func_mid_declaration, Total_Function_Declarations, WCET_list,
                                  filesname, output_filename)
        WCET_Output(WCET_list, os.path.splitext(Enter_File_Name)[0])
        print('Create ALF file Success!')

    else:
        print('It\'s not a file')


def Generate_taskalf(input_filename, output_filename):  # 'b':'Generate ALF for every OpenMP task.',
    '''
    针对每个TaskFunc生成alf文件
    :param input_filename: 输入文件名
    :param output_filename: 输出文件名
    :return:
    '''
    try:

        Enter_File_Name = input_filename

    except:
        print('Please Input ALF file u\'d like to analyze.\nAborted.')
        sys.exit(0)

    WCETList = {}

    if os.path.isfile(Enter_File_Name):
        file = open(Enter_File_Name, 'r')
        content = file.readlines()
        # Total_Function_Declarations：alf代码总的函数声明
        Total_Function_Declarations = getInitialHeader(content)
        file.close()
        # ALF_data：将代码保存为一个字符串
        ALF_data = readALF(Enter_File_Name)
        # 将DATA里的每一个func提取出来组合为一个列表（含注释）
        func_body_list = getFunc(ALF_data)
        # 将list_func的注释清除
        deleteNote(func_body_list)
        every_func_mid_declaration = getFunctionDeclaration(func_body_list)
        func_sum = {}
        callFunc_sum = {}
        for i in range(0, len(func_body_list)):
            func_sum[findLabel(func_body_list[i])] = func_body_list[i]
        filesname = []

        for i in range(0, len(func_body_list)):
            list_func_temp = []
            list_func_temp.append(func_body_list[i])
            funcname_start_place = list_func_temp[0].find('"')
            funcname_end_place = list_func_temp[0].find('"', funcname_start_place + 1)

            if (list_func_temp[0][funcname_start_place:funcname_end_place + 1].find('taskFunc') != -1) or (
                    list_func_temp[0][funcname_start_place:funcname_end_place + 1].find('thrFunc') != -1):
                # callFunc_sum：函数各个节点调用关系字典（key：节点，value：被调用函数）
                callFunc_sum = {}
                basicblock_set = getBasicBlockSlice(list_func_temp, 'b')

                callFunc_names = replaceCall(basicblock_set, func_sum, callFunc_sum, 'b')

                createEveryTask(basicblock_set, every_func_mid_declaration, Total_Function_Declarations, filesname,
                                callFunc_names, func_sum, output_filename)
                funcrelation_end_placee = list_func_temp[0].find(':', funcname_start_place + 1)
                GenerateFileName = output_filename + '/' + list_func_temp[0][
                                                           funcname_start_place + 1:funcrelation_end_placee] + 'relation.txt'

                f = open(GenerateFileName, 'w')
                for i in callFunc_sum.keys():
                    f.write(i + '    ')
                    f.write(callFunc_sum[i] + '\n')

        print('Create ALF file Success!')

    else:
        print('It\'s not a file')


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
