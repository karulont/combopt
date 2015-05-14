__author__ = 'Sander'


def readFile(filename):
    all_lines = []
    with open(filename) as f:
        all_lines = f.readlines()
    out = []
    for line in all_lines:
        if len(out) >= 6:
            break
        if line.startswith("#") or line.strip() == '':
            continue
        elements = line.strip().split()

        if '-' in elements[0]:  # assume that is edges
            for i in range(len(elements)):
                elements[i] = tuple(elements[i].split('-'))
                elements[i] = int(elements[i][0]), int(elements[i][1])
                # print(elements[i][0],elements[i][1])
        else:
            elements = list(map(int, elements))
        out.append(elements)
    return out


# def readFile(filename):
# out = []
# with open(filename) as f:
# for rida in f:
#             if len(out) >= 6:
#                 break
#             if rida.startswith("#") or rida.strip() == '':
#                 continue
#             elements = rida.strip().split()
#
#             if '-' in elements[0]:  # assume that is edges
#                 for i in range(len(elements)):
#                     elements[i] = tuple(elements[i].split('-'))
#                     elements[i] = int(elements[i][0]), int(elements[i][1])
#             else:
#                 elements = list(map(int, elements))
#             out.append(elements)
#     return out



if __name__ == '__main__':
    import subprocess

    res = subprocess.check_output(["concorde.exe", "newout.tsp"], universal_newlines=True)
    print(res)
    import time
    exit(0)
    name = "C://Users//Sander//Documents//combopt//project8//A3101.DAT.grp"
    t0 = time.clock()
    out = readFile(name)  # for=0.0010627081797740228; lines=0.0008131257055953125
    print(out[3])
    t1 = time.clock()
    print(out)
    # out=[]
    # out2=None
    # t0=None
    # t1=None
    # t2=None
    # with open(name) as f:
    # t0=time.clock()
    #     for rida in f:
    #         out.append(rida)
    #     t1=time.clock()
    #     # out2=f.readlines()
    #     # t2=time.clock()
    # print(t2)
