import sys
import math
from data import *
from gurobipy import *

# data.legal_wire_cost doesn't return None for some illegal wires.
# Use is_legal_wire first.
def is_legal_wire(x,y,z, x_,y_,z_, n,k):
    if z<0 or z>=k or z_<0 or z_>=k:
        return False
    if x<0 or x>=n or x_<0 or x_>=n or y<0 or y>=n or y_<0 or y_>=n:
        return False

    if x==x_ and y==y_ and abs(z-z_)==1:
        return True
    if x==x_ and abs(y-y_)==1 and z==z_ and z%2==1:
        return True
    if abs(x-x_)==1 and y==y_ and z==z_ and z%2==0:
        return True
    return False


# Read data
(n,pairs) = read_instance_from_file("switchboard-0016-002.vlsi")

terminals = []
for t1,t2 in pairs:
    terminals.append(tuple(t1))
    terminals.append(tuple(t2))
nt = len(terminals)

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
degs = {}

# Add wires between nodes
for i in range(np):
    degs[i] = m.addVar(vtype=GRB.BINARY)
    for j in range(i+1):
        x1,y1,z1 = points[i]
        x2,y2,z2 = points[j]
        if not is_legal_wire(x1,y1,z1, x2,y2,z2, n,k):
            continue
        cost = legal_wire_cost(x1,y1,z1, x2,y2,z2, n,k)
        vars[i,j] = m.addVar(obj=cost, vtype=GRB.BINARY,
                             name='e'+str(i)+'_'+str(j))
        vars[j,i] = vars[i,j]

# Add diagonal wires between the terminal node and the k nodes that it might connect to
t_vars = {}
for x,y in terminals:
    for z in range(k):
        t_vars[x,y,z] = m.addVar(obj=10, vtype=GRB.BINARY,
                                 name='t'+str(x)+'_'+str(y)+'_'+str(z))

m.update()

# Add degree-1 constraint for terminals
for x,y in terminals:
    m.addConstr(quicksum(t_vars[x,y,z] for z in range(k)) == 1)


# Add degree 0 or 2 constraint
for i in range(np):
    vars_ij = []
    for j in range(np):
        if (i,j) in vars:
            vars_ij.append(vars[i,j])

    if points[i] in t_vars:
        vars_ij.append(t_vars[points[i]])

    m.addConstr(quicksum(vars_ij) * 0.5, GRB.EQUAL, degs[i])


# Optimize model
m.optimize()


solution = m.getAttr('x', vars)
for v in vars:
    if solution[v] > 0.5:
        print(str(points[v[0]]) + ' ' + str(points[v[1]]) + ' ' + str(solution[v]))

t_solution = m.getAttr('x', t_vars)
for v in t_vars:
    if t_solution[v] > 0.5:
        print('t: ' + str(v) + ' ' + str(t_solution[v]))

print('')
print('Optimal cost: %g' % m.objVal)
print('')

# Write solution
s = []
for t1,t2 in pairs:
    route = []
    route.append(t1)
    for z in range(k):
        if t_solution[(t1[0],t1[1],z)] > 0.5:
            t1v = v
            break
    route.append(t1v)
    # TODO - backtrack route
    route.append(t2)
    s.append(route)

with open("switchboard-0016-002-sol2.vlsi", 'w') as f:
    json.dump( (n,s) ,  f)

check_solution("switchboard-0016-002.vlsi", "switchboard-0016-002-sol2.vlsi")
