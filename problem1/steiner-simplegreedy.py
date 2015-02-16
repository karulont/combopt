import networkx as nx
from gml_read import read_gml2
from graph_util import edge_order, draw_graph
from sys import argv

def main():
  # G = read_gml2(argv[1])
  G = read_gml2("steiner-010000")

  D = set() # candidate edge set
  T = [n for n, d in G.nodes(data=True) if d['T']] # terminals
  for u in T:
    for e in G.edges(u):
      D.add(edge_order(e))
  #print("initial candidate edge set D: " + str(D))

  UF = nx.Graph()
  UF.add_nodes_from(T)
  cyclic_edges = set() # edges that are known to form a cycle

  while not nx.is_connected(UF):
    if len(D) == 0:
      print("Not sufficiently connected")
      return None

    # find cheapest edge f in D
    min_f = float("inf")
    for f_i in D:
      f_cost = G.edge[f_i[0]][f_i[1]]['c']
      if f_cost < min_f:
        min_f = f_cost
        f = f_i
    f = edge_order(f)
    #print("select f: " + str(f) + ", cost: " + str(G.edge[f[0]][f[1]]['c']))

    # are the two nodes connected (will we create a cycle?)
    if (f[0] in UF and f[1] in UF) and nx.has_path(UF, f[0], f[1]):
      cyclic_edges.add(f)
    else:
      UF.add_edge(f[0], f[1])

    print(str(UF.number_of_edges()))
    #if UF.number_of_edges() > 500:
    #  return

    # add edges incident on f to D
    #print("add to D: "+str(G.edges(f[0]))+", " + str(G.edges(f[1])))
    for e in G.edges(f[0]):
      if not UF.has_edge(e[0], e[1]):
        e = edge_order(e)
        if e not in cyclic_edges:
          D.add(e)
    for e in G.edges(f[1]):
      if not UF.has_edge(e[0], e[1]):
        e = edge_order(e)
        if e not in cyclic_edges:
          D.add(e)
    D.remove(f)

  # restore data
  for n, d in UF.nodes(data=True):
    d.update(G.node[n])
  for e in UF.edges():
    UF[e[0]][e[1]].update(G[e[0]][e[1]])

  return UF


if __name__ == '__main__':
  UF = main()
  if UF:
    #print("Steiner tree nodes:",UF.nodes())
    #print("Steiner tree edges:",UF.edges())
    #draw_graph(UF)
    #nx.write_gml(G, argv[2])
    nx.write_gml(UF, "result2.gml")
