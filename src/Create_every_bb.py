# <OmpTG>  Copyright (C) <2021>  < Tao Jin; Jinrong Liu; >
# This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
# This is free software, and you are welcome to redistribute it
# under certain conditions; type `show c' for details.
# createEveryBasicBlock
import os
import platform
import re as r  # 正则表达式库
import sys
from callFunction import GenerateCallFunction
from callFunction import findPosFromPoint
import shutil


def createEveryBasicBlock(basicblock_sum, declaration_for_func_sum, declaration_total, WCETList, filesname,
                          out_filename):
    '''
    创建每一个basicblock的alf文件

    :param basicblock_sum:
    :param declaration_for_func_sum: 每个Func的申明
    :param declaration_total: 引导区的内容
    :param WCETList:   WECT的列表
    :param filesname:  已经生成的文件名集合（防止大小写不敏感时，两个func文件覆盖）
    :param out_filename: 输出的文件名

    '''

    out_filename = '/tmp/' + out_filename + '/'
    # outname =outname + '/'
    Systemtype = platform.system()  # system
    for basicblock_name in basicblock_sum:
        if len(basicblock_sum) != 1:
            # Not Only have return statement

            if basicblock_name != 'return':  # 这个basicblock不是"return"
                if Systemtype == "Linux" or Systemtype == "Darwin":  # Linux/mac系统
                    basicblock_part = basicblock_sum[basicblock_name]
                    basicblock_label = findLabel(basicblock_part)
                    path = out_filename + basicblock_label
                    folder = os.path.exists(path)
                    if not folder:  # 生成文件夹路径
                        os.makedirs(path)
                    GenerateFileName = out_filename + basicblock_label + '/' + basicblock_name + '.alf'
                    # 'Generate_file/'
                else:  # Windows系统
                    basicblock_part = basicblock_sum[basicblock_name]
                    basicblock_label = findLabel(basicblock_part)
                    for i in range(0, len(filesname)):
                        if filesname[i] == basicblock_label.lower():
                            basicblock_label = basicblock_label + "_other"
                            break
                    path = out_filename + basicblock_label
                    folder = os.path.exists(path)
                    if not folder:  # 生成文件夹路径
                        os.makedirs(path)
                    # f = open('Generate_file/'+'Circle_'+bb+'.txt', 'w')
                    GenerateFileName = out_filename + basicblock_label + '/' + basicblock_name + '.alf'

                f = open(GenerateFileName, 'w')
                for i in range(0, len(declaration_total)):  # 写入引导区内容

                    if type(declaration_total[i]) is str:
                        f.write(declaration_total[i] + '\n')
                        # print(type(list[i]))
                    elif isinstance(declaration_total[i], dict):
                        temp_part = basicblock_sum[basicblock_name]
                        templabel = findLabel(temp_part)
                        temp = " { lref 64 \"" + templabel + "\" }"
                        f.write(temp)
                    else:
                        for j in range(0, len(declaration_total[i])):
                            f.write(declaration_total[i][j] + '\n')
                f.write(declaration_for_func_sum[findLabel(basicblock_part)] + '\n')  # 写入函数申明
                f.write(basicblock_sum[basicblock_name] + '\n')  # 写入该basicblock的主体

                call_part = findCallPart(basicblock_sum[basicblock_name])  # 查找是否调用其他函数
                if (call_part == 0):  # 没有call的Func
                    f.write(basicblock_sum['return'] + '\n')
                    for i in range(0, 5):
                        for j in range(0, 5 - i):
                            f.write(' ')
                        f.write('}\n')
                else:  # 有call的Func
                    f.write(basicblock_sum['return'] + '\n')
                    for i in range(0, 3):
                        for j in range(0, 3 - i):
                            f.write(' ')
                        f.write('}\n')
                    f.write(GenerateCallFunction(call_part))
                    f.write('  }\n')
                    f.write(' }\n')
                f.close()
                WCET_Generator(basicblock_label, basicblock_name, GenerateFileName, WCETList)  # 生成WECT list
                # os.remove(GenerateFileName)
                # os.removedirs(path)
                # shutil.rmtree(path)
            else:  # 这个basicblock是"return"
                if Systemtype == "Linux" or Systemtype == "Darwin":  # Linux/mac系统
                    basicblock_part = basicblock_sum[basicblock_name]
                    basicblock_label = findLabel(basicblock_part)
                    path = out_filename + basicblock_label
                    folder = os.path.exists(path)
                    if not folder:  # 生成文件夹路径
                        os.makedirs(path)
                    GenerateFileName = out_filename + basicblock_label + '/' + basicblock_name + '.alf'
                else:  # Windows系统
                    basicblock_part = basicblock_sum[basicblock_name]
                    basicblock_label = findLabel(basicblock_part)
                    for i in range(0, len(filesname)):
                        if filesname[i] == basicblock_label.lower():
                            basicblock_label = basicblock_label + "_other"
                            break
                    path = out_filename + basicblock_label
                    folder = os.path.exists(path)
                    if not folder:  # 生成文件夹路径
                        os.makedirs(path)
                    # f = open('Generate_file/'+'Circle_'+bb+'.txt', 'w')

                    GenerateFileName = out_filename + basicblock_label + '/' + basicblock_name + '.alf'
                # 因为该basicblock之前的命名为"return"，这里是为了找出return的节点名
                return_nameplace_start = basicblock_part.find('::')
                return_nameplace_end = 0
                for i in range(return_nameplace_start + 1, len(basicblock_part)):
                    if basicblock_part[i] == '"':
                        return_nameplace_end = i
                        break
                return_name = basicblock_part[return_nameplace_start + 2:return_nameplace_end]
                for s in range(0, len(return_name) - 1):  # 将return中的":"变为"_"
                    if return_name[s] == ":":
                        return_name = return_name[:s] + '_' + return_name[s + 2:]

                f = open(GenerateFileName, 'w')
                for i in range(0, len(declaration_total)):  # 写入引导区内容

                    if type(declaration_total[i]) is str:
                        f.write(declaration_total[i] + '\n')

                    elif isinstance(declaration_total[i], dict):
                        temp_part = basicblock_sum[basicblock_name]
                        templabel = findLabel(temp_part)

                        temp = " { lref 64 \"" + templabel + "\" }"

                        f.write(temp)
                    else:
                        for j in range(0, len(declaration_total[i])):
                            f.write(declaration_total[i][j] + '\n')
                f.write(declaration_for_func_sum[findLabel(basicblock_part)] + '\n')  # 写入函数申明
                f.write(basicblock_sum[basicblock_name] + '\n')  # 写入basicblock的主体

                for i in range(0, 5):
                    f.write(' }\n')
                f.close()
                WCET_Generator(basicblock_label, return_name, GenerateFileName, WCETList)
        else:
            # Only have return statement
            if Systemtype == "Linux" or Systemtype == "Darwin":  # Linux/mac系统
                basicblock_part = basicblock_sum[basicblock_name]
                basicblock_label = findLabel(basicblock_part)
                path = out_filename + basicblock_label
                folder = os.path.exists(path)
                if not folder:  # 生成文件夹路径
                    os.makedirs(path)
                GenerateFileName = out_filename + basicblock_label + '/' + basicblock_name + '.alf'
                # 'Generate_file/'
            else:  # Windows系统
                basicblock_part = basicblock_sum[basicblock_name]
                basicblock_label = findLabel(basicblock_part)
                for i in range(0, len(filesname)):
                    if filesname[i] == basicblock_label.lower():
                        basicblock_label = basicblock_label + "_other"
                        break
                path = out_filename + basicblock_label
                folder = os.path.exists(path)
                if not folder:  # 生成文件夹路径
                    os.makedirs(path)
                GenerateFileName = out_filename + basicblock_label + '/' + basicblock_name + '.alf'

            # 因为该basicblock之前的命名为"return"，这里是为了找出return的节点名
            return_nameplace_start = basicblock_part.find('::')
            return_nameplace_end = 0
            for i in range(return_nameplace_start + 1, len(basicblock_part)):
                if basicblock_part[i] == '"':
                    return_nameplace_end = i
                    break
            return_name = basicblock_part[return_nameplace_start + 2:return_nameplace_end]
            f = open(GenerateFileName, 'w')
            for i in range(0, len(declaration_total)):  # 写入引导区内容
                # print(i)
                if type(declaration_total[i]) is str:
                    f.write(declaration_total[i] + '\n')
                    # print(type(list[i]))
                elif isinstance(declaration_total[i], dict):
                    temp_part = basicblock_sum[basicblock_name]
                    templabel = findLabel(temp_part)
                    temp = declaration_total[i][templabel]
                    f.write(temp)
                else:
                    for j in range(0, len(declaration_total[i])):
                        f.write(declaration_total[i][j] + '\n')
            f.write(declaration_for_func_sum[findLabel(basicblock_part)] + '\n')  # 写入函数申明
            f.write(basicblock_sum[basicblock_name] + '\n')  # 写入basicblock的主体
            for i in range(0, 5):
                for j in range(0, 5 - i):
                    f.write(' ')
                f.write('}\n')
            f.close()

            WCET_Generator(basicblock_label, return_name, GenerateFileName, WCETList)
            # os.remove(GenerateFileName)
            # shutil.rmtree(path)
    funcname = findLabel(basicblock_sum['return'])
    filesname.append(funcname.lower())


def createEveryTask(taskfunc_part, declaration_everyfunc, declaration_total, filesname, callfunc_names, func_sum,
                    outname):
    '''
    针对taskfunc部分创建alf文件
    :param taskfunc_part: taskfunc部分的主要代码段
    :param declaration_everyfunc: func的函数申明集合
    :param declaration_total: 引导区
    :param filesname: 已经生成的文件名集合（防止大小写不敏感时，两个func文件覆盖）
    :param callfunc_names: taskfunc中调用的其他函数
    :param func_sum: 所有函数的集合
    :param outname: 输出的文件名
    :return:
    '''

    outname = outname + '/'
    Systemtype = platform.system()  # system
    for task in taskfunc_part:
        func_name = findLabel(task)
        path = outname
        folder = os.path.exists(path)  # 生成路径
        if not folder:
            os.makedirs(path)
        GenerateFileName = outname + func_name + '.alf'
        f = open(GenerateFileName, 'w')
        for i in range(0, len(declaration_total)):

            if type(declaration_total[i]) is str:
                f.write(declaration_total[i] + '\n')

            elif isinstance(declaration_total[i], dict):
                t = taskfunc_part[task]
                templabel = findLabel(t)

                temp = " { lref 64 \"" + templabel + "\" }"

                f.write(temp)
            else:
                for j in range(0, len(declaration_total[i])):
                    f.write(declaration_total[i][j] + '\n')
        f.write(declaration_everyfunc[func_name] + '\n')
        f.write(taskfunc_part[task] + '\n')
        calledfunc_list = []  # 被调用过的函数集合
        for i in callfunc_names.keys():
            calledfunc_list.append(callfunc_names[i])
        for i in range(0, len(calledfunc_list)):  # 再次写入
            if calledfunc_list[i] != func_name:
                f.write(declaration_everyfunc[calledfunc_list[i]] + '\n')
                f.write(func_sum[calledfunc_list[i]] + '\n')
        f.write('  }\n')
        f.write(' }\n')


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


def findCallPart(string):
    string = string.strip()
    start_call_place = string.find("call")
    while (start_call_place != -1):
        if string[start_call_place - 1] == '_':
            start_call_place = string.find("call", start_call_place + 4)
        else:
            call_body = string[len(findPosFromPoint(string, 0)):].strip()
            return call_body
    return 0


def WCET_Generator(FuncName, BasicBlock, ALFile, WCETList):
    # call SWEET
    import subprocess
    std_hll = os.path.dirname(os.path.abspath(__file__)) + '/Support/std_hll.alf'
    clt = os.path.dirname(os.path.abspath(__file__)) + '/Support/CostTimeTable.clt'
    # ALF File=ALFile
    try:
        output = subprocess.Popen('sweet -i=' + ALFile + ',' + std_hll + \
                                  ' -c extref=off -ae pu aac=' + clt + ' tc=st,op merge=all' \
                                  , stdout=subprocess.PIPE, shell=True).communicate()
        WCET_Time = int(str(output[0]).split('table:')[-1].strip('\\n\"\ '))
        WCETList[FuncName + ' ' + BasicBlock] = WCET_Time
        print('WCET for ' + FuncName + '' + BasicBlock + '------' + str(WCET_Time))
    except:
        WCETList[FuncName + ' ' + BasicBlock] = 'ERROR'
        print('\n---' + FuncName + ' ' + BasicBlock + '---Output ERROR---\n')
