from heapq import *
from gml_read import read_gml2
from sys import argv
from UnionFind import UnionFind

import networkx as nx


def main():
  print('Reading graph...')
  G = read_gml2(argv[1])
  print('Graph contains', G.number_of_nodes(), 'nodes and', G.number_of_edges(), 'edges')

  # Terminal nodes
  terms = [n for n, d in G.nodes(data=True) if d['T']]
  print('Number of terms:', len(terms))

  # Component count, the goal is to reduce this to 1
  comp_count = len(terms)

  # Min-heaps that store the outgoing (unvisited) edges for each component ordered by cost
  heaps = {}

  for t in terms:
    e = min(G.edges(t, data=True), key=lambda e: e[2]['c'])
    heaps[t] = [(e[2]['c'], e[1], e[0])]

  S = nx.Graph()
  
  term_sets = set()
  uf = UnionFind()
  for t in terms:
    term_sets.add(uf[t])

  while comp_count != 1:
    for t in terms:
      if not heaps[t]:
        continue

      cur_comp = uf[t]
      cur_heap = heaps[cur_comp]

      cost, v, u = heappop(cur_heap)
      comp = uf[v]
      while comp == cur_comp and cur_heap:
        cost, v, u = heappop(cur_heap)
        comp = uf[v]

      if comp not in term_sets:
        for v1, v2, d in G.edges(v, data=True):
          heappush(cur_heap, (d['c'], v2, v1))
        term_sets.remove(cur_comp)
        uf.union(t, v)
        term_sets.add(uf[t])
        heaps[cur_comp] = None
        heaps[uf[t]] = cur_heap

      elif comp != cur_comp:
        h1 = cur_heap
        h2 = heaps[comp]
        hm = h1 + h2
        heapify(hm)
        heaps[comp] = None
        heaps[cur_comp] = None
        term_sets.remove(cur_comp)
        uf.union(t, v)
        term_sets.add(uf[t])
        heaps[uf[t]] = hm
        comp_count -= 1
        print('comp_count:', comp_count)

      else:  # comp['val'] == cur_comp['val']
        continue

      S.add_edge(u, v, {'c': cost})

  print('Solution:', S.edges())
  print('Total cost:', sum([d['c'] for u, v, d in S.edges(data=True)]))
  
  print('Saving graph...')
  for v, d in S.nodes_iter(data=True):
    d['orig'] = v
  nx.write_gml(S, 'solution.gml')


if __name__ == '__main__':
  main()
