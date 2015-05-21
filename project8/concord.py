from sys import argv, stdout
import networkx as nx
import subprocess as proc
import os

INFTY = 999999

def read_rpp(fname):
  with open(fname) as f:
    lines = [s for s in [l.strip() for l in f] if s and not s.startswith('#')]

  n, m = lines[0].split()
  print('N:', n, 'M:', m)

  edges = [(int(u), int(v)) for u, v in [p.split('-') for p in lines[2].split()]]

  costs = {e: c for e, c in zip(edges, [int(c) for c in lines[3].split()])}

  required = [e for e, r in zip(edges, [c == '1' for c in lines[4].split()]) if r]

  return edges, costs, required


def rpp_to_atsp(rpp):
  """ Converts an RPP problem into an asymmetric TSP problem.
      See section 4.10 in http://logistik.bwl.uni-mainz.de/Dateien/LM-2012-03.pdf. """
  edges, costs, required = rpp

  g = nx.Graph()
  g.add_edges_from([(u, v, {'cost': c}) for (u, v), c in costs.items()])

  atsp = []
  spaths = {}

  for u, v in required:
    lens = []
    for s, t in required:
      if u == s and v == t:
        lens.append(INFTY)
      else:
        spath = nx.shortest_path(g, v, s, 'cost')
        spath = [e if e in costs else e[::-1] for e in zip(spath[:-1], spath[1:])]
        spaths[v, s] = spath
        print('spaths[' + str(v) + ', ' + str(s) + '] = ' + str(spath))

        lens.append(costs[u, v] + sum(costs[e] for e in spath))
    atsp.append(lens)

  return atsp, spaths


def save_atsp_as_tsp(atsp, fname):
  """ Transforms an asymmetric TSP of size n into a symmetric TSP of size 2n and saves it in TSPLIB format.
      See http://en.wikipedia.org/wiki/Travelling_salesman_problem#Solving_by_conversion_to_symmetric_TSP. """
  n = len(atsp)
  with open(fname, 'wt') as f:
    f.write(
      'NAME: ' + fname + '\n'
      'TYPE: TSP\n'
      'DIMENSION: ' + str(n * 2) + '\n'
      'EDGE_WEIGHT_TYPE: EXPLICIT\n'
      'EDGE_WEIGHT_FORMAT: LOWER_DIAG_ROW\n'
      'EDGE_WEIGHT_SECTION\n')

    for i in range(n):
      f.write(' '.join([str(INFTY)] * (i + 1)) + '\n')

    for i in range(n):
      row = [str(d) for d in atsp[i]]
      row[i] = '0'
      f.write(' '.join(row + [str(INFTY)] * (i + 1)) + '\n')


def solve_atsp(atsp, name, concorde):
  # Concorde cannot solve ATSP, so we need to transform to TSP first.
  tsp_file = name + '.tsp'
  save_atsp_as_tsp(atsp, tsp_file)

  sol_file = name + '.tsp.sol'
  if os.path.exists(sol_file):
    os.remove(sol_file)

  stdout.flush()
  proc.call([concorde, '-x', '-o', sol_file, tsp_file])

  with open(sol_file) as f:
    tour = [int(s) for s in f.read().split()[1:]]

  n = len(atsp)
  if tour[1] - tour[0] != n:
    tour = (tour[1:] + tour[0:1])[::-1]

  for i, j in zip(tour[::2], tour[1::2]):
    if j - i != n:
      raise Exception('ERROR: Invalid ATSP tour produced by CONCORDE, (i, j) = ' + str((i, j)))

  return tour[::2]


def atsp_sol_to_rpp_sol(rpp, atsp_tour, spaths):
  edges, costs, required = rpp

  rpp_tour = []

  for i1, i2 in zip(atsp_tour, atsp_tour[1:] + atsp_tour[0:1]):
    e1 = required[i1]
    e2 = required[i2]
    rpp_tour.append(e1)
    rpp_tour += spaths[e1[1], e2[0]]

  #rpp_tour = [(0, 1), (1, 2), (2, 3), (2, 3), (2, 4), (4, 5), (5, 6), (6, 7), (3, 7), (3, 4), (4, 10), (9, 10), (8, 9), (8, 9), (0, 9)]
  #for e in rpp_tour:
    #print(str(e) + ': ' + str(1 if e in required else 0))

  print('RPP tour:', rpp_tour)
  print('RPP tour cost:', sum(costs[e] for e in rpp_tour))

  return [edges.index(e) for e in rpp_tour]


def main():
  fname = argv[1] if len(argv) > 1 else 'I01.grp'
  concorde = argv[2] if len(argv) > 2 else 'concorde'

  print('Reading RPP instance...')
  rpp = read_rpp(fname)
  print('Costs:', rpp[1])
  print('Required:', rpp[2])

  print('Transforming to ATSP...')
  atsp, aux = rpp_to_atsp(rpp)
  print('ATSP:')
  [print(r) for r in atsp]

  print('Solving with CONCORDE...')
  atsp_tour = solve_atsp(atsp, fname, concorde)
  print('ATSP tour:', atsp_tour)

  sol = atsp_sol_to_rpp_sol(rpp, atsp_tour, aux)

  print(sol)

if __name__ == '__main__':
  main()