from sys import argv
import math
import json
from munkres import Munkres

def dist(u, v):
  d = 0
  for i in range(0, len(u)):
    d += (u[i] - v[i]) ** 2
  return math.sqrt(d)

def best_assignment(snap1, snap2):
  m = Munkres()

  costs = []
  for u in snap1:
    c = []
    for v in snap2:
      c.append(dist(u, v))
    costs.append(c)

  indexes = m.compute(costs)
  perm = {}
  for i, j in indexes:
    perm[snap1[i]] = snap2[j]

  return perm

def solve(snapshots):
  print('Solving')
  n = len(snapshots)


  perms = []
  for i in range(0, n - 1):
    perm = best_assignment(snapshots[i], snapshots[i + 1])
    perms.append(perm)

    #print('Connections between snapshots', i, 'and', i + 1)
    #print(perm)
    print('Distance sum:', sum([dist(u, v) for u, v in perm.items()]))

  last_perm = [i for i in range(len(snapshots[0]))]
  newperms=[n]
  for i,perm in enumerate(perms):
    newperm = [0] * len(snapshots[0])
    for v1,v2 in perm.items():
      v1i=snapshots[i].index(v1)
      v2i=snapshots[i+1].index(v2)
      newperm[v2i] = last_perm[v1i]
    newperms+=[newperm]
  # import drawful
  # drawful.drawWithIndices(snapshots, newperms[1], newperms[2])
  return newperms

def read_instance_from_file(file):
  print('Reading input from', file)
  with open(file) as f:
    n, snapshots = json.load(f)
    #snapshots.sort(key = lambda ss: ss[0])
    return [[tuple(u) for u in ss[1]] for ss in snapshots]



def write_output(file, solution):
  with open(file, 'w') as f:
    json.dump(solution, f)
  print('Saved solution to', file)

def read_output(file):
  print('Reading output from', file)
  with open(file) as f:
    n,pi0, pi1, pi2 = json.load(f)
    #snapshots.sort(key = lambda ss: ss[0])
    return [n, pi1, pi2]

def main():
  input_file = argv[1] if len(argv) >= 2 else 'points-00125-0.lst'
  snapshots = read_instance_from_file(input_file)
  solution = solve(snapshots)
  if solution:
    output_file = argv[2] if len(argv) >= 3 else input_file + '.sol'
    write_output(output_file, solution)


if __name__ == '__main__':
  main()
