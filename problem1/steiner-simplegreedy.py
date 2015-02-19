import heapq
import networkx as nx
from gml_read import read_gml2
from graph_util import edge_order, draw_graph
from sys import argv
from UnionFind import UnionFind

def main():
  print('Reading graph...')
  G = read_gml2(argv[1] if len(argv) > 1 else "steiner-010000.gml")
  print('Graph contains', G.number_of_nodes(), 'nodes and', G.number_of_edges(), 'edges')

  T = [n for n, d in G.nodes_iter(data=True) if d['T']] # terminals
  print('Number of terms:', len(T))

  # candidate edge set D
  D = []
  for t in T:
    for _, u, d in G.edges_iter(t, data=True):
      D.append((d['c'], u, t))
  heapq.heapify(D)

  S = nx.Graph()
  uf = UnionFind()
  comp_count = G.number_of_nodes()

  while comp_count > 1:
    if not D:
      print("Not sufficiently connected")
      return

    cost, v, u = heapq.heappop(D)

    if uf[u] == uf[v]:
      continue

    S.add_edge(u, v, {'c': cost})
    uf.union(u, v)
    comp_count -= 1

    for _, w, d in G.edges_iter(v, data=True):
      if w != u:
        heapq.heappush(D, (d['c'], w, v))

  #draw_graph(S)
  print('Total cost:', sum([d['c'] for u, v, d in S.edges_iter(data=True)]))
  print('Saving graph...')
  for v, d in S.nodes_iter(data=True):
    d['orig'] = v
  nx.write_gml(S, argv[2] if len(argv) > 2 else "solution.gml")


if __name__ == '__main__':
  main()
