import sys
import math
import networkx as nx
from data import *
from graph_util import *
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

def get_solution_nonzero(solution, vars):
    selected = {}
    for v in vars:
        if solution[v] > 0.5:
            selected[v] = True
    return selected

def get_terminal_index(t,k,points,vertices):
    for z in range(k):
        if (t[0], t[1], z) in vertices:
            ti = points.index((t[0], t[1], z))
    return ti

# Add extra constraint in case of wrong paths
def path_elim(m, where):
    if where == GRB.callback.MIPSOL:
        print("Callback")
        
        wire_keys = list(m._vars.keys())
        wire_values = []
        for key in wire_keys:
            wire_values.append(m._vars[key])
        wire_sol = m.cbGetSolution(wire_values)

        wire_sel = []
        for i in range(len(wire_keys)):
            if wire_sol[i] > 0.5:
                wire_sel.append(wire_keys[i])
        print(wire_sel)

        term_keys = list(m._t_vars.keys())
        term_values = []
        for key in term_keys:
            term_values.append(m._t_vars[key])
        term_sol = m.cbGetSolution(term_values)

        term_sel = []
        for i in range(len(term_keys)):
            if term_sol[i] > 0.5:
                term_sel.append(term_keys[i])
        print(term_sel)


        g = nx.Graph()
        for e in wire_sel:
            g.add_edge(e[0], e[1])


        for t1,t2 in m._pairs:
            t1i = get_terminal_index(t1,m._k,m._points,term_sel)
            t2i = get_terminal_index(t2,m._k,m._points,term_sel)
            route = [t1i]
            t = t1i
            n = g.neighbors(t)
            t=n[0]
            while True:
                route.append(t)
                n = g.neighbors(t)
                if n[0] == route[len(route)-2]:
                    if len(n) == 1:
                        break
                    t = n[1]
                else:
                    t = n[0]

            if route[-1] != t2i:
                print("Wrong path!")
                print(route)
                t1p = m._points[t1i]
                t2p = m._points[t2i]
                expr = m._t_vars[t1p]
                for i in range(len(route)-1):
                    expr += m._vars[(route[i], route[i+1])]
                    #print( m._vars[(route[i], route[i+1])])
                    print( m._points[route[i]], m._points[route[i+1]])
                    print(str((route[i], route[i+1])))
                expr += m._t_vars[t2p]
                print(len(route)+1)
                m.cbLazy(expr <= len(route))
                return


# Read data
print("Reading data")
(n,pairs) = read_instance_from_file("switchboard-0300-017.vlsi")

print("Processing...")
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


# Create model
print("Creating model")
m = Model()
vars = {}
degs = {}
t_vars = {}

# Add wires between nodes
print("Adding wire vars")
for i in range(np):
    print(i)
    degs[i] = m.addVar(vtype=GRB.BINARY)
    for j in range(i+1):
        x1,y1,z1 = points[i]
        x2,y2,z2 = points[j]
        if not is_legal_wire(x1,y1,z1, x2,y2,z2, n,k):
            continue
        cost = legal_wire_cost(x1,y1,z1, x2,y2,z2, n,k)
        vars[i,j] = m.addVar(obj=cost, vtype=GRB.BINARY)
                             #name='e'+str(i)+'_'+str(j))
        vars[j,i] = vars[i,j]

# Add diagonal wires between the terminal node and the k nodes that it might connect to
print("Adding terminal vars")
for x,y in terminals:
    for z in range(k):
        t_vars[x,y,z] = m.addVar(obj=10, vtype=GRB.BINARY)
                                 #name='t'+str(x)+'_'+str(y)+'_'+str(z))

print("Updating model")
m.update()


print("Adding constraint")

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
m._vars = vars
m._t_vars = t_vars
m._pairs = pairs
m._points = points
m._k = k
m.params.LazyConstraints = 1

print("Optimizing")
m.optimize(path_elim)
'''
e_selected = get_solution_nonzero(m.getAttr('x', vars), vars)
g = nx.Graph()
for e in e_selected:
    g.add_edge(e[0], e[1])

t_selected = get_solution_nonzero(m.getAttr('x', t_vars), t_vars)
for t1,t2 in pairs:
    t1i = get_terminal_index(t1,k,points,t_selected)
    t2i = get_terminal_index(t2,k,points,t_selected)
    route = [t1i]
    t = t1i
    n = g.neighbors(t)
    t=n[0]
    while True:
        route.append(t)
        n = g.neighbors(t)
        if n[0] == route[len(route)-2]:
            if len(n) == 1:
                break
            t = n[1]
        else:
            t = n[0]

    if route[-1] != t2i:
        print("Wrong path!")

    print("route " + str(route))
'''
solution = m.getAttr('x', vars)
for v in vars:
    if solution[v] > 0.5:
        #print(str(points[v[0]]) + ' ' + str(points[v[1]]) + ' ' + str(solution[v]))
        pass

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

#with open("switchboard-0016-002-sol2.vlsi", 'w') as f:
with open("switchboard-0016-002-sol2.vlsi", 'w') as f:
    json.dump( (n,s) ,  f)

#check_solution("switchboard-0016-002.vlsi", "switchboard-0016-002-sol2.vlsi")
