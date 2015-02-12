from heapq import *
from sys import argv

import networkx as nx


def main():
  print('Reading graph...')
  G = nx.read_gml(argv[1])
  print('Graph contains', G.number_of_nodes(), 'nodes and', G.number_of_edges(), 'edges')

  # Terminal nodes
  terms = [n for n, d in G.nodes(data=True) if d['T']]

  # Component count, the goal is to reduce this to 1
  comp_count = len(terms)

  # Min-heaps that store the outgoing (unvisited) edges for each component ordered by cost
  heaps = {}

  for t in terms:
    e = min(G.edges(t, data=True), key=lambda e: e[2]['c'])
    heaps[t] = [(e[2]['c'], e[1], e[0])]

  for n, t in G.nodes_iter(data=True):
    t['c'] = None

  node_data = [d for n, d in G.nodes(data=True)]

  for t in terms:
    node_data[t]['c'] = {'val': t}

  S = nx.Graph()

  while comp_count != 1:
    for t in terms:
      if not heaps[t]:
        continue

      cur_comp = node_data[t]['c']

      cost, v, u = heappop(heaps[t])
      comp = node_data[v]['c']
      while comp is not None and comp['val'] == cur_comp['val'] and heaps[t]:
        cost, v, u = heappop(heaps[t])
        comp = node_data[v]['c']

      if comp is None:
        for v1, v2, d in G.edges(v, data=True):
          heappush(heaps[t], (d['c'], v2, v1))
        node_data[v]['c'] = cur_comp

      elif comp['val'] != cur_comp['val']:
        h1 = heaps[t]
        h2 = heaps[comp['val']]
        hm = h1 + h2
        heapify(hm)
        heaps[t] = hm
        heaps[comp['val']] = hm
        comp['val'] = cur_comp['val']
        comp_count -= 1

      else:  # comp['val'] == cur_comp['val']
        continue

      S.add_edge(u, v, {'c': cost})

  print('Solution:', S.edges())
  print('Total cost:', sum([d['c'] for u, v, d in S.edges(data=True)]))


if __name__ == '__main__':
  main()
