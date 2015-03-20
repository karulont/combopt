import sys
import math
from data import *
from gurobipy import *


# Callback - use lazy constraints to eliminate sub-tours

def subtourelim(model, where):
    if where == GRB.callback.MIPSOL:
        selected = []
        # make a list of edges selected in the solution
        for i in range(n):
            sol = model.cbGetSolution([model._vars[i,j] for j in range(n)])
            selected += [(i,j) for j in range(n) if sol[j] > 0.5]
        # find the shortest cycle in the selected edge list
        tour = subtour(selected)
        if len(tour) < n:
            # add a subtour elimination constraint
            expr = 0
            for i in range(len(tour)):
                for j in range(i+1, len(tour)):
                    expr += model._vars[tour[i], tour[j]]
            model.cbLazy(expr <= len(tour)-1)


# Given a list of edges, finds the shortest subtour

def subtour(edges):
    visited = [False]*n
    cycles = []
    lengths = []
    selected = [[] for i in range(n)]
    for x,y in edges:
        selected[x].append(y)
    while True:
        current = visited.index(False)
        thiscycle = [current]
        while True:
            visited[current] = True
            neighbors = [x for x in selected[current] if not visited[x]]
            if len(neighbors) == 0:
                break
            current = neighbors[0]
            thiscycle.append(current)
        cycles.append(thiscycle)
        lengths.append(len(thiscycle))
        if sum(lengths) == n:
            break
    return cycles[lengths.index(min(lengths))]


# Read data
(n,pairs) = read_instance_from_file("switchboard-0016-002.vlsi")

terminals = []
for t1,t2 in pairs:
    terminals.append(tuple(t1))
    terminals.append(tuple(t2))
nt = len(terminals)

#n=2
k=2


# Create vertices
points = []
for x in range(n):
    for y in range(n):
        for z in range(k):
            points.append((x,y,z))
np = len(points)

m = Model()

# Create variables
vars = {}

# Add wires between nodes
for i in range(np):
    for j in range(i + 1):
        pi = points[i]
        pj = points[j]
        cost = legal_wire_cost(pi[0], pi[1], pi[2], pj[0], pj[1], pj[2], n, k)
        if cost is None:
            continue
        #print(str(pi) + " " + str(pj) + " c=" + str(cost))
        vars[i,j] = m.addVar(obj=cost, vtype=GRB.BINARY,
                             name='e'+str(i)+'_'+str(j))
        vars[j,i] = vars[i,j]

# Add wires between the terminal node and the k nodes that it might connect to
t_vars = {}
for t in range(nt):
    for z in range(k):
        t_vars[t,z] = m.addVar(obj=10, vtype=GRB.BINARY,
                                 name='t'+str(t)+'_'+str(z))
        #t_vars[z,t] = t_vars[t,z]
        #print('t'+str(t)+'_'+str(z))

m.update()


# Add degree-1 constraint for terminals
for t in range(nt):
    m.addConstr(quicksum(t_vars[t,z] for z in range(k)) == 1)


# Add degree 0 or 2 constraint
for i in range(np):
    vars_ij = []
    for j in range(np):
        if (i,j) in vars:
            vars_ij.append(vars[i,j])
    point_i = points[i]
    #print((point_i[0], point_i[1]))
    if (point_i[0], point_i[1]) in terminals:
        print(t_vars)
    
    m.addConstr(quicksum(vars_ij) * 0.5, GRB.LESS_EQUAL, 1)

m.update()


# Optimize model

m._vars = vars
m.params.LazyConstraints = 1
#m.optimize(subtourelim)
m.optimize()

solution = m.getAttr('x', t_vars)
print(solution)
for v in t_vars:
    if solution[v] > 0.5:
        print(v)
#selected = [(i,j) for i in range(n) for j in range(n) if solution[i,j] > 0.5]
#assert len(subtour(selected)) == n

print('')
#print('Optimal tour: %s' % str(subtour(selected)))
print('Optimal cost: %g' % m.objVal)
print('')
