#/usr/bin/python3
import json
import random
from sys import argv

####################################################################################################

def write_instance_to_file(fn,n,terminal_pairs):
    with open(fn, 'w') as f:
        json.dump( (n,terminal_pairs) ,  f)

def read_instance_from_file(fn):
    with open(fn, 'r') as f:
        (n,tp) = json.load(f)
    return (n,tp)

def legal_wire_cost(x,y,z, x_,y_,z_, n=-1,k=-1):
    if z<0 or z>=k or z_<0 or z_>=k:
        return None
    if x<0 or x>=n or x_<0 or x_>=n or y<0 or y>=n or y_<0 or y_>=n:
        return None
    if z==z_:
        if z%2==0:
            if y==y_ and abs(x-x_)==1:
                return 1
            return None
        else:
            if x==x_ and abs(y-y_)==1:
                return 1
            return None
    else:
        if abs(z-z_)==1:
            return 10
        return None

def check_solution(instance_fn, sol_fn):
    (n,terminal_pairs) = read_instance_from_file(instance_fn)
    with open(sol_fn, 'r') as f:
        (k,routes) = json.load(f)

    T = len(terminal_pairs)
    if T != len(routes):
        print("ERROR Something is wrong with this solution: len(terminal_pairs) != len(routes)")

    node_used = [ []   for x in range(n) ]
    for x in range(n):
        for y in range(n):
            node_used[x].append( [ False for z in range(k) ] )

    cost = 10*2*T # costs of diagonal wires + costs of layers
    for t in range(T):
        # check route for terminal pair t:
        if routes[t][0] != terminal_pairs[t][0]:
            print("ERROR Route ",t," doesn't start at first terminal in terminal pair")
        if routes[t][-1] != terminal_pairs[t][1]:
            print("ERROR Route ",t," doesn't end in second terminal in terminal pair")
        if routes[t][0][0] != routes[t][1][0]  or  routes[t][0][1] != routes[t][1][1]:
            print("ERROR Route ",t," wire ",0," isn't possible.")
        if routes[t][-1][0] != routes[t][-2][0]  or  routes[t][-1][1] != routes[t][-2][1]:
            print("ERROR Route ",t," last wire isn't possible.")

        (x,y,z) = routes[t][1]
        if node_used[x][y][z]:
            print("ERROR Route ",t," node ",1," is used by another route.")
        else:
            node_used[x][y][z] = True
        for j in range(1,len(routes[t])-2):
            (x,y,z)    = routes[t][j]
            (x_,y_,z_) = routes[t][j+1]
            if node_used[x_][y_][z_]:
                print("ERROR Route ",t," node ",j+1," is used by another route.")
            else:
                node_used[x_][y_][z_] = True
            c = legal_wire_cost(x,y,z, x_,y_,z_, n=n,k=k)
            #print(c)
            if c==None:
                print("ERROR Route ",t," wire ",j,"->",j+1," isn't legal.")
            else:
                cost += c
    #print("Number of layers: {}; wiring cost: {}; total cost (incl. layers): {}".format(k,cost+ 100* n**2 *k))
    print("Number of layers: {}; wiring cost: {}; total cost (incl. layers): {}".format(k,cost,cost))

####################################################################################################

def random_instance(n, T):
    terminal_pairs = [ [(-1,-1),(-1,-1)] for t in range(T) ]

    possible_terminal_locations = []
    for x in range(1,n):
        possible_terminal_locations.append((x,0))
    for y in range(1,n):
        possible_terminal_locations.append((0,y))
    for x in range(0,n-1):
        possible_terminal_locations.append((x,n-1))
    for y in range(0,n-1):
        possible_terminal_locations.append((n-1,y))

    tmp_tp = random.sample( possible_terminal_locations, 2*T )

    for t in range(T):
        terminal_pairs[t][0] = tmp_tp[2*t]
        terminal_pairs[t][1] = tmp_tp[2*t+1]

    return (n,terminal_pairs)

####################################################################################################

def generate_some_random_instances():
    for f in range(1,300):
        n = 20*f
        T = int( n/20+2 )
        (n,tp) = random_instance(n,T)
        fn = "switchboard-{0:0>4}-{1:0>3}.vlsi".format(n,T)
        write_instance_to_file(fn,n,tp)

if __name__ == '__main__':
  check_solution(argv[1], argv[2] if len(argv) >= 3 else argv[1] + '.sol')