from data import *
from math import log
from gurobipy import *
import networkx as nx
import my_display
import sys

def zeroFix(a):
    if a < 1.e-307:
        return (1.e+31)
    else:
        return (1/a)

def find_foreground(m,n,P,k,a,b):
    mo = Model("model")

    print ("k", k, "a", a, "b", b)

    node_vars = {}
    edge_vars = {}
    s_vars = {}
    t_vars = {}
    for x in range(m):
        for y in range(n):
            node_vars[x,y] = mo.addVar(obj = 0, name = str((x,y)))

    print("Creating graph...")
    print("Adding v-v edges...")
    for x in range(m):
        for y in range(n):
            for x_ in range( max(0,x-k), min(m,x+k+1) ):
                x2 = (x_-x)**2
                for y_ in range(max(0,y-k), min(n,y+k+1)):
                    y2 = (y_-y)**2
                    d2 = x2 + y2
                    if d2 == 0:
                        continue
                    cost = a * (k/d2)
                    if ((x,y),(x_,y_)) in edge_vars:
                        print("Alert!")
                    edge_vars[(x,y),(x_,y_)] = mo.addVar(obj=cost)
                    print(((x,y),(x_,y_)), cost)

    print("Adding s-v and v-t edges...")
    for x in range(m):
        for y in range(n):
            c1 = log(zeroFix(1-P[x][y])) * b
            c2 = log(zeroFix(P[x][y])) * b
            edge_vars['s',(x,y)] = mo.addVar(obj=c1)
            print(('s',(x,y)), c1)
            edge_vars[(x,y),'t'] = mo.addVar(obj=c2)
            print(((x,y),'t'), c2)

    mo.update()

    print("Adding constraints...")
    for (p,q) in edge_vars:
        print(p,q)
        summ = []
        summ.append(edge_vars[p,q])
        if p != 's' and p != 't':
            summ.append(node_vars[p])
        if q != 's' and q != 't':
            summ.append(-node_vars[q])
        coef = 0
        if p != 's':
            coef -= 1
        if q != 's':
            coef += 1
        print(summ, coef)
        mo.addConstr(quicksum(summ) >= coef)

    print("Finding minimum cut...")
    mo.modelSense = GRB.MINIMIZE
    mo.optimize()

    reachable = []
    for var, x in mo.getAttr('x', edge_vars).items():
        if x == 1:
            print(var)
    for var, x in mo.getAttr('x', node_vars).items():
        if x == 1:
            reachable.append(var)

    #print("Non-reachable:", str(non_reachable))
    #print("Reachable:", str(reachable))
    print("Reachable:", str(len(reachable)))

    F=[[1 if (x,y) in reachable else 0
        for y in range(n)] for x in range(m)]
    return F

def find_foreground_by_probability(m,n,P):
    F = [[1 if P[x][y] > 0.5 else 0
        for y in range(n)] for x in range(m)]
    return F

def main():
    filename = "v2_test-00.img"
    if len(sys.argv) == 2:
        filename = sys.argv[1]

    print("Reading", filename)
    P = read_instance_from_file(filename)
    m = len(P)
    n = len(P[0])
    print("m:", str(m))
    print("n:", str(n))

    k = 2
    a = 0
    b = 20

    F = find_foreground(m,n,P,k,a,b)
    #F = find_foreground_by_probability(m,n,P)

    df = deficiency(m,n,P,F,k,a,b)
    print("Deficiency:", str(df))

    #display=my_display.MyDisplay()
    #display.save_to_file=True

    #display.add_tab(P,"_P_")
    #display.add_tab(F,"_F_")
    #display.show()

if __name__ == '__main__':
    main()
