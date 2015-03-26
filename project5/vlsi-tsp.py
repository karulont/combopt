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
#(n,pairs) = read_instance_from_file("switchboard-0032-004.vlsi")
(n,pairs) = read_instance_from_file("switchboard-0016-002.vlsi")

print("Processing...")
terminals = []
for t1,t2 in pairs:
    terminals.append(tuple(t1))
    terminals.append(tuple(t2))
nt = len(terminals)

k=2


# Create vertices
np = n*n*k
print(np)

# Create model
print("Creating model")
m = Model()
vars = {}
degs = {}
t_vars = {}

tid = 0
idmap = {}
def v_id(x,y,z):
    global tid
    global idmap
    if (x,y,z) in idmap:
        return idmap[x,y,z]
    
    #return n*n*z + n*y + x
    idmap[x,y,z] = tid
    tid += 1
    return idmap[x,y,z]
    #return x*n*k + y*n + z
    #return tid

# Add wires between nodes
print("Adding wire vars")
for x in range(n):
    for y in range(n):
        for z in range(k):
            i = v_id(x,y,z)
            degs[i] = m.addVar(vtype=GRB.BINARY)
            if z%2 == 0:
                if x < n-1:
                    vars[i, v_id(x+1,y,z)] = m.addVar(obj=1, vtype=GRB.BINARY)
                    #vars[v_id(x+1,y,z), i] = vars[i, v_id(x+1,y,z)]
            else:
                if y < n-1:
                    vars[i, v_id(x,y+1,z)] = m.addVar(obj=1, vtype=GRB.BINARY)
                    #vars[v_id(x,y+1,z), i] = vars[i, v_id(x,y+1,z)]
            if z < k-1:
                vars[i, v_id(x,y,z+1)] = m.addVar(obj=10, vtype=GRB.BINARY)
                #vars[v_id(x,y,z+1), i] = vars[i, v_id(x,y,z+1)]

# Add diagonal wires between the terminal node and the k nodes that it might connect to
print("Adding terminal vars")
for x,y in terminals:
    for z in range(k):
        t_vars[x,y,z] = m.addVar(obj=10, vtype=GRB.BINARY)

print("Updating model")
m.update()


print("Adding constraint")

# Add degree-1 constraint for terminals
for x,y in terminals:
    m.addConstr(quicksum(t_vars[x,y,z] for z in range(k)) == 1)


# Add degree 0 or 2 constraint
for x in range(n):
    for y in range(n):
        for z in range(k):
            point_edges = []
            i = v_id(x,y,z)
            if z%2 == 0:
                if x < n-1:
                    point_edges.append(vars[i, v_id(x+1,y,z)])
                if x > 0:
                    point_edges.append(vars[v_id(x-1,y,z), i])
            else:
                if y < n-1:
                    point_edges.append(vars[i, v_id(x,y+1,z)])
                if y > 0:
                    point_edges.append(vars[v_id(x,y-1,z), i])
            if z < k-1:
                point_edges.append(vars[i, v_id(x,y,z+1)])
            if z > 0:
                point_edges.append(vars[v_id(x,y,z-1), i])

            if (x,y,z) in t_vars:
                point_edges.append(t_vars[x,y,z])

            print(str((x,y,z)) + ' ' + str(point_edges))
            m.addConstr(quicksum(point_edges) * 0.5, GRB.EQUAL, degs[i])


# Optimize model
m._vars = vars
m._t_vars = t_vars
m._pairs = pairs
#m._points = points
m._k = k
#m.params.LazyConstraints = 1

print("Optimizing")
m.optimize()
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
        print(str(v))
        print(str(solution[v]))
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
