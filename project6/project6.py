from data import *
import networkx as nx

def find_foreground(m,n,P,k,a,b):
    g = nx.DiGraph()

    sizeV = m*n
    bprim = b / sizeV
    aprim = a / sizeV
    print ("aprim", aprim, "bprim", bprim)

    for x in range(m):
        for y in range(n):
            for x_ in range( max(0,x-k), min(m,x+k+1) ):
                for y_ in range(max(0,y-k), min(n,y+k+1)):
                    d2 = (x_-x)**2 + (y_-y)**2
                    if d2 == 0:
                        continue
                    c = k/d2
                    print (x,y,c,c*aprim)
                    g.add_edge((x,y), (x_,y_), capacity=c*aprim)
                    g.add_edge((x_,y_), (x,y), capacity=c*aprim)

    g.add_node("s")
    g.add_node("t")

    for x in range(m):
        for y in range(n):
            g.add_edge("s", (x,y), capacity=P[x][y] * bprim)
            g.add_edge((x,y), "t", capacity=(1-P[x][y]) * bprim)

    print(str(g.edges(data=True)))

    (value,partition) = nx.minimum_cut(g,"s","t")
    reachable, non_reachable = partition
    print("Non-reachable: " + str(non_reachable))
    print("Reachable: " + str(reachable))

    F=[[0 for i in range(n)] for j in range(m)]

    reachable.remove('s')
    for (x,y) in reachable:
        F[x][y] = 1

    return F

P = read_instance_from_file("v2_test-0.img")
m = len(P)
n = len(P[0])
print("m: " + str(m))
print("n: " + str(n))

k = 2
a = 0
b = 1

F = find_foreground(m,n,P,k,a,b)

df = deficiency(m,n,P,F,k,a,b)
print("Deficiency: " + str(df))
