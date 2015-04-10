import json
from data import read_instance_from_file
from gurobipy import *
from sys import argv
import itertools
import networkx as nx


def solve(n, pairs, k):
  print('N:', n)
  print('Pairs:', len(pairs))
  print('Layers:', k)

  def nodes_iter():
    return itertools.product(range(n), range(n), range(k))

  def wires_iter():
    for x, y, z in nodes_iter():
      if z > 0:
        yield ((x, y, z - 1), (x, y, z))
      if z % 2 == 1 and y > 0:
        yield ((x, y - 1, z), (x, y, z))
      elif z % 2 == 0 and x > 0:
        yield ((x - 1, y, z), (x, y, z))

  def adjacent_wires_iter(node):
    x, y, z = node
    if z > 0:
      yield (x, y, z - 1), node
    if z < k - 1:
      yield node, (x, y, z + 1)
    if z % 2 == 1 and y > 0:
      yield (x, y - 1, z), node
    if z % 2 == 1 and y < n - 1:
      yield node, (x, y + 1, z)
    if z % 2 == 0 and x > 0:
      yield (x - 1, y, z), node
    if z % 2 == 0 and x < n - 1:
      yield node, (x + 1, y, z)


  m = Model('project5')
  terminals = set(sum(pairs, ()))
  term_to_pair = {t: p for p in pairs for t in p}

  print('Adding variables...')

  wire_vars = {}
  node_vars = {}
  term_vars = {}

  # wire_vars[i, p] == 1 iff wire i is part of the route that connects pair p
  for i in wires_iter():
    is_vertical = i[0][2] != i[1][2]
    cost = 10 if is_vertical else 1
    for p in pairs:
      wire_vars[i, p] = m.addVar(obj=cost, vtype=GRB.BINARY)

  # node_vars[j, p] == 1 iff node j is part of the route that connects pair p
  for j in nodes_iter():
    for p in pairs:
      node_vars[j, p] = m.addVar(obj=0, vtype=GRB.BINARY)

  # term_vars[x, y, z] == 1 iff the terminal at (x, y) is to be connected at level z
  for t in terminals:
    x, y = t
    for z in range(k):
      term_vars[x, y, z] = m.addVar(obj=10, vtype=GRB.BINARY)

  m.update()

  print('Adding constraints...')

  # every node must have either 0 or 2 adjacent selected edges
  for j in nodes_iter():
    x, y, z = j
    ws = list(adjacent_wires_iter(j))
    for p in pairs:
      vars = [wire_vars[i, p] for i in ws]
      if (x, y) in p:  # if the node is connected to a terminal, add 1 to edge count
        vars.append(term_vars[j])
      m.addConstr(quicksum(vars) == 2 * node_vars[j, p])

  # wires can only be used if their endpoints are used
  for i in wires_iter():
    for p in pairs:
      n1, n2 = i
      m.addConstr(wire_vars[i, p] <= node_vars[n1, p])
      m.addConstr(wire_vars[i, p] <= node_vars[n2, p])

  # every node must be part of either 0 or 1 routes
  for j in nodes_iter():
    m.addConstr(quicksum([node_vars[j, p] for p in pairs]) <= 1)

  # each terminal is connected at exactly 1 level
  for t in terminals:
    x, y = t
    vars = [term_vars[x, y, z] for z in range(k)]
    m.addConstr(quicksum(vars) == 1)


  def add_node_depth_constraints(visited_nodes, nodes, pair, depth):
    if depth > 70: return
    #print('depth', depth, 'nodes', len(nodes))
    next_nodes = set()
    for node in nodes:
      next_nodes.update(*adjacent_wires_iter(node))
    next_nodes.difference_update(nodes)
    next_nodes.difference_update(visited_nodes)
    vars = [node_vars[node, pair] for node in next_nodes]
    m.addConstr(quicksum(vars) >= 1)
    for node in next_nodes:
      if node[0:2] in pair: # we stop if we reach the other endpoint (the constraints do not hold beyond this point)
        return
    visited_nodes.update(nodes)
    add_node_depth_constraints(visited_nodes, next_nodes, pair, depth + 1)

  for x, y in terminals:
    nodes = {(x, y, z) for z in range(k)}
    add_node_depth_constraints(set(), nodes, term_to_pair[x, y], 0)

  print('Solving...')

  m.modelSense = GRB.MINIMIZE
  m.optimize()

  if m.status == GRB.status.OPTIMAL:
    print('\nFound solution with total cost', round(m.objVal), 'using', k, 'layers')
    if n <= 5:
      for wire, x in m.getAttr('x', wire_vars).items():
        if x > 0: print('Wire', wire, ':', x)
      for node, x in m.getAttr('x', node_vars).items():
        if x > 0: print('Node', node, ':', x)
      for term, x in m.getAttr('x', term_vars).items():
        if x > 0: print('Term', term, ':', x)
    graph = nx.Graph()
    graph.add_edges_from([wire[0] for wire, x in m.getAttr('x', wire_vars).items() if x > 0])
    graph.add_edges_from([(term[0:2], term) for term, x in m.getAttr('x', term_vars).items() if x > 0])
    routes = [nx.shortest_path(graph, *p) for p in pairs]
    return k, list(routes)

  print('\nNo solution found.')
  return None


def read_input(file):
  print('Reading input from', file)
  n, pairs = read_instance_from_file(file)
  pairs = [(tuple(p[0]), tuple(p[1])) for p in pairs]
  return n, pairs


def write_output(file, solution):
  with open(file, 'w') as f:
    json.dump(solution, f)
  print('Saved solution to', file)


def main():
  input_file = argv[1] if len(argv) >= 2 else 'switchboard-0016-002.vlsi'
  n, pairs = read_input(input_file)
  solution = solve(n, pairs, 2)
  if solution:
    output_file = argv[2] if len(argv) >= 3 else input_file + '.sol'
    write_output(output_file, solution)


if __name__ == '__main__':
  main()
