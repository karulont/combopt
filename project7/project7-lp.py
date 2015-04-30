from gurobipy import *
from sys import argv
import json
import math

def read_lst(fn):
    with open(fn, 'r') as f:
        (n,tp) = json.load(f)
    return (n,tp)

def distance(v1, v2):
    return math.sqrt((v2[0]-v1[0])**2 + (v2[1]-v1[1])**2 + (v2[2]-v1[2])**2)

def distance_squared(v1, v2):
    return (v2[0]-v1[0])**2 + (v2[1]-v1[1])**2 + (v2[2]-v1[2])**2

#def get_permutation(edges):
    

def main():
    fn = 'data-n2-t3.json'
    if len(argv) == 2:
        fn = argv[1]
    n,frames = read_lst(fn)
    print("n:", n)
    print("frames: t0-t" + str(len(frames)-1))

    edge_vars = {}
    m = Model('project7')

    print("Adding variables...")
    frame_edges = {}
    point_edges = {}
    for f in range(len(frames)-1):
        t1,f1 = frames[f]
        t2,f2 = frames[f+1]
        frame_edges[f] = []
        for i in range(n):
            v1 = tuple(f1[i])
            point_edges[f,v1] = []
            for j in range(n):
                v2 = tuple(f2[j])
                cost = distance_squared(v1,v2)
                edge_vars[f,v1,v2] = m.addVar(obj=cost, vtype=GRB.BINARY)
                frame_edges[f].append(edge_vars[f,v1,v2])
                point_edges[f,v1].append(edge_vars[f,v1,v2])
    m.update()

    print("Adding constraints...")

    # There must be n edges from one frame to the next
    #for f in range(len(frames)-1):
    #    m.addConstr(quicksum(frame_edges[f]) == n)

    # There must be one outgoing edge per point in the first n-1 frames
    for edges in point_edges:
        m.addConstr(quicksum(point_edges[edges]) == 1)

    m.optimize()

    if m.status == GRB.status.OPTIMAL:
        edges = m.getAttr('x', edge_vars).items()
        cost = {}
        for edge,selected in edges:
            if selected:
                f,v1,v2 = edge
                if f in cost:
                    cost[f] += distance(v1,v2)
                else:
                    cost[f] = distance(v1,v2)
        print("cost:", cost)

        #get_permutation()

if __name__ == '__main__':
    import time
    start = time.clock()
    main()
    end = time.clock()
    print("time: {0:.3f} s".format(end - start))
