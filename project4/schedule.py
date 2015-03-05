import json
from data import read_instance_from_file
from gurobipy import *
from sys import argv

print("Reading file...")
inst = read_instance_from_file(argv[1] if len(argv) > 1 else "rnd-6000.sch")
costs = inst[0]
precedence = inst[1]

n = len(costs)
print("Number of tasks: " + str(n))

m = Model('schedule')

# Start time variables
start = {}
for i in range(0,n):
    start[i] = m.addVar(obj=1, name='start_%s' % i)
m.update()

# Precedence constraints
for p in precedence:
    i1 = p[0]
    i2 = p[1]
    m.addConstr(start[i1] + costs[i1], GRB.LESS_EQUAL, start[i2],
        'cap_%s_%s' % (i1,i2))

m.optimize()

# Print solution
if m.status == GRB.status.OPTIMAL:
    solution = m.getAttr('x', start)
    s = []
    max_endtime = -1
    for i in range(n):
        s.append(solution[i])
        if solution[i] + costs[i] > max_endtime:
            max_endtime = solution[i] + costs[i]
    print('max: %s' % max_endtime)
    with open(argv[2] if len(argv) == 3 else "rnd-6000.sol", 'w') as f:
        json.dump(s,f)
else:
    print("No solution")

