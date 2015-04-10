from sys import argv
import math
import networkx as nx
from data import *
from gurobipy import *
import draw

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

    # wires can only be used if their endpoints are used
    for p1,p2 in wire_vars:
        m.addConstr(wire_vars[p1,p2] <= degs[p1])
        m.addConstr(wire_vars[p1,p2] <= degs[p2])

    
    #horisontaalsed jooned eraldajateks
    for x1 in range(n-1):
        x2 = x1 + 1
        col_vars = []
        for y in range(n):
            for z in range(k):
                i1 = v_id(x1,y,z)
                i2 = v_id(x2,y,z)
                if (i1, i2) in wire_vars:
                    col_vars.append(wire_vars[i1,i2])
##        p_count=0
##        for p in pairs:
##            if (p[0][0] > x1 and p[1][0] < x2) or (p[0][0] < x2 and p[1][0] > x1):
##                p_count += 1

        p_count=0
        for p in pairs:
            center_x=(x1+ x1+1)/2
            #joone valem: x-center_x=0
            p1_side=sign(p[0][0]-center_x)
            p2_side=sign(p[1][0]-center_x)
            if p1_side!=p2_side:            
                p_count += 1
        m.addConstr(quicksum(col_vars) >= p_count)

    #vertikaalsed jooned eraldajateks
    for y1 in range(n-1):
        y2 = y1 + 1
        col_vars = []
        for x in range(n):
            for z in range(k):
                i1 = v_id(x,y1,z)
                i2 = v_id(x,y2,z)
                if (i1, i2) in wire_vars:
                    col_vars.append(wire_vars[i1,i2])
##        p_count=0
##        for p in pairs:
##            if (p[0][1] > y1 and p[1][1] < y2) or (p[0][1] < y2 and p[1][1] > y1):
##                p_count += 1
        p_count=0
        for p in pairs:
            center_y=(y1+ y1+1)/2
            #joone valem: y-center_y=0
            p1_side=sign(p[0][1]-center_y)
            p2_side=sign(p[1][1]-center_y)
            if p1_side!=p2_side:            
                p_count += 1
        print(p_count)
        m.addConstr(quicksum(col_vars) >= p_count)

    #suunaga alla diagonaalid(alumine pool)
    for x1 in range(1,n):
        diag_col_vars = []
        for z in range(k):
            v0=[x1,0]
            
            while v0[0] != 0:
                left_i1 = v_id(v0[0],v0[1],z)
                left_i2 = v_id(v0[0]-1,v0[1],z)
                if (left_i1, left_i2) in wire_vars:
                    diag_col_vars.append(wire_vars[left_i1, left_i2])

                up_i1 = v_id(v0[0]-1,v0[1],z)
                up_i2 = v_id(v0[0]-1,v0[1]+1,z)
                if (up_i1, up_i2) in wire_vars:
                    diag_col_vars.append(wire_vars[up_i1, up_i2])
                    
                v0 = [v0[0]-1,v0[1]+1]

        p_count=0
        for p in pairs:
            center_x=(x1+ x1-1)/2
            center_y=0
            tous=-1#kuna suunaga alla
            p_count += get_diag_cols_count(p[0],p[1],center_x, center_y, tous)
        m.addConstr(quicksum(diag_col_vars) >= p_count)

    #suunaga alla diagonaalid(ülemine pool)
    for y1 in range(0,n-1):
        diag_col_vars = []
        for z in range(k):
            v0=[n, y1]
            
            while v0[1] != n:
                up_i1 = v_id(v0[0],v0[1],z)
                up_i2 = v_id(v0[0],v0[1]+1,z)
                if (up_i1, up_i2) in wire_vars:
                    diag_col_vars.append(wire_vars[up_i1, up_i2])
                    
                left_i1 = v_id(v0[0],v0[1]+1,z)
                left_i2 = v_id(v0[0]-1,v0[1]+1,z)
                if (left_i1, left_i2) in wire_vars:
                    diag_col_vars.append(wire_vars[left_i1, left_i2])
                    
                v0 = [v0[0]-1,v0[1]+1]

        p_count=0
        for p in pairs:
            center_x=n
            center_y=(y1+ y1+1)/2
            tous=-1#kuna suunaga alla
            p_count += get_diag_cols_count(p[0],p[1],center_x, center_y, tous)
        m.addConstr(quicksum(diag_col_vars) >= p_count)

    #suunaga üles diagonaalid (alumine pool)
    for x1 in range(0,n-1):
        diag_col_vars = []
        for z in range(k):
            v0=[x1,0]
            
            while v0[0] != n:
                right_i1 = v_id(v0[0],v0[1],z)
                right_i2 = v_id(v0[0]+1,v0[1],z)
                if (right_i1, right_i2) in wire_vars:
                    diag_col_vars.append(wire_vars[right_i1, right_i2])

                up_i1 = v_id(v0[0]+1,v0[1],z)
                up_i2 = v_id(v0[0]+1,v0[1]+1,z)
                if (up_i1, up_i2) in wire_vars:
                    diag_col_vars.append(wire_vars[up_i1, up_i2])
                    
                v0 = [v0[0]+1,v0[1]+1]

        p_count=0
        for p in pairs:
            center_x=(x1+ x1+1)/2
            center_y=0
            tous=1#kuna suunaga üles
            p_count += get_diag_cols_count(p[0],p[1],center_x, center_y, tous)
        m.addConstr(quicksum(diag_col_vars) >= p_count)

    #suunaga üles diagonaalid (ülemine pool)
    for y1 in range(0,n-1):
        diag_col_vars = []
        for z in range(k):
            v0=[0,y1]
            
            while v0[1] != n:
                up_i1 = v_id(v0[0],v0[1],z)
                up_i2 = v_id(v0[0],v0[1]+1,z)
                if (up_i1, up_i2) in wire_vars:
                    diag_col_vars.append(wire_vars[up_i1, up_i2])
                    
                right_i1 = v_id(v0[0],v0[1]+1,z)
                right_i2 = v_id(v0[0]+1,v0[1]+1,z)
                if (right_i1, right_i2) in wire_vars:
                    diag_col_vars.append(wire_vars[right_i1, right_i2])
                
                v0 = [v0[0]+1,v0[1]+1]

        p_count=0
        for p in pairs:
            center_x=0
            center_y=(y1+ y1+1)/2
            tous=1#kuna suunaga üles
            p_count += get_diag_cols_count(p[0],p[1],center_x, center_y, tous)
        m.addConstr(quicksum(diag_col_vars) >= p_count)
        

    # Optimize model
    m._vars = wire_vars
    m._t_vars = t_vars
    m._pairs = pairs
    m._k = k
    m.params.LazyConstraints = 1
##    m.params.MIPFocus = 3
    
    return m


# centerpoint_x - punkt,
#   mida loodav joon peab läbima(kahe päris punkti vahel, et ei oleks "joone peal")
def get_diag_cols_count(p1,p2,centerpoint_x, centerpoint_y, tous):
    p1_side=get_middle_line_side(centerpoint_x, centerpoint_y, tous, p1[0],p1[1])
    p2_side=get_middle_line_side(centerpoint_x, centerpoint_y, tous, p2[0],p2[1])
    if p1_side!=p2_side:#kui pooled ei ole võrdsed, siis peab ületama, ühendades A ja A'
        return 1
    return 0

#returns -1 kui ühel pool, +1 kui teisel pool, 0 kui joone peal
def get_middle_line_side(centerpoint_x, centerpoint_y, tous, p_x, p_y):
    #ühe punkti ja tõusu valemiga; tõus alati -1 või 1, p=(centerpoint_x,centerpoint_y)
    return sign(p_y - centerpoint_y - tous*(p_x-centerpoint_x))

#tagastab numbri märgi (-1,0,1)
def sign(nr):
    if nr>0:
        return 1
    elif nr<0:
        return -1
    return 0

filename1 = argv[1] if len(argv) > 1 else "switchboard-0048-006.vlsi"
filename2 = argv[2] if len(argv) == 3 else "switchboard-0048-006-sol2.vlsi"

print("Reading data from:", filename1)
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
draw.draw(n,s)
