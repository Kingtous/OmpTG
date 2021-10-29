# <OmpTG>  Copyright (C) <2021>  < Tao Jin; Jinrong Liu; >
# This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
# This is free software, and you are welcome to redistribute it
# under certain conditions; type `show c' for details.
import networkx as nx
import sys, getopt
from networkx.drawing.nx_pydot import write_dot
import re
import os
# =========================
from PreprocessDot import preprocess

# =========================

# 设置工作目录
# root='/home/rtco/Desktop/Bots_OpenMP_Tasks/sort/PCFG/'
root = '/Users/liuuujr/neww/'
# =======DOT存放位置===============
dotPath = root + 'sort_sw.dot'
# =======relation.txt存放位置======
relationPath = root + 'relati.txt'
# =======需要处理的函数入口（暂时不用）======
parseFunction = '_thrFunc0_'
# =======WCET目录====================
wctPath = root + 'sot.wct'
# ===========cluster_定义==========
Definition = ''
# ========输出================================
# =======dot输出==========
dotOutput = root + 'sort_pro.dot'

# =======特征输出==========
Edges = 0
Nodes = 0
Call_TaskFunc = 0
ConditionVertex = 0
AverageConditionBranch = 0
AverageWCET = 0
WCET_Varies = 0
Wait_Vertex = 0
# ========辅助计算数据
TotalConditionBranch = 0
DEBUG = False
# ===========WCET Config=========
Program_RUN = 33
WCET_Total = 0


# ===============================


def NodeWait(graph):
    graph.add_edge('_taskFunc8__exit', '_thrFunc0___bb6', color='green')
    graph.add_edge('_taskFunc2__exit', 'cilksort_par__bb16__32', color='green')
    graph.add_edge('_taskFunc3__exit', 'cilksort_par__bb16__32', color='green')
    graph.add_edge('_taskFunc4__exit', 'cilksort_par__bb16__32', color='green')
    graph.add_edge('_taskFunc5__exit', 'cilksort_par__bb16__32', color='green')
    graph.add_edge('_taskFunc6__exit', 'cilksort_par__bb16__35', color='green')
    graph.add_edge('_taskFunc7__exit', 'cilksort_par__bb16__35', color='green')
    graph.add_edge('_taskFunc0__exit', 'cilkmerge_par__bb59__40', color='green')
    graph.add_edge('_taskFunc1__exit', 'cilkmerge_par__bb59__40', color='green')


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
                            graph.node[returnNode]['label'] + '\nRETURN\n'

    # 删除returnNode
    for node in NodeNeedTobeDelete:
        graph.remove_node(node)

        global Definition
        Definition = Definition.replace('"' + node + '"', '')


def AddWCETValue(graph):
    WCET_Varies_Dict = {}

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
                            WCET_Varies_Dict[wctLine] = WCET_Varies_Dict.get(wctLine, 0) + 1
                        graph.node[name]['label'] = \
                            graph.node[name]['label'] + '\n' + \
                            'WCET=' + wctLine

                    global WCET_Varies, AverageWCET
                    WCET_Varies = len(WCET_Varies_Dict)
                    AverageWCET = WCET_Total / Nodes



                except:
                    continue
        if DEBUG:
            print('WCET Dict=', end='')
            print(WCET_Varies_Dict)

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
        else:
            graph.node[callBlock]['label'] = callBlock + '\n' + 'CALL ' + relationDict[callBlock]

        Function_entry = relationDict[callBlock] + '_entry'
        Function_exit = relationDict[callBlock] + '_exit'

        # 判断是否存在当前结点，因为要考虑调用Library的情况
        if graph.has_node(Function_entry) or graph.has_node(Function_exit):

            nextNode = None

            for nod in nx.neighbors(graph, callBlock):
                nextNode = nod
            if not relationDict[callBlock].startswith('_taskFunc'):
                graph.add_edge(Function_exit, nextNode, color='red')
                # 删去不必要的边
                graph.remove_edge(callBlock, nextNode)
            graph.add_edge(callBlock, Function_entry, color='blue')

    # 处理 CFG
    deleteTaskReturnNode(graph)
    changeShapeOfCondition(graph)
    NodeWait(graph)
    parrallel(graph)
    deleteUndependNode(graph)
    calcTotalBranch(graph)
    AddWCETValue(graph)
    # 输出
    printFeatureOfGraph(graph)


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
        print('WCET_Varies(e): ' + str(WCET_Varies))
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
        file.write('\nWCET_Varies(e): ' + str(WCET_Varies))
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


# 处理输入的文件路径
def init_argv(Argslist, current_dir):
    global dotPath, relationPath, wctPath, root, dotOutput

    # # =======DOT存放位置===============
    if os.path.isabs(Argslist['d']) == False:  # 相对路径
        if Argslist['d'].find("../") != -1:  # 相对路径格式为"格式1：../文件夹/文件"
            dotPath = current_dir[:current_dir[:-1].rfind("/") + 1] + Argslist['d'][3:]
        elif Argslist['d'].find("./") != -1:
            wctPath = current_dir + Argslist['d'][2:]
        else:
            dotPath = current_dir + Argslist['d']  # 相对路径格式为"格式1：文件夹/文件   格式2： ./文件夹/文件"

    else:  # 绝对路径
        dotPath = Argslist['d']
    # # =======relation存放位置===============
    if os.path.isabs(Argslist['r']) == False:
        if Argslist['r'].find("../") != -1:
            relationPath = current_dir[:current_dir[:-1].rfind("/") + 1] + Argslist['r'][3:]
        elif Argslist['r'].find("./") != -1:
            wctPath = current_dir + Argslist['r'][2:]
        else:
            relationPath = current_dir + Argslist['r']

    else:
        relationPath = Argslist['r']

    # # =======wct存放位置===============
    if os.path.isabs(Argslist['w']) == False:
        if Argslist['w'].find("../") != -1:
            wctPath = current_dir[:current_dir[:-1].rfind("/") + 1] + Argslist['w'][3:]

        elif Argslist['w'].find("./") != -1:
            wctPath = current_dir + Argslist['w'][2:]
        else:
            wctPath = current_dir + Argslist['w']

    else:
        wctPath = Argslist['w']

    # # =======root目录===============好像没用了
    root_flag_loc = dotPath.rfind("/")
    root = dotPath[:root_flag_loc + 1]
    # # =======dotOutput===============
    dotOutput = dotPath[: dotPath.rfind(".")] + "_pro.dot"


if __name__ == '__main__':
    # currentdir = os.path.dirname(__file__) + "/"
    currentdir = os.getcwd() + "/"
    op_p = False  # path
    op_d = False  # dot
    op_r = False  # relation
    op_w = False  # wct
    # Process
    getArgs = {}
    options, args = getopt.getopt(sys.argv[1:], "d:r:w:")
    for op, value in options:

        if op == '-d':
            op_d = True
            # # =======DOT存放位置===============
            # dotPath = current_dir + value
            getArgs['d'] = value
            continue
        if op == '-r':
            op_r = True
            getArgs['r'] = value
            # # =======需要处理的函数入口（暂时不用）======
            # relationPath =current_dir + value
            continue
        if op == '-w':
            op_w = True
            getArgs['w'] = value
            # # =======WCET目录====================
            # wctPath =current_dir + value

    if (op_d == False) or (op_r == False) or (op_w == False):
        print('Please Import the file u\'d like to ')

        # //print(current_dir1)
    else:

        init_argv(getArgs, currentdir)

        print("处理Relation表...")
        relation = parseRelation(relationPath)
        # 预处理
        print("预处理CFG...")
        preprocess(dotPath)
        # 得到cluster定义
        print("获取图的Cluster__定义...")
        Definition = open(dotPath + '_dec').read()
        # 调用networkx处理CFG
        print("处理CFG图...")
        graph = nx.nx_pydot.read_dot(dotPath + '_pd')
        parse(parseFunction, graph, relation)
        write_dot(graph, dotOutput)
        # 加入定义
        print("加入图的Cluster__定义...")
        fileContext = open(dotOutput, 'r').readlines()
        FinalOutput = open(dotOutput + '_Final', 'w')
        for line in fileContext[:-1]:
            FinalOutput.write(line)
        print("生成最终Dot图...")
        FinalOutput.write(Definition)
        FinalOutput.close()
        print("生成最终PDF...")
        # 调用系统 graphviz生成最终的dot
        pdfPrint(dotOutput + '_Final')

else:
    print("Please run this scripts directly.")
