import networkx as nx
from FunctionModel import *
import copy
import re
import os
import queue

# =========================
# <OmpTG>  Copyright (C) <2021>  < Tao Jin; Jinrong Liu; >
# This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
# This is free software, and you are welcome to redistribute it
# under certain conditions; type `show c' for details.
from PreprocessDot import preprocess

# =========================

# 设置工作目录
root = '/home/kingtous/Bots_OpenMP_Tasks/fft/PCFG/_thrFunc1_/'
# =======DOT存放位置===============
dotPath = root + 'fft_sweet.dot'
# =======relation.txt存放位置======
relationPath = root + 'relation.txt'
# =======需要处理的函数入口======
parseFunction = '_thrFunc1_'
# =======WCET目录====================
wctPath = root + '../fft.wct'
EFGDir = root + 'EFG/'
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
TotalConditionBranch = 0
DEBUG = False
WCET_Varience_Data = []
# ===========WCET Config=========
Program_RUN = 33
WCET_Total = 0
# ===============================


function_set = set()


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


def AddWCETValue(graph):
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
                        graph.node[name]['label'] = \
                            graph.node[name]['label'] + '\n' + \
                            'WCET=' + wctLine

                    global WCET_Varience, AverageWCET
                    import numpy
                    WCET_Varience = numpy.var(WCET_Varience_Data)
                    AverageWCET = WCET_Total / Nodes
                except:
                    continue
        if DEBUG:
            print('WCET Dict=', end='')
            print(WCET_Varience)

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
    AddWCETValue(graph)
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
    os.system('dot -Tpdf ' + Path + ' -o ' + os.path.dirname(Path) + '/FinalOutput.pdf')


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


processed_Function = []
EFGList = []
ModeDict = {}
graphOutputed = []
# 储存已经遍历过的path
pathSelected = {}
pathSum = []
output_cnt = 0


def connectEdgeForEFG(EFG, relationDict):
    for node in EFG.nodes:
        if ('CREATE' in EFG.node[node]['label'] or 'CALL' in EFG.node[node]['label']):
            Function_entry = relationDict[node] + '_entry'
            Function_exit = relationDict[node] + '_exit'
            # 判断是否存在当前结点，因为要考虑调用系统库的情况（系统库没有出现在图中）
            if EFG.has_node(Function_entry) or EFG.has_node(Function_exit):
                nextNode = None
                for nod in nx.neighbors(EFG, node):
                    nextNode = nod
                if not relationDict[node].startswith('_taskFunc'):
                    EFG.add_edge(Function_exit, nextNode, color='red')
                    # 删去不必要的边
                    EFG.remove_edge(node, nextNode)
                EFG.add_edge(node, Function_entry, color='blue')


def clusterForEFG(graph, EFG):
    '''
    :原理：通过全局变量Definition，删除当前EFG当中没有的点
    :param EFG: 未加Cluster的
    :return: 返回修改好的Definition
    '''
    global Definition
    # 查找EFG中没有的结点，在Definition中删除
    Definition_Copy = copy.deepcopy(Definition)
    Nodes = []
    for node in graph.nodes:
        Nodes.append(node)
    for node in EFG.nodes:
        Nodes.remove(node)
    for node in Nodes:
        regex = r'"' + node + '"'
        Definition_Copy = re.sub(regex, '', Definition_Copy)
    return Definition_Copy


def genEFG(graph, path, keylist, relation):
    '''
    :param graph: 总图
    :param path: 当前选择的路径集合
    :param keylist: path的index，path的顺序与keylist相同
    :param relation: statement-relation
    :return: 不返回，生成用 dot 表示的图文件
    '''
    global output_cnt
    EFG = nx.MultiDiGraph()
    # 先计算当前path需要加入那些函数path
    functionsForCurrentPath = set()
    functionsForCurrentPathQueue = queue.Queue()
    # 入口点开始，开始广度优先搜索需要添加的结点
    functionsForCurrentPathQueue.put(parseFunction)
    while not functionsForCurrentPathQueue.empty():
        functionLabel = functionsForCurrentPathQueue.get()
        if functionLabel not in keylist:
            # Maybe System Library
            continue
        elif functionLabel in functionsForCurrentPath:
            continue
        for vertex in path[keylist.index(functionLabel)][functionLabel]:
            if vertex in relation.keys() and not relation[vertex].startswith('ort_'):
                functionsForCurrentPathQueue.put(relation[vertex])
        functionsForCurrentPath.add(functionLabel)
    for item in functionsForCurrentPath:
        index = ModeDict[item].pathModel.pathList.index(path[keylist.index(item)][item])
        EFG = nx.compose(EFG, ModeDict[item].pathModel.subgraphList[index])
    connectEdgeForEFG(EFG, relation)
    # 解决图的重复问题
    for gh in graphOutputed:
        if nx.is_isomorphic(gh, EFG):
            return
    graphOutputed.append(copy.deepcopy(EFG))

    # 输出DOT文件
    print('输出第' + str(output_cnt) + '张图')
    nx.nx_pydot.write_dot(EFG, EFGDir + str(output_cnt) + '.dot')
    file = open(EFGDir + str(output_cnt) + '.dot', 'r')
    fileData = file.readlines()
    file.close()
    delFile(EFGDir + str(output_cnt) + '.dot')
    file = open(EFGDir + str(output_cnt) + '_EFG.dot', 'w')
    for line in fileData[:-1]:
        file.write(line)
    # 生成加框代码
    currentClusterDefition = clusterForEFG(graph, EFG)
    file.write(currentClusterDefition)
    file.close()
    # 将DOT转换输出PDF文件
    os.system('dot -Tpdf ' + EFGDir + str(output_cnt) + '_EFG.dot' + ' -o ' + EFGDir + str(output_cnt) + '_EFG.pdf')
    output_cnt = output_cnt + 1
    if (output_cnt > graphLimited):
        print('抽取结束')
        exit(0)


def hasPath():
    '''
    :return: 返回所有ModeDict中元素的PathModel中的选择队列是否为空
    '''
    for key in ModeDict.keys():
        if not ModeDict[key].pathModel.pathNoneSelected.empty():
            return True
    return False


def getPathSelectionSummary(graph, path, keylist, point, relation):
    '''
    :param graph:总图
    :param path: 初始/上一次路径
    :param keylist: 顺序list
    :param point: keylist的下标
    :return: 不返回，处理完即抽取完EFG
    '''
    if point >= ModeDict.__len__():
        genEFG(graph, path, keylist, relation)
        return
    else:
        while not ModeDict[keylist[point]].pathModel.pathNoneSelected.empty():
            ModeDict[keylist[point]].pathModel.pathSelectedNow = ModeDict[
                keylist[point]].pathModel.pathNoneSelected.get()
            path1 = copy.deepcopy(path)
            path1.append({keylist[point]: ModeDict[keylist[point]].pathModel.pathSelectedNow})
            getPathSelectionSummary(graph, path1, keylist, point + 1, relation)
        for path in ModeDict[keylist[point]].pathModel.pathList:
            ModeDict[keylist[point]].pathModel.pathNoneSelected.put(path)
        ModeDict[keylist[point]].pathModel.pathSelectedNow = None


def addEdgesForEmptyBody(path, subgraph):
    '''
    :param path: [list]当前的执行路径
    :param subgraph: 子图
    :return: 不返回，直接修改subgraph
    '''
    for i in range(len(path) - 1):
        subgraph.add_edge(path[i], path[i + 1])


def dfs(pathsList, graph, now, src, dest, path, dict, maxLimited):
    if (len(pathsList) > pathLimited):
        return
    if len(path) > maxLimited:
        return
    elif path[-1] == dest:
        pathsList.append(copy.deepcopy(path))
        return
    iter = graph.neighbors(now)
    for node in iter:
        path1 = copy.copy(path)
        path1.append(node)
        dict1 = copy.copy(dict)
        if (dict1.get(node, 0) + 1 > bound):
            continue
        dfs(pathsList, graph, node, src, dest, path1, dict1, maxLimited)


def calcMaxLimited(graph, functionName):
    # maxLimited数量的确定：先确定为当前子图的结点数的两倍
    maxLimited = 0
    for node in graph.nodes:
        if node.startswith(functionName):
            maxLimited = maxLimited + 1
    return maxLimited * 2


def findAllPaths(graph, functionName, src, dest, maxLimited):
    pathsList = []
    if not graph.has_node(src) or not graph.has_node(dest):
        raise Exception
    dfs(pathsList, graph, src, src, dest, [src], {}, maxLimited)
    return pathsList


def graphEFG(graph, relation):
    '''
    :param graph: 经过前面处理过的CFG图
    :param relation: statement与函数调用的图
    :return: 无返回值
    '''
    import sys
    sys.setrecursionlimit(1000000)
    for callblock in function_set:
        try:
            # it = nx.all_simple_paths(graph, callblock + '_entry', callblock + '_exit')
            print('抽取EFG图：' + '搜索' + callblock + '的路径...')
            it = findAllPaths(graph, callblock, callblock + '_entry', callblock + '_exit',
                              calcMaxLimited(graph, callblock))
        except Exception as e:
            print('Warning:skip:' + callblock + '\n' + str(e))
            continue
        paths = []
        pM = pathModel()
        for path in it:
            paths.append(path)
            subgraph = nx.create_empty_copy(graph.subgraph(path), True)
            addEdgesForEmptyBody(path, subgraph)
            pM.addPathModel(path, subgraph, relation)

        model = functionModel(callblock, pM, [])
        for node in graph.nodes:
            if node.startswith(callblock):
                model.nodesList.append(node)
        ModeDict[callblock] = model

    # print(ModeDict['diff'].pathModel.pathList)
    print('路径搜索完成，开始生成图')
    keylist = list(ModeDict.keys())
    # 获取路径总和，并且生成一种解决方案就生成dot文件
    getPathSelectionSummary(graph, [], keylist, 0, relation)


def delFile(filePath):
    os.remove(filePath)


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
    EFG = nx.nx_pydot.read_dot(dotPath + '_pd')
    delFile(dotPath + '_pd')
    parse(parseFunction, EFG, relation)
    print("抽取EFG图...")
    graphEFG(EFG, relation)
    print('抽取结束')
    # 加入定义
    # print("加入图的Cluster__定义...")
    # fileContext = open(dotOutput, 'r').readlines()
    # FinalOutput = open(dotOutput + '_Final', 'w')
    # for line in fileContext[:-1]:
    #     FinalOutput.write(line)
    # print("生成最终Dot图...")
    # FinalOutput.write(Definition)
    # FinalOutput.close()
    # print("生成最终PDF...")
    # # 调用系统 graphviz生成最终的dot
    # pdfPrint(dotOutput + '_Final')
