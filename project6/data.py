#/usr/bin/python3
import json
import random
from math import log


def check_data(m,n,P):
    assert len(P) == m, "read_instance_from_file(): matrix has wrong numo row"
    for x in range(m):
        assert len(P[x]) == n, "read_instance_from_file(): a matrix row has wrong numo entries"
        for y in range(n):
            assert 0 <= P[x][y] <= 1, "read_instance_from_file(): a matrix entry is not a probability"

####################################################################################################
# I/O

def write_instance_to_file(fn,P):
    with open(fn, 'w') as f:
        json.dump( (len(P),len(P[0]),P) ,  f)

def read_instance_from_file(fn):
    with open(fn, 'r') as f:
        (m,n,P) = json.load(f)

    if __debug__:
        check_data(m,n,P)

    return P

####################################################################################################
# cost computation

def deficiency(m,n,P,F, k, a,b):
    # It's an n by n pixel image
    # P[x][y] is the foreground probability of pixel (x,y)
    # F[x][y]==1 if pixel (x,y) belonges to the foreground, ==0 otherwise
    p = 1 # probability that we got the forground right
    for x in range(m):
        for y in range(n):
            if F[x][y]==1:
                p *= P[x][y]
            else:
                p *= 1-P[x][y]
    c = 0 # cost
    for x in range(m):
        for y in range(n):
            if F[x][y]==1:
                for x_ in range( max(0,x-k), min(m,x+k+1) ):
                    for y_ in range( max(0,y-k), min(n,y+k+1) ):
                        if F[x_][y_] == 0:
                            d2 = (x_-x)**2 + (y_-y)**2
                            c += k/d2
    print('p', p, 'c', c)
    apart = a*c
    bpart = b * (log(1/p) if p > 0 else 1e309)
    print("apart",apart,"bpart",bpart)
    return apart + bpart

####################################################################################################

def prb_from_rgb(r,g,b):
    return r / (r+g+b)

def rnd_instance(n):
    P = [ [] for x in range(m) ]
    for x in range(m):
        for y in range(n):
            (r,g,b) = (random.randint(0,255),random.randint(0,63),random.randint(0,63))
            p = prb_from_rgb(r,g,b)
            P[x].append( p )

    return P

####################################################################################################
# For debugging

def rnd_solution(n):
    F = []
    for x in range(m):
        F.append( [ random.randint(0,1)   for y in range(n) ] )

    return F

def check_rnd_solution(n):
    for i in range(10):
        P = rnd_instance(n)
        write_instance_to_file("test-{}.img".format(i),P)
        Q = read_instance_from_file("test-{}.img".format(i))
        assert P==Q, "Oops, saving and loading changed the instance"
        k = random.randint(1,10)
        a = random.randint(1,10)
        b = random.randint(1,10)
        defi = 1.e99
        while defi > 1.e30:
            F = rnd_solution(n)
            defi = deficiency(m,n,P,F, k, a,b)
            print("defi={}".format(defi))
        print("OK")
