from data import *
from math import log
import networkx as nx
import my_display

def zeroFix(a):
    if a < 1.e-307:
        return (1.e+31)
    else:
        return (a)

def find_foreground(m,n,P,k,a,b):
    g = nx.DiGraph()

    print ("k", k, "a", a, "b", b)

    for x in range(m):
        for y in range(n):
            for x_ in range( max(0,x-k), min(m,x+k+1) ):
                for y_ in range(max(0,y-k), min(n,y+k+1)):
                    d2 = (x_-x)**2 + (y_-y)**2
                    if d2 == 0:
                        continue
                    c = k/d2
                    g.add_edge((x,y), (x_,y_), capacity=c*a)
                    g.add_edge((x_,y_), (x,y), capacity=c*a)

    g.add_node("s")
    g.add_node("t")

    for x in range(m):
        for y in range(n):
            g.add_edge("s", (x,y), capacity=log(1/zeroFix(P[x][y])) * b)
            g.add_edge((x,y), "t", capacity=log(1/zeroFix(1-P[x][y])) * b)

    #print(str(g.edges(data=True)))

    (value,partition) = nx.minimum_cut(g,"s","t")
    reachable, non_reachable = partition
    print("Non-reachable: " + str(non_reachable))
    print("Reachable: " + str(reachable))
    print("Cut value: ", value)

    F=[[0 for i in range(n)] for j in range(m)]

    reachable.remove('s')
    for (x,y) in reachable:
        F[x][y] = 1

    return F

P = read_instance_from_file("v2_test-00.img")
m = len(P)
n = len(P[0])
print("m: " + str(m))
print("n: " + str(n))

k = 7
a = 3
b = 2

F = find_foreground(m,n,P,k,a,b)

df = deficiency(m,n,P,F,k,a,b)
print("Deficiency: " + str(df))

display=my_display.MyDisplay()
display.save_to_file=True

display.add_tab(P,"_P_")
display.add_tab(F,"_F_")
display.show()
