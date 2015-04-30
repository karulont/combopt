import kdtree
import json
import networkx as nx
from sys import argv

def dist(u, v):
  d = 0
  for i in range(0, len(u)):
    d += (u[i] - v[i]) ** 2
    return d

def solve(snapshots):
  times = [t[0] for t in snapshots]
  snaps = [t[1] for t in snapshots]
  dt1 = times[1] - times[0]
  dt2 = times[2] - times[1]
  if dt1 <= dt2:
    dt = times[2] - times[1]
    first = snaps[0]
    second = snaps[1]
    third = snaps[2]
    perm = solveForTwo(snaps[0],snaps[1])
  else:
    dt = times[0] - times[1]
    first = snaps[1]
    second = snaps[2]
    third = snaps[0]
    perm = solveForTwo(snaps[1],snaps[2])

  tree = kdtree.create(third)

  # predict
  # TODO: vectorize
  perm2 = {}
  for k,v in perm.items():
    newpos = tuple([v[i] + dt * (v[i] - k[i]) for i in range(len(k))])
    node = tree.search_nn(newpos)[0]
    perm2[v] = node.data
    tree.remove((0,0,0), node=node)

  print(perm2)

def solveForTwo(sn1, sn2):
  g = nx.DiGraph()

  for u in sn1:
    for v in sn2:
      g.add_edge((u, '-'), (v, '+'), weight=dist(u, v), capacity=1)

  for u in sn1:
    g.node[u, '-']['demand'] = -1

  for u in sn2:
    g.node[u, '+']['demand'] = 1

  mcf = nx.min_cost_flow(g)

  perm = {}
  for u in sn1:
    flows = mcf[u, '-']
    for (v, _), f in flows.items():
      if f > 0:
        perm[u] = v
        break

  print('Connections between snapshots')
  print(perm)
  print('Distance sum:', sum([dist(u, v) for u, v in perm.items()]))

  return perm

def read_instance_from_file(file):
  print('Reading input from', file)
  with open(file) as f:
    n, snapshots = json.load(f)
    #snapshots.sort(key = lambda ss: ss[0])
    return [(ss[0],[tuple(u) for u in ss[1:]]) for ss in snapshots]


def write_output(file, solution):
  with open(file, 'w') as f:
    json.dump(solution, f)
  print('Saved solution to', file)


def main():
  input_file = argv[1] if len(argv) >= 2 else 'data-n2-t3.json'
  snapshots = read_instance_from_file(input_file)
  solution = solve(snapshots)
  if solution:
    output_file = argv[2] if len(argv) >= 3 else input_file + '.sol'
    write_output(output_file, solution)


if __name__ == '__main__':
  main()
