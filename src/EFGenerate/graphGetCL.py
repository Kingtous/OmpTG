import networkx as nx
from PreprocessDot import *
from FunctionModel import *
from infoModel import *
import copy
import re
import os
import queue

'''
Author: Kingtous
Date: 2019-05-02
'''

# =========================
from PreprocessDot import preprocess

# =========================

# 设置工作目录
root = '/Users/kingtous/test/sort/PCFG/'
# =======DOT存放位置===============
dotPath = root + 'sort_sweet.dot'
# =======relation.txt存放位置======
relationPath = root + 'relation.txt'
# =======需要处理的函数入口======
parseFunction = '_thrFunc0_'
# =======WCET目录====================
wctPath = root + 'sort.wct'
EFGDir = root + 'EFG/'
dotOutput = root + 'sort_pro2.dot'

# ========Bound文件==================
boundPath = root + 'bound.txt'
# ===========cluster_定义==========
Definition = ''
# ========输出================================
# =======特征输出==========
Edges = 0
Nodes = 0
Call_TaskFunc = 0
ConditionVertex = 0
AverageConditionBranch = 0
AverageWCET = 0
WCET_Varience = 0
Wait_Vertex = 0
# ===========限制条件
pathLimited = 50
graphLimited = 100
maxLimited = 70  # 默认值
bound = 2
# ========辅助计算数据
# <OmpTG>  Copyright (C) <2021>  < Tao Jin; Jinrong Liu; >
# This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
# This is free software, and you are welcome to redistribute it
# under certain conditions; type `show c' for details.
TotalConditionBranch = 0
DEBUG = False
WCET_Varience_Data = []
# ===========WCET Config=========
Program_RUN = 33
WCET_Total = 0
WCET_Table = {}
# ===============================
# ========end 结点
endNodesSet = set()

function_set = set()

# ========== else出点
'''
格式：{结点起点：结点终点}
'''
startPoint = []
start_point_model = {}
pointInfo = {}


# ===========


def NodeWait(graph):
    # graph.add_edge('_taskFunc0__exit', '_thrFunc0___bb86', color='green')

    graph.add_edge('_taskFunc1__exit', 'sparselu__bb7__2', color='green')
    graph.add_edge('_taskFunc0__exit', 'sparselu__bb7__2', color='green')


def parseRelation(Path):
    '''
    :param Path: path to relation file
    :return: Dict [key:basic block] [value: Function to be called]
    '''
    relationDict = {}
    file = open(Path, 'r')
    while True:
        line = file.readline().strip()
        if line == '':
            break
        else:
            KeyValue = re.split('\s+', line.replace(':', '_'))
            relationDict[KeyValue[0]] = KeyValue[1]
    return relationDict


def changeShapeOfCondition(graph):
    '''
    :param graph: CFG 图
    :return: None （处理后的带有判断的CFG图）
    '''
    for node in nx.nodes(graph):
        try:
            # TODO 1 在pointInfo里加上node信息
            pre = []
            succ = []
            for key in graph.predecessors(node):
                pre.append(key)
            for key in graph.predecessors(node):
                succ.append(key)
            model = infoModel(node, pre, succ, False, None)
            pointInfo[node] = model
            #
            if 'CREATE' in graph.node[node]['label']:
                # 顺带计算 Task Creation (Call_TaskFunc)
                global Call_TaskFunc
                Call_TaskFunc = Call_TaskFunc + 1
                continue
            elif 'taskwait' in graph.node[node]['label']:
                global Wait_Vertex
                Wait_Vertex = Wait_Vertex + 1
                continue
            elif node.endswith('_exit') or node.endswith('_entry'):
                continue
            count = 0
            # 结点连接的结点
            neighbour = nx.neighbors(graph, node)
            for n in neighbour:
                # 判断是否是task创建
                count = count + 1
            if count > 1:
                graph.node[node]['shape'] = 'diamond'
                # TODO 2 给exit_point字典中的node加上isStart标记
                pointInfo[node].isStart = True
                startPoint.append(node)
                global ConditionVertex
                ConditionVertex = ConditionVertex + 1
        except:
            print('Warning: ' + node + ' ERROR in Function:' + 'changeShapeOfCondition')
            continue


def deleteTaskReturnNode(graph):
    '''
    :param graph: CFG图
    :return: None （处理后的，删去taskFunc return结点的图）
    '''
    NodeNeedTobeDelete = []
    for node in nx.nodes(graph):
        if node.endswith('exit'):
            if (node.startswith('_taskFunc') or node.startswith('_thrFunc')):
                # return 结点
                allNB = nx.all_neighbors(graph, node)
                for returnNode in allNB:
                    # returnNode
                    nebrs = nx.all_neighbors(graph, returnNode)
                    for n in nebrs:
                        # 判断是否是_exit，不是的话加一条边
                        if n != node:
                            graph.add_edge(n, node)
                    NodeNeedTobeDelete.append(returnNode)
                    break
            else:
                # 加 return 标识
                allNB = nx.all_neighbors(graph, node)
                for returnNode in allNB:
                    if graph.has_edge(returnNode, node):
                        graph.node[returnNode]['label'] = \
                            graph.node[returnNode]['label'] + '\nRETURN'

    # 删除returnNode
    for node in NodeNeedTobeDelete:
        graph.remove_node(node)

        global Definition
        Definition = Definition.replace('"' + node + '"', '')


def genWCETValue(graph):
    global WCET_Table
    global WCET_Varience_Data
    global wctPath
    text = ''
    file = open(wctPath, 'r')
    try:
        text = file.readlines()
        # Add Label
        for line in text:
            line = line.strip()
            if line != '':
                line = line.split(' ')

                statement = re.split(r'_+', line[1])
                if len(statement) == 3:
                    statement = statement[0] + '__' + statement[1] + '___' + statement[2]
                elif len(statement) == 2:
                    statement = statement[0] + '__' + statement[1]
                else:
                    statement = statement[0]
                name = line[0] + '__' + statement
                try:
                    value = line[2]
                    try:
                        wctLine = str(int(value) - Program_RUN)
                    except:
                        wctLine = 'ERROR'

                    if graph.node[name] != None:
                        # 加Nodes
                        global Nodes, WCET_Total

                        Nodes = Nodes + 1
                        if wctLine != 'ERROR':
                            WCET_Total = WCET_Total + int(wctLine)
                            WCET_Varience_Data.append(int(wctLine))
                            # graph.node[name]['label'] = \
                            #     graph.node[name]['label'] + '\n' + \
                            #     'WCET=' + wctLine
                            WCET_Table[name] = int(wctLine)

                except:
                    continue

    except:
        print('WCET FILE ERROR')
    finally:
        file.close()


def parrallel(graph):
    '''
    :param graph: CFG图
    :return: None （处理后的，具有并行意义的图）
    '''
    # 改并行
    for node in nx.nodes(graph):
        try:
            name = graph.node[node]['label']
            if 'CREATE' in name:
                for ne in nx.all_neighbors(graph, node):
                    if ne.endswith('exit'):
                        # task 并行
                        # node(entry) -> ne(起点)
                        # tmp = taskFuncXX_exit
                        tmp = ne
                        nameToBeFind = 'CREATE ' + ne.replace('_exit', '')
                        for nodeName in nx.nodes(graph):
                            if (graph.node[nodeName]['label'].split('\n')[-1] == nameToBeFind):
                                ne = nodeName
                                break
                        taiList = []

                        for mother in nx.neighbors(graph, ne):
                            taiList.append(mother)

                        edgeToBeAdd = []
                        edgeToBeDelete = []

                        for mother in nx.all_neighbors(graph, ne):
                            if mother not in taiList:
                                # graph.add_edge(mother,node)
                                edgeToBeAdd.append(mother)
                                # graph.remove_edge(tmp,node)
                                edgeToBeDelete.append(node)

                        for edge in edgeToBeAdd:
                            graph.add_edge(edge, node)
                        for edge in edgeToBeDelete:
                            graph.remove_edge(tmp, edge)
        except:
            print('Warning: ' + node + ' ERROR in Function:' + 'parrallel')
            continue


def deleteUndependNode(graph):
    NodetoBeDelete = []
    nodeIter = nx.nodes(graph)
    for node in nodeIter:
        count = 0
        iter = nx.all_neighbors(graph, node)
        for elem in iter:
            count = count + 1
        if count == 0:
            NodetoBeDelete.append(node)
    # 删除结点
    for node in NodetoBeDelete:
        graph.remove_node(node)
        global Definition
        Definition = Definition.replace('"' + node + '"', '')


def parse(parseFunction, graph, relationDict):
    '''
    :param parseFunction: 要处理的函数
    :param graph: networkx处理生成的图数据
    :param relationDict: 关系字典，basicblock:callFunction
    :return: graph 拼接的图文件
    '''
    # 在set中添加初始结点，以便抽取EFG
    function_set.add(parseFunction)
    # 获取图中所有节点
    for callBlock in relationDict.keys():
        # 查找图中的callBlock,连接callBlock以及函数entry,exit连接callBlock的下一条边
        if relationDict[callBlock].startswith('ort_'):
            # taskwait judgement
            if relationDict[callBlock] == 'ort_taskwait':
                graph.node[callBlock]['style'] = 'filled'
                graph.node[callBlock]['color'] = 'green'
            graph.node[callBlock]['label'] = callBlock + '\n(' + callBlock.split('__bb')[0] + ')' + relationDict[
                                                                                                        callBlock][4:]
            continue
            # callBlockNode = nx.get_node_attributes(graph, callBlock)
        elif relationDict[callBlock].startswith('_taskFunc'):
            # task creation
            graph.node[callBlock]['label'] = callBlock + '\n' + 'CREATE ' + relationDict[callBlock]
            graph.node[callBlock]['style'] = 'filled'
            graph.node[callBlock]['color'] = 'aquamarine'
            function_set.add(relationDict[callBlock])
        else:
            graph.node[callBlock]['label'] = callBlock + '\n' + 'CALL ' + relationDict[callBlock]
            function_set.add(relationDict[callBlock])

    # 处理 CFG
    deleteTaskReturnNode(graph)
    changeShapeOfCondition(graph)
    parrallel(graph)
    deleteUndependNode(graph)
    calcTotalBranch(graph)

    # 输出
    # printFeatureOfGraph(graph)


def printFeatureOfGraph(graph):
    # 计算处理完后的结点,Nodes在生成WCET时数
    Edges = nx.number_of_edges(graph)
    # 输出--Terminal
    if DEBUG:
        print('========Debug Message Start=========')
        print('Vertex(|V|): ' + str(Nodes))
        print('Edges(|E|): ' + str(Edges))
        print('Call_TaskFunc(N_ce): ' + str(Call_TaskFunc))
        print('Wait Vertex(N_we): ' + str(Wait_Vertex))
        print('Condition Vertex(N_cd): ' + str(ConditionVertex))
        print('AverageConditionalBranch(N_br): ' + str(AverageConditionBranch))
        print('Average WCET(C): ' + str(AverageWCET))
        print('WCET_Varience(e): ' + str(WCET_Varience))
        print('-----------Extra Message------------')
        print('TotalConditionBranch:', TotalConditionBranch)
        print('WCET_Total', WCET_Total)
        print('========Debug Message End=========')
    # 输出--文件
    file = open(root + 'FeatureOfPCFG.txt', 'w')
    try:
        file.write('Vertex(|V|): ' + str(Nodes))
        file.write('\nEdges(|E|): ' + str(Edges))
        file.write('\nCall_TaskFunc(N_ce): ' + str(Call_TaskFunc))
        file.write('\nWait Vertex(N_we): ' + str(Wait_Vertex))
        file.write('\nCondition Vertex(N_cd): ' + str(ConditionVertex))
        file.write('\nAverageConditionalBranch(N_br): TotalConditionalBranch/(N_if+N_loop)')
        file.write('\nAverage WCET(C): ' + str(AverageWCET))
        file.write('\nWCET_Varience(e): ' + str(WCET_Varience))
        file.write('\nTotalConditionBranch:' + str(TotalConditionBranch))
        file.write('\nWCET_Total:' + str(WCET_Total))
    except:
        print('I/O Error.')
    finally:
        file.close()


def pdfPrint(Path):
    import os
    os.system('dot -Tpdf ' + Path + ' -o ' + os.path.dirname(Path) + '/FinalOutput2.pdf')


def calcTotalBranch(graph):
    global TotalConditionBranch

    for node in graph.node:
        try:
            # 直接判断菱形形状
            if graph.node[node]['shape'] == 'diamond':
                count = 0
                for n in nx.neighbors(graph, node):
                    count = count + 1
                TotalConditionBranch = TotalConditionBranch + count
                if DEBUG:
                    print(node, graph.node[node]['shape'], count)
            else:
                continue
        except:
            continue


def calcBranch(graph):
    global TotalConditionBranch
    # 计算每个函数的 branch 数量
    result = nx.weakly_connected_component_subgraphs(graph)
    for gh in result:
        # 对于每一个子图，先得到entry结点
        entryNode = ''
        for node in gh.node:
            if node.endswith('_entry'):
                entryNode = node
                break
        numset = set()
        # 从起点一个一个尝试 simple path
        for node in gh.node:
            pathGen = nx.all_simple_paths(gh, entryNode, node)
            count = 0
            for path in pathGen:
                count = count + 1
            if count != 0:
                numset.add(count)
        print("Debug: " + entryNode.replace('_entry', ' numset:'), max(numset))
        if max(numset) > 1:
            # >1 表示有条件分支
            TotalConditionBranch = TotalConditionBranch + max(numset)


def getNodeExit(graph, point):
    '''
    :param graph:
    :param point:
    :return: 返回exit点，类型
    '''
    nodeQueue = queue.Queue()
    nodeInQueued = []

    for succ in graph.successors(point):
        pointInfo[succ].sign.add((point, succ))
        nodeQueue.put(succ)
        nodeInQueued.append(succ)
    while not nodeQueue.empty():
        node = nodeQueue.get()
        # 加入node的succ
        for succ in graph.successors(node):
            if succ not in nodeInQueued:
                # node的sign传给succ

                # TODO 待商榷，是否要切断
                # if 'RETURN' in graph.node[succ]['label']:
                #     print('切断'+point+'->'+succ)
                #     continue

                pointInfo[succ].sign = pointInfo[succ].sign.union(pointInfo[node].sign)
                if succ != point:
                    nodeQueue.put(succ)
                    nodeInQueued.append(succ)
            else:
                if len(pointInfo[succ].sign.union(pointInfo[node].sign)) > 1:
                    # 相遇的结点的bb与point的相同，则清空queue,break，为循环
                    if getBB(succ) == getBB(point):
                        while not nodeQueue.empty():
                            nodeQueue.get()
                        break
                    clearSign(point, nodeInQueued)
                    start_point_model[point] = startPointModel(graph, point, succ, 'Cond')
                    return succ, 'Cond'

    sign_set = list(pointInfo[point].sign)

    for item in graph.successors(point):
        if (point, item) not in sign_set:
            clearSign(point, nodeInQueued)
            start_point_model[point] = startPointModel(graph, point, item, 'Loop')
            return item, 'Loop'


def clearSign(point, nodeInQueued):
    nodeInQueued.append(point)
    for node in nodeInQueued:
        pointInfo[node].sign.clear()


def getExit(graph):
    '''
    :param graph: 经过前面处理过的CFG图
    :param relation: statement与函数调用的图
    :return: 无返回值
    '''
    for point in startPoint:
        pointInfo[point].isExit, pointInfo[point].type = getNodeExit(graph, point)
    # # point='insertion_sort__bb4__3' (4615468136)
    # getNodeExit(graph,'seqpart__bb9__5')


def getCondBranch(graph):
    items = list(start_point_model.items())
    for i in range(len(items)):
        if start_point_model[items[i][0]].type == 'Cond':
            # 拆分branch
            start_point_model[items[i][0]].CondBranch = {0: [], 1: []}
            num = []
            for succ in graph.successors(start_point_model[items[i][0]].start):
                num.append(succ)

            if num[0] > num[1]:
                tmp = num[0]
                num[0] = num[1]
                num[1] = tmp
            num = list(map(getValue, num))

            for node in start_point_model[items[i][0]].v:
                # 如果node是起始结点的话就不用了
                if node == start_point_model[items[i][0]].start:
                    continue
                if num[1] > getValue(node) >= num[0]:
                    start_point_model[items[i][0]].CondBranch[0].append(('v', node))
                else:
                    start_point_model[items[i][0]].CondBranch[1].append(('v', node))

            # 处理 include
            for includeBlock in start_point_model[items[i][0]].includes:
                if num[1] > getValue(includeBlock) >= num[0]:
                    start_point_model[items[i][0]].CondBranch[0].append(('i', includeBlock))
                else:
                    start_point_model[items[i][0]].CondBranch[1].append(('i', includeBlock))


def getBlockRelation(graph, relationDict):
    # 加入函数大Block
    # step.1 parseFunction
    start_point_model[parseFunction + '_entry'] = startPointModel(graph,
                                                                  parseFunction + '_entry',
                                                                  parseFunction + '_exit',
                                                                  None)
    # step.2 callblock
    for callblock in relationDict:
        if not relationDict[callblock].startswith('ort_'):
            start_point_model[relationDict[callblock] + '_entry'] = startPointModel(graph,
                                                                                    relationDict[callblock] + '_entry',
                                                                                    relationDict[callblock] + '_exit',
                                                                                    None)

    items = list(start_point_model.items())
    for j in range(len(items)):
        for k in range(len(items)):
            model1 = start_point_model[items[j][0]]
            model2 = start_point_model[items[k][0]]
            if (j == k):
                continue
            if model1.function != model2.function:
                continue
            if model1.isInclude(model2) and not model2.hasParent():
                model1.include(start_point_model, model1, model2)
    # 利用pointInfo和startpoint进行获取
    getCondBranch(graph)


def combineNodes(IsolatedGraph):
    '''
    :param IsolatedGraph: 判断出入度
    :param Definition: 删除(维护)
    :return:
    '''
    global Definition
    dnodes = set()
    for model in start_point_model.items():
        # start_point_model[model]没有，则表明为Series
        # 合并v中可合并的
        nodeToBeDeleted = set()
        # if model[0]=='_taskFunc2__entry':
        #     pass

        for node in model[1].v:
            # 如果node有且只有一个后继结点，则删除当前的node(加入nodeToTeDeleted),
            # 若successor没在model[1].v中则表明该结点不能删除,taskwait,call,entry,exit
            # if node=='_taskFunc2___bb15__2':
            #     pass

            cnt = 0
            flag = False

            # 以下情况不作处理：标签中含有taskwait,create,call以及_entry和_exit结点
            if 'taskwait' in IsolatedGraph.node[node]['label'] or 'CREATE' in IsolatedGraph.node[node]['label'] \
                    or 'CALL' in IsolatedGraph.node[node]['label'] \
                    or IsolatedGraph.node[node]['label'][1:-1].endswith('_exit') \
                    or IsolatedGraph.node[node]['label'][1:-1].endswith('_entry'):
                continue
            # 以下情况不作处理：形状为菱形（条件分支）
            try:
                if IsolatedGraph.node[node]['shape'] == 'diamond':
                    continue
            except:
                pass

            # 如果flag==true，表明该结点不能删除，下为遍历与node相关的结点
            for snode in nx.all_neighbors(IsolatedGraph, node):
                if snode not in model[1].v and not snode.endswith('_entry') and not snode.endswith('_exit'):
                    flag = True
                    break
                cnt = cnt + 1
            if flag == True or cnt > 2:
                continue
            # 该结点可能可以删除，但还需要看后继是否能够合并该结点
            # cnt==1
            for succ in IsolatedGraph.successors(node):
                if 'taskwait' in IsolatedGraph.node[succ]['label'] or 'CALL' in IsolatedGraph.node[succ]['label'] \
                        or 'CREATE' in IsolatedGraph.node[succ]['label'] \
                        or succ.endswith('_exit') \
                        or succ.endswith('_entry'):
                    # 后继拥有以下特征： taskwait,call,create,_exit,_entry,则不能合并
                    continue
                else:
                    try:
                        # 后继是个菱形（分支），continue
                        if IsolatedGraph.node[succ]['shape'] == 'diamond':
                            continue
                    except:
                        pass
                    try:
                        # 后继的all_neighbour数量>2，continue
                        cnt2 = 0
                        for n in nx.all_neighbors(IsolatedGraph, succ):
                            cnt2 = cnt2 + 1
                        if cnt2 > 2:
                            continue
                    except:
                        pass
                    # 添加入待删除的结点
                    nodeToBeDeleted.add(node)
        nodeToBeDeleted = sorted(list(nodeToBeDeleted), key=getValue)
        # 删除nodeToBeDeleted中保存的结点, WCET进行叠加,taskwait,call
        for dnode in nodeToBeDeleted:
            # 叠加到将当前dnode的wcet叠加到succ
            for succ in IsolatedGraph.successors(dnode):
                if succ in WCET_Table:
                    WCET_Table[succ] = WCET_Table[succ] + WCET_Table.get(dnode, 0)
                    # 删除WCET_Table中的dnode
                    if dnode in WCET_Table:
                        WCET_Table.pop(dnode)
                Definition = Definition.replace('"' + dnode + '"', '')
                dnodes.add(dnode)
        model[1].v = model[1].v - set(nodeToBeDeleted)
    for dnode in dnodes:
        # 在 isolated中删除该结点，连接前驱和后继
        pre = []
        it = IsolatedGraph.predecessors(dnode)
        for p in it:
            pre.append(p)
        it = IsolatedGraph.successors(dnode)
        post = []
        for p in it:
            post.append(p)
            # 将dnode的值加给后继
            try:
                IsolatedGraph.node[p]['wcet'] = \
                    str(int(IsolatedGraph.node[p]['wcet']) + int(IsolatedGraph.node[dnode]['wcet']))
            except:
                print('Warning:WCET叠加出现问题(' + dnode + '->' + p + ')')
                pass
        for re in pre:
            for po in post:
                IsolatedGraph.add_edge(re, po)

        IsolatedGraph.remove_node(dnode)
        # TODO 在start_point_model中找到要删除的点，将其删除
        for m in start_point_model.items():
            if dnode in m[1].v:
                m[1].v.remove(dnode)


def delFile(filePath):
    os.remove(filePath)


def connectEdgeForGraph(G, relationDict):
    for node in G.nodes:
        if ('CREATE' in G.node[node]['label'] or 'CALL' in G.node[node]['label']):
            Function_entry = relationDict[node] + '_entry'
            Function_exit = relationDict[node] + '_exit'
            # 判断是否存在当前结点，因为要考虑调用系统库的情况（系统库没有出现在图中）
            if G.has_node(Function_entry) or G.has_node(Function_exit):
                nextNode = None
                for nod in nx.neighbors(G, node):
                    nextNode = nod
                if not relationDict[node].startswith('_taskFunc'):
                    G.add_edge(Function_exit, nextNode, color='red')
                    # 删去不必要的边
                    G.remove_edge(node, nextNode)
                G.add_edge(node, Function_entry, color='blue')


def addWCET(graph):
    for item in WCET_Table:
        if graph.has_node(item):
            # 合并再添加标签
            # graph.node[item]['label'] = graph.node[item]['label'] + '\nWCET=' + str(WCET_Table[item])

            graph.node[item]['wcet'] = str(WCET_Table[item])


def addWCETBoundToLabel(graph):
    for node in graph.nodes:
        try:
            graph.node[node]['label'] = graph.node[node]['label'] + '\nWCET=' + graph.node[node]['wcet']
        except:
            pass
        try:
            graph.node[node]['label'] = graph.node[node]['label'] + '\nbound=' + graph.node[node]['bound']
        except:
            pass


def addBound(graph):
    '''
    :param graph:
    :return: 给结点添加bound
    '''
    try:
        bound_info = open(boundPath, 'r')
    except FileNotFoundError:
        print('bound文件不存在,bound未添加')
        return
    lines = bound_info.readlines()
    bound_info.close()
    for line in lines:
        line = line.strip()
        if r.match(bound_regex, line):
            name, value_str = line.split(':')
            if graph.has_node(name):
                graph.node[name]['bound'] = value_str
                # graph.node[name]['label'] = graph.node[name]['label'] + '\nbound=' + value_str
            else:
                print('Warning:图中不含' + name)


if __name__ == '__main__':
    print("处理Relation表...")
    relation = parseRelation(relationPath)
    # 预处理
    print("预处理CFG...")
    preprocess(dotPath)
    # 得到cluster定义
    print("获取图的Cluster__定义...")
    Definition = open(dotPath + '_dec').read()
    delFile(dotPath + '_dec')
    # 调用networkx处理CFG
    print("处理CFG图...")
    IsolatedGraph = nx.nx_pydot.read_dot(dotPath + '_pd')
    delFile(dotPath + '_pd')
    parse(parseFunction, IsolatedGraph, relation)
    print("获取Loop,Condition出点...")
    getExit(IsolatedGraph)
    print('获取block嵌套关系')
    getBlockRelation(IsolatedGraph, relation)
    print('生成WCET表')
    genWCETValue(IsolatedGraph)
    print('加入WCET标记')
    addWCET(IsolatedGraph)
    print('加入bound信息')
    addBound(IsolatedGraph)
    print('连接调用关系')
    connectEdgeForGraph(IsolatedGraph, relation)
    print('合并结点')
    combineNodes(IsolatedGraph)
    print('添加结点信息到label')
    addWCETBoundToLabel(IsolatedGraph)
    # 输出部分
    nx.nx_pydot.write_dot(IsolatedGraph, dotOutput)
    print("加入图的Cluster__定义...")
    fileContext = open(dotOutput, 'r').readlines()
    FinalOutput = open(dotOutput + '_Final2', 'w')
    for line in fileContext[:-1]:
        FinalOutput.write(line)
    print("生成最终Dot图...")
    FinalOutput.write(Definition)
    FinalOutput.close()
    print("生成最终PDF...")
    # 调用系统 graphviz生成最终的dot
    pdfPrint(dotOutput + '_Final2')
