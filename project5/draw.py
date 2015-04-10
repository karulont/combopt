import turtle

OFFSET=200
MULTIPLE=10
def draw(n,paths):
    cords=[(0,0),(n,0),(n,n),(0,n),(0,0)]
    turtle.penup()
    for c in cords:
        turtle.setpos(getCoord(c[0]),getCoord(c[1]))
        turtle.pendown()
##        turtle.left(90)

    
##    turtle.penup()
##    turtle.goto(-OFFSET,-OFFSET)
##    turtle.pendown()
    prevz=-1
    for path in paths:
        turtle.penup()
        for stepi in range(1,len(path)-1):
            step=path[stepi]
            if len(step)==2:
                continue
            x,y,z=step
            turtle.pencolor(getrgb(z))
            turtle.setpos(getCoord(x),getCoord(y))
            print(stepi)
##            if stepi==1 or stepi==(len(path)-2):
            if prevz!=z or stepi==1 or stepi==(len(path)-2):
                turtle.write(str(x)+","+str(y))
            prevz=z
            turtle.setpos(getCoord(x),getCoord(y))
            turtle.pendown()
    turtle.ht()
    
        

def getCoord(x):
    return x*MULTIPLE-OFFSET

def getrgb(z):
    x=[0,0,0]
    x[z]=turtle.colormode()
    return tuple(x)

if __name__=="__main__":
        
    draw(48,[[[21, 0], (21, 0, 0), (22, 0, 0), (23, 0, 0), (24, 0, 0), (25, 0, 0), (26, 0, 0), (27, 0, 0), (28, 0, 0), (29, 0, 0), (30, 0, 0), (31, 0, 0), (32, 0, 0), (33, 0, 0), (34, 0, 0), (35, 0, 0), (36, 0, 0), (37, 0, 0), (38, 0, 0), (39, 0, 0), (40, 0, 0), (41, 0, 0), [41, 0]],
         [[34, 0], (34, 0, 1), (34, 1, 1), (34, 2, 1), (34, 3, 1), (34, 4, 1), (34, 5, 1), (34, 6, 1), (34, 7, 1), (34, 8, 1), (34, 9, 1), (34, 10, 1), (34, 11, 1), (34, 12, 1), (34, 13, 1), (34, 14, 1), (34, 15, 1), (34, 16, 1), (34, 17, 1), (34, 18, 1), (34, 19, 1), (34, 20, 1), (34, 21, 1), (34, 22, 1), (34, 23, 1), (34, 24, 1), (34, 25, 1), (34, 26, 1), (34, 27, 1), (34, 28, 1), (34, 28, 0), (35, 28, 0), (36, 28, 0), (37, 28, 0), (38, 28, 0), (39, 28, 0), (40, 28, 0), (41, 28, 0), (42, 28, 0), (43, 28, 0), (44, 28, 0), (45, 28, 0), (46, 28, 0), (47, 28, 0), [47, 28]]])
