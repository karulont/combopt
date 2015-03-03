import networkx as nx

# from read_mcf import read_mcf
# edges = read_mcf("mcf-20000--flow-20000")

def read_mcf(path):
    f = open(path)
    edges = []
    for line in f.readlines():
        line = line.split(' ', 2)
        attrs = {} # eval(line[2])
        data = line[2].split(',')
        for attr in data:
            attr = attr.rstrip("}\n")
            li = attr.find('\'') + 1
            ri = attr.find('\'', li)
            name = attr[li:ri]
            vi = attr.find(':', ri) + 1
            attrs[name] = int(attr[vi:])
        edge = (int(line[0]), int(line[1]), attrs)
        #edge = (int(line[0]), int(line[1]), attrs['c'], attrs['u'])
        edges.append(edge)
    f.close()
    return edges

def read_mcf_nx(path):
    edges = read_mcf(path)
    g = nx.DiGraph()
    for v1,v2,attrs in edges:
        g.add_edge(v1,v2,attrs)
        g.node[v1]['label'] = v1
        g.node[v2]['label'] = v2
    return g
