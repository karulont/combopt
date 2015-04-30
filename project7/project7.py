from sys import argv
import json
import networkx as nx

def dist(u, v):
  d = 0
  for i in range(0, len(u)):
    d += (u[i] - v[i]) ** 2
    return d

def solve(snapshots):
  n = len(snapshots)
  g = nx.DiGraph()

  for i in range(0, n - 1):
    ss1 = snapshots[i]
    ss2 = snapshots[i + 1]

    for u in ss1:
      for v in ss2:
        g.add_edge((u, '-', i), (v, '+', i + 1), weight=dist(u, v), capacity=1)

  for i in range(1, n - 1):
    for u in snapshots[i]:
      g.add_edge((u, '+', i), (u, '-', i), weight=0, capacity=1)

  for u in snapshots[0]:
    g.node[u, '-', 0]['demand'] = -1

  for u in snapshots[n - 1]:
    g.node[u, '+', n - 1]['demand'] = 1

  mcf = nx.min_cost_flow(g)

  perms = []
  for i in range(0, n - 1):
    ss = snapshots[i]
    perm = {}
    for u in ss:
      flows = mcf[u, '-', i]
      for (v, _, _), f in flows.items():
        if f > 0:
          perm[u] = v
          break
    perms.append(perm)

    print('Connections between snapshots', i, 'and', i + 1)
    print(perm)
    print('Distance sum:', sum([dist(u, v) for u, v in perm.items()]))


  return None

def read_instance_from_file(file):
  print('Reading input from', file)
  with open(file) as f:
    n, snapshots = json.load(f)
    #snapshots.sort(key = lambda ss: ss[0])
    return [[tuple(u) for u in ss[1:]] for ss in snapshots]


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
