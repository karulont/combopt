import networkx as nx
from gml_read import read_gml2
from sys import argv


if len(argv) != 3:
    print ("Usage: ",argv[0], "input_file output_file")
    exit(1)

G = read_gml2(argv[1])
H = read_gml2(argv[2])


# Check whether H is a subgraph of G

for v,d in G.nodes_iter(data=True):
    d['in_H'] = False

for u,d in H.nodes_iter(data=True):
    v = d['orig']
    if G.node[v]['in_H']:
        print ("Vertex ",v," appears twice in H")
        exit(10)
    G.node[v]['in_H'] = True

total_cost = 0

for u1,u2 in H.edges_iter():
    v1 = H.node[u1]['orig']
    v2 = H.node[u2]['orig']
    if not v2 in G[v1]:
        print ("H has an edge {",v1,",",v2,"} which doesn't appear in G")
        exit(10)
    else:
        total_cost += G[v1][v2]['c']

for v,d in G.nodes_iter(data=True):
    if d['T'] and not d['in_H']:
        print ("Terminal vertex ",v," is not in H")
        exit(10)

if nx.is_connected(H):
    print ("OK. Total cost =",total_cost)
else:
        print ("H is not connected")
        exit(10)
