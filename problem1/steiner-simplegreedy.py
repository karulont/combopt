import networkx as nx
from gml_read import read_gml2
from graph_util import edge_order, draw_graph
from sys import argv

def main():
  # G = read_gml2(argv[1])
  G = read_gml2("steiner-010000.gml")

  # candidate edge set D
  D = {}       # {cost:[edges]} pairs
  T = [n for n, d in G.nodes_iter(data=True) if d['T']] # terminals
  for u in T:
    for e in G.edges_iter(u, data=True):
      cost = e[2]['c']
      if cost not in D:
        D[cost] = []
      D[cost].append(edge_order(e))
  #print("initial candidate edge set D: " + str(D))

  UF = nx.Graph()
  UF.add_nodes_from(T)
  cyclic_edges = set() # edges that are known to form a cycle

  while not nx.is_connected(UF):
    if not D:
      print("Not sufficiently connected")
      return

    # find cheapest edge f in D
    f_cost = min(D)
    f = D[f_cost].pop()
    if not D[f_cost]:
      D.pop(f_cost, None)
    #print("select f: " + str(f) + ", cost: " + str(G.edge[f[0]][f[1]]['c']))

    # are the two nodes connected (will we create a cycle?)
    if (f[0] in UF and f[1] in UF) and nx.has_path(UF, f[0], f[1]):
      cyclic_edges.add((f[0], f[1]))
    else:
      UF.add_edge(f[0], f[1])

    # print(str(len(D_costs)))

    # add edges incident on f to D
    for e in G.edges_iter([f[0], f[1]]):
      if not UF.has_edge(e[0], e[1]):
        e = edge_order(e)
        if e not in cyclic_edges:
          if e[0] == f[0] and e[1] == f[1]: # \ f
            continue
          cost = G.edge[e[0]][e[1]]['c']
          if cost not in D:
            D[cost] = []
          D[cost].append(e)

  # restore data
  for n, d in UF.nodes_iter(data=True):
    d.update(G.node[n])
  for e in UF.edges_iter():
    UF[e[0]][e[1]].update(G[e[0]][e[1]])

  return UF


if __name__ == '__main__':
  UF = main()
  if UF:
    #print("Steiner tree nodes:",UF.nodes())
    #print("Steiner tree edges:",UF.edges())
    #draw_graph(UF)
    #nx.write_gml(G, argv[2])
    print('Total cost:', sum([d['c'] for u, v, d in UF.edges_iter(data=True)]))
    nx.write_gml(UF, "steiner-010000-result.gml")
