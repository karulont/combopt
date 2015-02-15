# Remove non-terminals with degree 0 (disjoint) or 1 (leaf)
def prepass(g):
  h = g.copy()
  nonterm = [n for n, d in h.nodes(data=True) if (d['T'] == 0 and h.degree(n) <= 1)]
  h.remove_nodes_from(nonterm)

  nn = g.number_of_nodes() - h.number_of_nodes()
  ne = g.number_of_edges() - h.number_of_edges()
  print("prepass: removed " + str(nn) + " nodes, " + str(ne) + " edges")

  return h
