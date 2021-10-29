# <OmpTG>  Copyright (C) <2021>  < Tao Jin; Jinrong Liu; >
# This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
# This is free software, and you are welcome to redistribute it
# under certain conditions; type `show c' for details.
import os
import re as r  # 正则表达式库
import sys
from readalf import readALF
from getHeader1 import getHeader
from getFunc import getFunc
from Delete_Note import deleteNote
from Function_declaration import getFunctionDeclaration
from replace_call import replaceCall
from getBasicBlockSlice import getBasicBlockSlice
from Create_every_bb import createEveryBasicBlock

Enter_File_Name = input("Input file name:")
hashtag_rule = r.compile(u'(\/\*(\s|.)*?\*\/)|(\/\/.*)')
file = open(Enter_File_Name, 'r')
content = file.readlines()
head = getHeader(content)  # head：alf代码总的函数声明
file.close()
# print(head)
DATA = readALF(Enter_File_Name)  # DATA：将代码保存为一个字符串放白奴和
# print(head)
# print(DATA)
list_func = getFunc(DATA)  # 将DATA里的每一个func提取出来组合为一个列表（含注释）
# for i in range(0,len(list_func)):
# print(list_func[i])
# print(list_func)
deleteNote(list_func)  # 将list_func的注释清除
# print(list_func)
Every_func_mid_declaration = getFunctionDeclaration(list_func)
# print(Every_func_mid_declaration)
for i in range(0, len(list_func)):
    list_func_temp = []
    list_func_temp.append(list_func[i])
    dict_temp = getBasicBlockSlice(list_func_temp)
    # print(dict_temp)
    replaceCall(dict_temp)
    # print(dict_temp)
    createEveryBasicBlock(dict_temp, Every_func_mid_declaration, head)

print('Create "alf"file Success!')
# print(Every_func_mid_declaration)
# print(list_func)
