import networkx as nx
from heapq import *
from sys import argv
    
def main():
        G = nx.read_gml(argv[1])
        
        terms = [i for i,d in G.nodes(data=True) if d['T']]
        
        edges = []

        number_of_components = len(terms)
        heaps = {}
        
        for t in terms:
                edge = min(G.edges(terms[0], data=True), key = lambda e: e[2]['c'])
                edges.append(edge)
                heaps[t] = [(0,t)]

        for i,t in G.nodes_iter(data=True): 
            t['c'] = None
       
        for t in terms: 
            G.nodes(data=True)[t][1]['c'] = {'val':t}

        while number_of_components != 1:
            for i in terms:
                print ("das: ", i, number_of_components, heaps)
                if heaps[i] == []:
                    continue
                cost,v = heappop(heaps[i])
                comp = G.nodes(data = True)[v][1]['c']
                while heaps[i] != [] and comp != None and comp['val'] == i:
                    cost,v = heappop(heaps[i])
                if comp == None:
                    for v1,v2,d in G.edges(v, data=True):
                        heappush(heaps[i], (d['c'], v2))
                    G.nodes(data =True)[v][1]['c'] = G.nodes(data = True)[i][1]['c']
                elif comp['val'] != i:
                    print("merge")
                    h1 = heaps[i]
                    h2 = heaps[comp['val']]
                    hm = h1 + h2
                    heapify(hm)
                    heaps[i] = hm
                    heaps[comp['val']] = hm
                    comp['val'] = G.nodes(data = True)[i][1]['c']['val']
                    number_of_components -= 1
        
if __name__ == '__main__':
        main()


