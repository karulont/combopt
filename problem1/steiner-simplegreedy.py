import networkx as nx
import matplotlib.pyplot as plt
from gml_read import read_gml2
from sys import argv

# based on http://www.geeksforgeeks.org/detect-cycle-undirected-graph/
def is_cyclic(g):
  def is_cyclic_recurse(start, visited, parent):
    visited.add(start)
    for v in g[start]:
      if v not in visited:
        if is_cyclic_recurse(v, visited, start):
          return True
      elif v != parent:
        return True
    return False

  # do DFS, if we reach a visited node, then there is a cycle
  visited=set()
  for u in g:
    if u not in visited:
      if is_cyclic_recurse(u, visited, None):
        return True
  return False

# order edge vertices by id
def edge_order(e):
  if e[0] < e[1]:
    return e
  return (e[1], e[0])

def draw_graph(g):
  nx.draw_networkx(g, with_labels = True)
  plt.draw()
  plt.show()

def main():
  # G = read_gml2(argv[1])
  G = read_gml2("steiner-slides.gml")

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

    UF_f = UF.copy()
    UF_f.add_edge(f[0], f[1])
    if not is_cyclic(UF_f):
      UF = UF_f
    else:
      cyclic_edges.add(f)

    # add edges incident on f to D
    #print("add to D: "+str(G.edges(f[0]))+", " + str(G.edges(f[1])))
    for e in G.edges(f[0]):
      if not UF.has_edge(e[0], e[1]) and edge_order(e) not in cyclic_edges:
        D.add(edge_order(e))
    for e in G.edges(f[1]):
      if not UF.has_edge(e[0], e[1]) and edge_order(e) not in cyclic_edges:
        D.add(edge_order(e))
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
    nx.write_gml(UF, "result.gml")
