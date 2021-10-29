# <OmpTG>  Copyright (C) <2021>  < Tao Jin; Jinrong Liu; >
# This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
# This is free software, and you are welcome to redistribute it
# under certain conditions; type `show c' for details.
# sweet -i=complex.alf func=xxx -c extref=off size=off --dot-print file=complex g=cg
import networkx as nx
import os
import pydot

'''
#Used for locally generated files

pathfile='/Users/jintao/Bots_OpenMP_Tasks/'
filepart='fft'
pathfile=pathfile+filepart+'/complex1.dot'
outpath='/Users/jintao/PycharmProjects/test/'
'''


def pdfPrint(Path, filename):
    import os
    os.system('dot -Tpdf ' + Path + ' -o ' + os.path.dirname(Path) + '/' + filename + '.pdf')
    if __name__ == '__main__':
        G = nx.nx_pydot.read_dot(pathfile)
        # nodes=G.node[1]['label']
        allnodes = nx.get_node_attributes(G, 'label')
        alledges = list(G.edges())
        tasknodes = {}
        waitnode = ''
        taskpath = {}
        tasknodeslist = []
        task_root_node = {}
        looplist = []
        iswait = {}
        for i in allnodes.keys():
            if allnodes[i].find("taskFunc") != -1:  # 寻找taskFunc的节点
                tasknodes[i] = allnodes[i]
                tasknodeslist.append(i)
        for i in allnodes.keys():
            if allnodes[i].find("ort_taskwait") != -1:  # 寻找taskwait的节点
                waitnode = i

        for i in tasknodes.keys():
            path = nx.shortest_path(G, source='0', target=i, weight=None)
            taskpath[i] = path
        for i in taskpath.keys():
            flag = 0
            for j in tasknodeslist:
                if (j in taskpath[i]) and (j != i):
                    task_root_node[i] = j
                    flag = 1
            if flag == 0:
                task_root_node[i] = '0'

        for i in list(nx.simple_cycles(G)):
            count = 0
            templist = []
            for j in tasknodeslist:
                if j in i:
                    templist.append(j)
            if '0' in i:
                templist.append('0')
            looplist.append(templist)

        tempn = []
        for i in alledges:
            if waitnode in i:
                tempn.append(i[0])
        for i in tasknodeslist:
            iswait[i] = '0'

        for i in tempn:
            for j in alledges:
                if (i == j[0]) and (j[1] in tasknodeslist):
                    iswait[j[1]] = '1'
        nodess = []
        for i in allnodes:
            if i not in tasknodeslist and i != waitnode and i != '0':
                nodess.append(i)
        G.remove_nodes_from(nodess)
        edgess = []
        edgess = alledges[:]
        G.remove_edges_from(edgess)
        # 加普通边
        for i in task_root_node.keys():
            G.add_edge(task_root_node[i], i)
        # 加loop
        for i in looplist:
            if len(i) == 1:
                # G.edges([i, i]['color'] = "blue")
                G.add_edge(i[0], i[0], color='blue')
            else:
                for j in range(0, len(i)):
                    if j != len(i) - 1:
                        G.add_edge(i[j], i[j + 1], color='blue')
                    else:
                        G.add_edge(i[j], i[0], color='blue')
        # 加wait关系
        for i in iswait.keys():
            if iswait[i] == '1':
                # G.edges[i, waitnode]['color'] = "green"
                G.add_edge(i, waitnode, color='green')

        nx.nx_pydot.write_dot(G, 'temp.dot')

        # outpath=outpath+filepart+'.dot'
        outpath = outpath + 'temp.dot'
        pdfPrint(outpath, filepart)
        os.remove(outpath)
        print('Generate taskCG successfully')
