import networkx as nx
from sys import argv

def main():
  # G = nx.read_gml(argv[1])
  G = nx.read_gml("steiner-small.gml")
	
  T = [] # terminals
  for v,d in G.nodes_iter(data=True):
    if d['T'] == 1:
      T.append(v)

  U = T[:] # Steiner tree vertices
  F = [] # Steiner tree edges

  D = [] # candidate edge set

  for u in T:
    u_incident = G.edges(u)
    for i in u_incident:
      D.append(i)

  UF = nx.Graph()
  UF.add_nodes_from(T)

  while not nx.is_connected(UF):
    if len(D) == 0:
      print("Not sufficiently connected")
      return None

    min_f = float("inf")
    for f_i in D:
      f_cost = G.edge[f_i[0]][f_i[1]]['c']
      if f_cost < min_f:
        min_f = f_cost
        f = f_i

    UF_f = UF.copy()
    UF_f.add_edge(f[0], f[1])
    if nx.has_no_cycles(UF_f):
      pass
      #F.append(f)
      #U.append(f[0])
      #U.append(f[1])

    #D.append(f.incident)
    #D.remove(f)

  return UF
  

if __name__ == '__main__':
  UF = main()
  print("UF nodes:",UF.nodes())
  print("UF edges:",UF.edges())
