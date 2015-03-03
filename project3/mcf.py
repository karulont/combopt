import networkx as nx
import matplotlib.pyplot as plt
from gurobipy import *
from read_mcf import read_mcf_nx
from sys import argv

def draw_graph(g):
    pos=nx.circular_layout(g)
    nx.draw_networkx(g, pos=pos, with_labels = True)
    nx.draw_networkx_edge_labels(g, pos=pos)
    plt.draw()
    plt.show()

print("Reading file...")
g = read_mcf_nx(argv[1] if len(argv) > 1 else "mcf-00010-flow-2")
d = int(argv[2]) if len(argv) == 3 else 2
#draw_graph(g)

m = Model('min_cost_flow')

flow = {}
for v1,v2,data in g.edges_iter(data=True):
    flow[v1,v2] = m.addVar(ub=data['u'], obj=data['c'],
                           name='flow_%s_%s' % (v1,v2))
m.update()

# Capacity constraints
for v1,v2,data in g.edges_iter(data=True):
    m.addConstr(flow[v1,v2], GRB.LESS_EQUAL, data['u'],
                'cap_%s_%s' % (v1,v2))

# Required flow
m.addConstr(
    quicksum(flow[s,u] for s,u in g.out_edges_iter(0)) -
    quicksum(flow[w,s] for w,s in g.in_edges_iter(0)) == d)

# Flow conservation
for v in g.nodes_iter():
    if v == 0 or v == 1:
        continue
    m.addConstr(
      quicksum(flow[w,v] for w,v in g.in_edges_iter(v)) ==
      quicksum(flow[v,u] for v,u in g.out_edges_iter(v)),
               'node_%s' % v)

m.optimize()

# Print solution
if m.status == GRB.status.OPTIMAL:
    solution = m.getAttr('x', flow)
    for v1,v2 in g.edges_iter():
        if solution[v1,v2] > 0:
            print('%s -> %s: %g' % (v1, v2, solution[v1,v2]))
else:
    print("No solution")
