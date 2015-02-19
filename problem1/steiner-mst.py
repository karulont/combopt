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

  # New complete graph
  Gr = nx.Graph()

  # Add edges to Gr
  for t in terms:
      dists, paths = nx.single_source_dijkstra(G,t,weight='c')
      for r in terms:
          if r != t:
            Gr.add_edge(t, r, c=dists[r], p=paths[r])

  # Print statistics for Gr
  print('Gr contains', Gr.number_of_nodes(), 'nodes and', Gr.number_of_edges(), 'edges.')

  MST = nx.minimum_spanning_tree(Gr, weight='c')

  print('Total cost:', sum([d['c'] for u, v, d in MST.edges(data=True)]))

  # Add edges to Solution
  S = nx.Graph()
  for u,v,d in MST.edges_iter(data = True):
      p = d['p']
      for i in range(len(p)-1):
          d=G.get_edge_data(p[i],p[i+1])
          S.add_edge(p[i],p[i+1], c=d['c'])

  print('Total cost2:', sum([d['c'] for u,v,d in S.edges_iter(data = True)]))
  
  print('Saving graph...')
  for v, d in S.nodes_iter(data=True):
    d['orig'] = v
  nx.write_gml(S, 'solution.gml')


if __name__ == '__main__':
  main()
