from data import *
from math import log
import networkx as nx
import my_display
import sys

def zeroFix(a):
    if a < 1.e-307:
        return (1.e+31)
    else:
        return (a)

def find_foreground(m,n,P,k,a,b):
    g = nx.DiGraph()

    print ("k", k, "a", a, "b", b)

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
                    g.add_edge((x,y), (x_,y_), capacity=cost)

    print("Adding s-v and v-t edges...")
    for x in range(m):
        for y in range(n):
            g.add_edge("s", (x,y), capacity=log(1/zeroFix(1-P[x][y])) * b)
            g.add_edge((x,y), "t", capacity=log(1/zeroFix(P[x][y])) * b)

    #print(str(g.edges(data=True)))

    print("Finding minimum cut...")
    cut_value, partition = nx.minimum_cut(g,"s","t")
    reachable, non_reachable = partition
    reachable.remove('s')
    non_reachable.remove('t')

    #print("Non-reachable:", str(non_reachable))
    #print("Reachable:", str(reachable))
    print("Non-reachable:", str(len(non_reachable)))
    print("Reachable:", str(len(reachable)))
    print("Cut value:", cut_value)

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
    a = 1
    b = 2

    F = find_foreground(m,n,P,k,a,b)
    #F = find_foreground_by_probability(m,n,P)

    df = deficiency(m,n,P,F,k,a,b)
    print("Deficiency:", str(df))

    display=my_display.MyDisplay()
    display.save_to_file=True

    display.add_tab(P,"_P_")
    display.add_tab(F,"_F_")
    display.show()

if __name__ == '__main__':
    main()
