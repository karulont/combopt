import networkx as nx

# from gml_read import read_gml2
# g = read_gml2("steiner-small.gml")

def read_gml2(path):

    # Read file lines
    f = open(path)
    lines = f.readlines()
    f.close()

    # Split lines into symbols
    syms = []
    for line in lines:
        line = line.strip().split(' ')
        if len(line) != 0 and line[0] == '#': # skip comments
            continue
        for sym in line:
            syms.append(sym)
    n_syms = len(syms)

    # Find node labeled 'graph'
    has_graph = False
    i_sym = 0
    while not has_graph and i_sym < n_syms:
        sym = syms[i_sym]
        i_sym += 1
        if sym == 'graph':
            has_graph = True
            break

    if not has_graph:
        print ("Couldn't find a graph")
        return

    G = nx.Graph()

    # Recurse the graph structure
    level = 0
    expect_value = True
    attribs = {1:G.graph}
    current_node = None
    current_edge = None
    while level >= 0 and i_sym < n_syms:
        sym = syms[i_sym]
        if expect_value:
            value = None
            if sym == '[':       # list
                level += 1
            elif sym[0] == '\"': # string
                value = sym
                while syms[i_sym][-1] != '\"':
                    i_sym += 1
                    value += ' ' + syms[i_sym]
                value = value[1:-1]
            elif '.' in sym:
                value = float(sym)
            else:
                value = int(sym)
            if value != None:
                #if level not in attribs:
                #    attribs[level] = {}
                attribs[level][current_key] = value
            expect_value = False
        else:
            if sym == ']':       # list end
                level -= 1
                if level == 1:
                    if current_node != None:
                        id = current_node['id']
                        current_node.pop('id', None)   # don't need id in attribs
                        G.add_node(id, current_node)
                        current_node = None
                    elif current_edge != None:
                        source = current_edge['source']
                        target = current_edge['target']
                        current_edge.pop('source', None)
                        current_edge.pop('target', None)
                        G.add_edge(source, target, current_edge)
                        current_edge = None
            else:
                if level == 1:
                    if sym == 'node':
                        current_node = {}
                        attribs[level + 1] = current_node
                    elif sym == 'edge':
                        current_edge = {}
                        attribs[level + 1] = current_edge
                current_key = sym
                expect_value = True
        i_sym += 1

    return G
