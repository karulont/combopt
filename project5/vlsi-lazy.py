from sys import argv
import math
import networkx as nx
from data import *
from gurobipy import *

def get_solution_nonzero(solution, vars):
    selected = {}
    for v in vars:
        if solution[v] > 0.5:
            selected[v] = True
    return selected

def get_mip_solution_selected(m, vars):
    # must order key-value pairs for cbGetSolution
    keys = list(vars.keys())
    values = []
    for k in keys:
        values.append(vars[k])
    solution = m.cbGetSolution(values)
    selected = {}
    for i in range(len(keys)):
        if solution[i] > 0.5:
            selected[keys[i]] = values[i]
    return selected

def get_final_solution_selected(m, vars):
    solution = m.getAttr('x', vars)
    selected = []
    for v in vars:
        if solution[v] > 0.5:
            selected.append(v)
    return selected
'''
def v_id(x,y,z,n,k):
    return n*n*z + n*y + x

def get_v(i,n,k):
    (x,i) = divmod(i,5)
    (y,i) = divmod(i,5)
    (z,i) = divmod(i,k)
    return [x,y,z]
'''

tid = 0
idmap = {}
idmap_rev = {}
def v_id(x,y,z):
    global tid
    global idmap
    global idmap_rev
    if (x,y,z) in idmap:
        return idmap[x,y,z]
    idmap[x,y,z] = tid
    idmap_rev[tid] = (x,y,z)
    tid += 1
    return idmap[x,y,z]

def get_v(i):
    return idmap_rev[i]


# T(x,y) -> T(x,y,z)
def get_terminal_selected(t,k,vertices):
    for z in range(k):
        if v_id(t[0], t[1], z) in vertices:
            return v_id(t[0], t[1], z)
    print("Terminal not found!")

# Add extra constraint in case of wrong paths
def path_elim(m, where):
    if where == GRB.callback.MIPSOL:
        print("Callback")

        wire_sel = get_mip_solution_selected(m,m._vars)
        term_sel = get_mip_solution_selected(m,m._t_vars)

        g = nx.Graph()
        for e in wire_sel:
            g.add_edge(e[0], e[1])

        for t1,t2 in m._pairs:
            t1i = get_terminal_selected(t1,m._k,term_sel)
            t2i = get_terminal_selected(t2,m._k,term_sel)
            route = [t1i]
            t = t1i
            n = g.neighbors(t)
            t=n[0]
            while True:
                route.append(t)
                tn = g.neighbors(t)
                if tn[0] == route[len(route)-2]:
                    if len(tn) == 1:
                        break
                    t = tn[1]
                else:
                    t = tn[0]

            if route[-1] != t2i:
                #print("Wrong path!")
                print("eliminate path of length " + str(len(route)))
                #for r in route:
                #    print(get_v(r))
                #print(get_v(t1i), get_v(t2i))
                expr = m._t_vars[t1i]
                for i in range(len(route)-1):
                    expr += m._vars[(route[i], route[i+1])]
                expr += m._t_vars[t2i]
                m.cbLazy(expr <= len(route))
            else:
                #print("path ok")
                pass

def create_model(n,k):
    print("Creating model")
    m = Model()
    wire_vars = {}
    degs = {}
    t_vars = {}


    print("Adding wire vars")
    for x in range(n):
        for y in range(n):
            for z in range(k):
                i = v_id(x,y,z)
                degs[i] = m.addVar(vtype=GRB.BINARY)
                if z%2 == 0:
                    if x < n-1:
                        wire_vars[v_id(x+1,y,z), i] = wire_vars[i, v_id(x+1,y,z)] = m.addVar(obj=1, vtype=GRB.BINARY)
                else:
                    if y < n-1:
                        wire_vars[v_id(x,y+1,z), i] = wire_vars[i, v_id(x,y+1,z)] = m.addVar(obj=1, vtype=GRB.BINARY)
                if z < k-1:
                    wire_vars[v_id(x,y,z+1), i] = wire_vars[i, v_id(x,y,z+1)] = m.addVar(obj=10, vtype=GRB.BINARY)

    # Add diagonal wires between the terminal node and the k nodes that it might connect to
    print("Adding terminal vars")
    for x,y in terminals:
        for z in range(k):
            t_vars[v_id(x,y,z)] = m.addVar(obj=10, vtype=GRB.BINARY)

    print("Updating model")
    m.update()


    print("Adding constraints")

    # Add degree-1 constraint for terminals
    for x,y in terminals:
        m.addConstr(quicksum(t_vars[v_id(x,y,z)] for z in range(k)) == 1)


    # Add degree 0 or 2 constraint
    for x in range(n):
        for y in range(n):
            for z in range(k):
                point_edges = []
                i = v_id(x,y,z)
                if z%2 == 0:
                    if x < n-1:
                        point_edges.append(wire_vars[i, v_id(x+1,y,z)])
                    if x > 0:
                        point_edges.append(wire_vars[v_id(x-1,y,z), i])
                else:
                    if y < n-1:
                        point_edges.append(wire_vars[i, v_id(x,y+1,z)])
                    if y > 0:
                        point_edges.append(wire_vars[v_id(x,y-1,z), i])
                if z < k-1:
                    point_edges.append(wire_vars[i, v_id(x,y,z+1)])
                if z > 0:
                    point_edges.append(wire_vars[v_id(x,y,z-1), i])

                if i in t_vars:
                    point_edges.append(t_vars[i])

                m.addConstr(quicksum(point_edges) * 0.5, GRB.EQUAL, degs[i])

    #
    for p1,p2 in wire_vars:
        m.addConstr(wire_vars[p1,p2] <= degs[p1])
        m.addConstr(wire_vars[p1,p2] <= degs[p2])

    for x1 in range(n-1):
        x2 = x1 + 1
        col_vars = []
        for y in range(n):
            for z in range(k):
                i1 = v_id(x1,y,z)
                i2 = v_id(x2,y,z)
                if (i1, i2) in wire_vars:
                    col_vars.append(wire_vars[i1,i2])
        p_count=0
        for p in pairs:
            if (p[0][0] > x1 and p[1][0] < x2) or (p[0][0] < x2 and p[1][0] > x1):
                p_count += 1
        m.addConstr(quicksum(col_vars) >= p_count)

    for y1 in range(n-1):
        y2 = y1 + 1
        col_vars = []
        for x in range(n):
            for z in range(k):
                i1 = v_id(x,y1,z)
                i2 = v_id(x,y2,z)
                if (i1, i2) in wire_vars:
                    col_vars.append(wire_vars[i1,i2])
        p_count=0
        for p in pairs:
            if (p[0][1] > y1 and p[1][1] < y2) or (p[0][1] < y2 and p[1][1] > y1):
                p_count += 1
        print(p_count)
        m.addConstr(quicksum(col_vars) >= p_count)


    # Optimize model
    m._vars = wire_vars
    m._t_vars = t_vars
    m._pairs = pairs
    m._k = k
    m.params.LazyConstraints = 1
    return m


filename1 = argv[1] if len(argv) > 1 else "switchboard-0032-004.vlsi"
filename2 = argv[2] if len(argv) == 3 else "switchboard-0032-004-sol2.vlsi"

print("Reading data")
(n,pairs) = read_instance_from_file(filename1)

print("Processing...")
terminals = []
for t1,t2 in pairs:
    terminals.append(tuple(t1))
    terminals.append(tuple(t2))
nt = len(terminals)

k=2

while True:
    m = create_model(n,k)

    print("Optimizing with k = " + str(k))
    m.optimize(path_elim)

    if m.status == GRB.status.OPTIMAL:
        break

    k += 1


print('')
print('Optimal cost: %g' % m.objVal)
print('')


# Write solution
e_selected = get_final_solution_selected(m, m._vars)
t_selected = get_final_solution_selected(m, m._t_vars)

g = nx.Graph()
for e in e_selected:
    g.add_edge(e[0], e[1])

s = []
for t1,t2 in pairs:
    t1i = get_terminal_selected(t1,k,t_selected)
    t2i = get_terminal_selected(t2,k,t_selected)
    route = [t1,t1i]
    t = t1i
    tn = g.neighbors(t)
    t=tn[0]
    while True:
        route.append(t)
        tn = g.neighbors(t)
        if tn[0] == route[len(route)-2]:
            if len(tn) == 1:
                break
            t = tn[1]
        else:
            t = tn[0]
    for i in range(1,len(route)):
        route[i] = get_v(route[i])
    route.append(t2)
    print(route)
    s.append(route)

with open(filename2, 'w') as f:
    json.dump( (k,s) ,  f)

check_solution(filename1, filename2)
