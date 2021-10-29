# <OmpTG>  Copyright (C) <2021>  < Tao Jin; Jinrong Liu; >
# This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
# This is free software, and you are welcome to redistribute it
# under certain conditions; type `show c' for details.
class infoModel:

    def __init__(self, name, pre, succ, isStart, isExit):
        self.name = name
        self.pre = pre
        self.succ = succ
        self.isStart = isStart
        self.isExit = isExit
        self.sign = set()
        self.type = None

    def insertSign(self, sign):
        self.sign.add(sign)


class startPointModel:

    def __init__(self, graph, start, end, type):
        self.v = set()
        self.type = type
        self.includes = set()
        self.start = start
        self.end = end
        self.startValue = None
        self.endValue = None
        self.getFunctionNameAndValue()
        self.findV(graph)
        self.parent = False
        self.CondBranch = None

    def getFunctionNameAndValue(self):
        if self.start != None:
            self.function = getFunctionName(self.start)
            self.startValue = getValue(self.start)
        if self.end != None:
            self.endValue = getValue(self.end)

    def findV(self, graph):
        for node in graph:
            if getFunctionName(node) != self.function:
                continue
            value = getValue(node)
            if value >= float(self.startValue) and value < self.endValue:
                self.v.add(node)

    def hasParent(self):
        return self.parent

    def isInclude(self, model):
        if self.v.issuperset(model.v):
            return True
        return False

    def include(self, totalModel, oriModel, model):
        if oriModel.v.isdisjoint(model.v):
            # 那就在其中的include列表中
            for ori in oriModel.includes:
                oriModel.include(totalModel, totalModel[ori], model)
        else:
            oriModel.v = oriModel.v - model.v
        # 考虑结束结点相同的情况
        oriModel.includes.add(model.start)
        oriModel.v.add(oriModel.start)
        # 不放end结点，结束结点不属于当前block
        # oriModel.v.add(oriModel.end)
        # 添加parent
        model.parent = oriModel.start


def getBB(nodeName):
    import re as r
    if nodeName != None:
        if nodeName.endswith('_entry'):
            return None
        if nodeName.endswith('_exit'):
            return None
        result = r.split('__bb', nodeName)

        if len(result) == 2:
            if result[1].startswith('__') or result[1] == '':
                return 0
            else:
                return result[1].split('__')[0]


def getValue(nodeName):
    import re as r
    if nodeName != None:
        if nodeName.endswith('_entry'):
            return -1
        if nodeName.endswith('_exit'):
            return 9999
        result = r.split('__bb', nodeName)

        if len(result) == 2:
            if result[1].startswith('__'):
                # __bb__1___3
                result2 = r.split('[_]+', result[1][2:])
                if len(result2) == 1:
                    return float('0.' + result2[0].zfill(4))
                elif len(result2) == 2:
                    return float('0.' + result2[0].zfill(4) + result2[1].zfill(4))
            elif result[1] == '':
                return 0
            else:
                result2 = r.split('[_]+', result[1])
                if len(result2) == 1:
                    return float(result2[0])
                elif len(result2) == 2:
                    return float(result2[0] + '.' + result2[1].zfill(4))
                elif len(result2) == 3:
                    return float(result2[0] + '.' + result2[1].zfill(4) + result2[2].zfill(4))


def getFunctionName(name):
    if name.endswith('_entry'):
        return name.replace('_entry', '')

    if name.endswith('_exit'):
        return name.replace('_exit', '')

    import re as r
    result = r.split('__bb', name)
    return result[0]
