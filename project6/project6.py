from data import *
import networkx as nx

def find_foreground(m,n,P,k,a,b):
    g = nx.DiGraph()

    for x in range(m):
        for y in range(m):
            for x_ in range( max(0,x-k), min(m,x+k+1) ):
                for y_ in range(max(0,y-k), min(n,y+k+1)):
                    d2 = (x_-x)**2 + (y_-y)**2
                    if d2 == 0:
                        continue
                    c = k/d2
                    g.add_edge((x,y), (x_,y_), capacity=c)
                    g.add_edge((x_,y_), (x,y), capacity=c)

    g.add_node("s")
    g.add_node("t")

    for x in range(m):
        for y in range(m):
            g.add_edge("s", (x,y), capacity=P[x][y] * b)
            g.add_edge((x,y), "t", capacity=P[x][y] * b)

    (value,partition) = nx.minimum_cut(g,"s","t")
    reachable, non_reachable = partition
    #print("Non-reachable: " + str(non_reachable))
    #print("Reachable: " + str(reachable))

    F=[[0 for i in range(m)] for j in range(n)]

    for x in range(m):
        for y in range(m):
            if (x,y) in reachable:
                F[x][y] = 1

    return F

P = read_instance_from_file("v2_test-00.img")
m = len(P)
n = len(P[0])
print("m: " + str(m))
print("n: " + str(n))

k = 2
a = 1
b = 1

F = find_foreground(m,n,P,k,a,b)

df = deficiency(m,n,P,F,k,a,b)
print("Deficiency: " + str(df))
