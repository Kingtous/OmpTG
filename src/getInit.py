# <OmpTG>  Copyright (C) <2021>  < Tao Jin; Jinrong Liu; >
# This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
# This is free software, and you are welcome to redistribute it
# under certain conditions; type `show c' for details.
import re as r


def getInitialHeader(string):
    '''
    获取引导区的内容
    :param string: alf文件
    :return: 返回一个list，每一行（除下lrefs那行）都是一个list中的元素，lrefs那行切成一个一个小的元素(按lref切，方便后序重组)
    '''

    temp = []  # 暂存列表列表
    result = []  # 存储最终结果的列表
    d = {}  # 暂存有关lref元素的字典
    sub_str1 = "funcs"  # 被匹配字符串
    # 找出引导区末尾终结符
    for index, value in enumerate(string):  # 读取列表中元素的值对应的索引
        if sub_str1 in value:
            last = index + 1
            break
    # 将引导区内容暂存在temp列表里
    temp = string[: last]

    # 在temp里找出中间lrefs那一行，并分割为列表
    sub_str2 = "lrefs"  # 被匹配字符串
    for index, value in enumerate(temp):
        if sub_str2 in value:
            middle = index
            break
    temp[middle] = temp[middle].replace("lrefs ", "lrefs \n ")  # 以\n作为分割来转换列表
    temp[middle] = temp[middle].replace("} ", "}\n ")
    # 将temp列表转换为字符串，并去除回车空格括号等字符
    str_temp = ''.join(temp)
    list_str = str_temp.split("\n")  # 若以列表返回，则将之前的字符串转换为列表
    # print(list_str)
    # print("-----")

    # 以列表为元素的构建部分
    sub_str3 = 'lrefs'  # 将lrefs之前的元素转换为列表，并以该列表为元素存进列表中
    for index, value in enumerate(list_str):
        if sub_str3 in value:
            front = index + 1
            break
    f = list_str[: front]  # 将前半部分以列表的形式存进列表
    result.append(f)

    # 以字典为元素的构建部分
    sub_str4 = 'lref 64 '  # 匹配temp中有关lref的元素
    for value in list_str:
        if sub_str4 in value:  # 转换temp中的一些有关lref的元素为字典
            p = value.split('"')[1]  # 提取双引号内容作为字典的键值
            # print(p)
            d[p] = value
    result.append(d)  # 将中间转换为字典的元素以字典形式存进列表

    sub_str5 = 'imports'  # 匹配最后部分的元素，找出这些元素存进列表，这些元素是以字符串形式存进列表的
    for index, value in enumerate(list_str):
        if sub_str5 in value:
            tail = index - 2  # 减2为了将imports前的两个'}'包含进列表
            break;
    result = result + list_str[tail:]
    # print(result)
    return result

