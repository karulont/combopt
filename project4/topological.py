from data import *
import json
import networkx as nx
import sys

def main():
	if (len(sys.argv) < 2):
		print('Usage:', sys.argv[0], '<input file> <output file>')
		return

	print('Reading input...')
	times, arcs = read_instance_from_file(sys.argv[1])
	n = len(times)
	print('Number of tasks:', n)
	print('Number of dependencies:', len(arcs))
	
	print('Solving...')
	print('Doing topological sort...')
	g = nx.DiGraph()
	for i in range(n):
		g.add_node(i)
	for arc in arcs:
		g.add_edge(arc[0], arc[1])
	
	order = nx.topological_sort(g)
	
	print('Assigning start times...')
	start = [0] * n
	end = 0
	for u in order:
		end = max(end, start[u] + times[u])
		for v in g.neighbors_iter(u):
			start[v] = max(start[v], start[u] + times[u])
	print('Total time to complete all tasks:', end)
	
	print('Saving solution...')
	solf = sys.argv[2] if len(sys.argv) > 2 else 'solution.sol'
	with open(solf, 'w') as f:
		json.dump(start, f)
	print('Solution saved to', solf)

if __name__ == '__main__':
	main()