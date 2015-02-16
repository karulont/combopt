import matplotlib.pyplot as plt

__all__ = ['is_cyclic', 'edge_order', 'draw_graph']

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
