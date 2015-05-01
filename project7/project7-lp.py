from gurobipy import *
from sys import argv
import json
import math
import drawful


def read_lst(fn):
    with open(fn, 'r') as f:
        (n, tp) = json.load(f)
    return (n, tp)


def write_lst(fn, lst):
    with open(fn, 'w') as f:
        json.dump(lst, f)


def distance(v1, v2):
    return math.sqrt((v2[0] - v1[0]) ** 2 + (v2[1] - v1[1]) ** 2 + (v2[2] - v1[2]) ** 2)


def distance_squared(v1, v2):
    return (v2[0] - v1[0]) ** 2 + (v2[1] - v1[1]) ** 2 + (v2[2] - v1[2]) ** 2


def get_permutation(edges, last_perm, last_frame, frame, n):
    perm = [0] * n
    for v1, v2 in edges:
        v1i = last_frame.index(list(v1))
        v2i = frame.index(list(v2))
        j = last_perm.index(v1i)
        perm[j] = v2i
    return perm


def main():
    # fn = 'data-n2-t3.json'
    # fn = 'example-points.lst'
    fn = 'points-00100-0.lst'
    if len(argv) == 2:
        fn = argv[1]
    n, frames = read_lst(fn)

    orig_frames = [[tuple(u) for u in ss[1]] for ss in frames]

    nf = len(frames) - 1
    print("n:", n)
    print("frames: t0-t" + str(nf))

    m = Model('project7')

    print("Adding variables...")
    edge_vars = [{} for i in range(nf)]
    point_edges = [{} for i in range(nf)]
    for f in range(nf):
        t1, f1 = frames[f]
        t2, f2 = frames[f + 1]
        for i in range(n):
            v1 = tuple(f1[i])
            point_edges[f][v1] = []
            for j in range(n):
                v2 = tuple(f2[j])
                cost = distance_squared(v1, v2)
                edge_vars[f][v1, v2] = m.addVar(obj=cost, vtype=GRB.BINARY)
                point_edges[f][v1].append(edge_vars[f][v1, v2])
    m.update()

    print("Adding constraints...")
    '''
    # There must be n edges from one frame to the next
    for frame in edge_vars:
        m.addConstr(quicksum(frame.values()) == n)

    # There must be one incoming edge per point in the last n-1 frames
    for f in range(nf):
        for v2 in frames[f+1][1]:
            v2 = tuple(v2)
            v2_edges = []
            for v1 in frames[f][1]:
                v1 = tuple(v1)
                v2_edges.append(edge_vars[f][v1,v2])
            m.addConstr(quicksum(v2_edges) == 1)
    '''
    # There must be one outgoing edge per point in the first n-1 frames
    for frame in point_edges:
        for edges in frame:
            m.addConstr(quicksum(frame[edges]) == 1)

    m.optimize()

    if m.status == GRB.status.OPTIMAL:
        solution = [n]
        last_perm = [i for i in range(n)]

        for f in range(nf):
            edges = m.getAttr('x', edge_vars[f]).items()
            selected = []
            for edge, value in edges:
                if value:
                    selected.append(edge)

            # Calculate cost
            cost = 0
            for v1, v2 in selected:
                cost += distance(v1, v2)
            print("cost", f, ":", cost)

            # Add frame permutation to solution
            last_perm = get_permutation(selected, last_perm, frames[f][1], frames[f + 1][1], n)
            solution.append(last_perm)
        # print(solution)
        write_lst(fn + '.sol', solution)
        drawful.drawWithIndices(orig_frames, solution[1], solution[2])


if __name__ == '__main__':
    import time

    start = time.clock()
    main()
    end = time.clock()
    print("time: {0:.3f} s".format(end - start))
