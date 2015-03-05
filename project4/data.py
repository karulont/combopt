#/usr/bin/python3
import json
import random
import sys

####################################################################################################

def write_instance_to_file(fn,t,p):
    with open(fn, 'w') as f:
        json.dump((t,p),f)

def read_instance_from_file(fn):
    with open(fn, 'r') as f:
        (t,p) = json.load(f)
    return (t,p)

def check_solution(instance_fn, sol_fn):
    (t,p) = read_instance_from_file(instance_fn)
    with open(sol_fn, 'r') as f:
        sol = json.load(f)

    n = len(t)
    if len(sol) != n:
        print("Something is wrong with this solution....")
    for (a,b) in p:
        if sol[a] + t[a] > sol[b]:
            print('"Solution" violates precedence constraint ({},{})'.format(a,b))

    makespan = 0.
    for i in range(n):
        makespan = max(makespan, sol[i] + t[i])

    print("Makespan={}".format(makespan))

####################################################################################################

def random_instance(n, t_min=1,t_max=100, predprob=.1):
    t = [ random.randint(t_min,t_max)  for i in range(n) ]
    jobs = [ i for i in range(n) ]
    random.shuffle(jobs)

    p = []
    for b in range(n):
        for a in range(b):
            if random.random() < predprob:
                p.append( (jobs[a],jobs[b]) )

    return (t,p)

####################################################################################################

def generate_some_random_instances():
    (t,p) = random_instance(10)
    write_instance_to_file("small.sch",t,p)
    (t,p) = random_instance(100,predprob=2./100)
    write_instance_to_file("rnd-0100.sch",t,p)
    (t,p) = random_instance(500,predprob=3./500)
    write_instance_to_file("rnd-0500.sch",t,p)
    (t,p) = random_instance(1000,predprob=5./1000)
    write_instance_to_file("rnd-1000.sch",t,p)
    (t,p) = random_instance(2000,predprob=7./2000)
    write_instance_to_file("rnd-2000.sch",t,p)
    (t,p) = random_instance(3000,predprob=6./3000)
    write_instance_to_file("rnd-3000.sch",t,p)
    (t,p) = random_instance(4000,predprob=3./4000)
    write_instance_to_file("rnd-4000.sch",t,p)
    (t,p) = random_instance(5000,predprob=1./5000)
    write_instance_to_file("rnd-5000a.sch",t,p)
    (t,p) = random_instance(5000,predprob=.01)
    write_instance_to_file("rnd-5000b.sch",t,p)
    (t,p) = random_instance(5000,predprob=.1)
    write_instance_to_file("rnd-5000c.sch",t,p)
    (t,p) = random_instance(6000,predprob=11./6000)
    write_instance_to_file("rnd-6000.sch",t,p)

if __name__ == '__main__':
    check_solution(sys.argv[1], sys.argv[2])
