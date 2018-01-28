
import random


NOTHING     = 0b00000000
WALLED      = 0b00000001
LIGHT       = 0b00000010

NORTH       = 0b00000010
SOUTH       = 0b00000100
EAST        = 0b00001000
WEST        = 0b00010000

PAINTA      = 0b00100000
PAINTB      = 0b01000000
PAINTC      = 0b10000000

NOWALL_SYM  = "  "
WALL_SYM    = "MM"
LIGHT_SYM   = "@@"
class Labyrinth():

    def __init__(self,width=10,height=10):
        self.height = height
        self.width = width
        self.hwalls = [[NOTHING for y in range(0,width+1)] for x in range(0,height)]
        self.vwalls = [[NOTHING for y in range(0,width)] for x in range(0,height+1)]
        #self.outerwall()
        #self.generate(30,30,NOTHING)
        self.allwalls()
        self.backtrack()
        #self.generate(50,50,NOTHING)


    def generate(self,vwall,hwall,code):
        for wallcount in range(0,vwall):
            x = random.randint(1,len(self.vwalls)-2)
            y = random.randint(1,len(self.vwalls[0])-1)
            self.vwalls[x][y] = code
        for wallcount in range(0,hwall):
            x = random.randint(1,len(self.hwalls)-1)
            y = random.randint(1,len(self.hwalls[0])-2)
            self.hwalls[x][y] = code

    def allwalls(self):
        self.hwalls = [[WALLED for y in range(0,self.width+1)] for x in range(0,self.height)]
        self.vwalls = [[WALLED for y in range(0,self.width)] for x in range(0,self.height+1)]

    def testwall(self):
        self.hwalls[0][1] = WALLED
        self.hwalls[1][1] = WALLED
        self.hwalls[2][1] = WALLED

    def outerwall(self):
        for col in range(0,len(self.hwalls)):
            self.hwalls[col][0] |= WALLED
            self.hwalls[col][len(self.hwalls[0])-1] = WALLED
        for row in range(0,len(self.vwalls[0])):
            self.vwalls[0][row] |= WALLED
            self.vwalls[len(self.vwalls)-1][row] = WALLED

    def output(self):
        maze = [[NOWALL_SYM for x in range(0,2*self.height+1)] for y in range(0,2*self.width+1)]

        for x in range(0,self.height+1):
            for y in range(0,self.width+1):
                maze[y*2][x*2] = WALL_SYM

        for x in range(0,len(self.hwalls)):
            for y in range(0,len(self.hwalls[0])):
                if self.hwalls[x][y] == WALLED: maze[y*2][x*2+1]=WALL_SYM
                if self.hwalls[x][y] == LIGHT: maze[y*2][x*2+1]=LIGHT_SYM

        for x in range(0,len(self.vwalls)):
            for y in range(0,len(self.vwalls[0])):
                if self.vwalls[x][y] == WALLED: maze[y*2+1][x*2]=WALL_SYM
                if self.vwalls[x][y] == LIGHT: maze[y*2+1][x*2]=LIGHT_SYM

        return maze

    def code(self,x,y):
        code = NOTHING
        if self.vwalls[x+1][y] & (WALLED | LIGHT) > 0:
            code |= EAST
        if self.vwalls[x][y] & (WALLED | LIGHT) > 0:
            code |= WEST
        if self.hwalls[x][y] & (WALLED | LIGHT) > 0:
            code |= NORTH
        if self.hwalls[x][y+1] & (WALLED | LIGHT) > 0:
            code |= SOUTH
        return code

    def go(self,x,y,direction):
        return  self.code(x,y) & direction ==0


    def walling(self,x,y,direction,code):
        if direction & EAST > 0:
            self.vwalls[x+1][y] = code
        if direction & WEST> 0:
            self.vwalls[x][y] = code
        if direction & NORTH > 0:
            self.hwalls[x][y] = code
        if direction & SOUTH > 0:
            self.hwalls[x][y+1] = code

    def getNeighboors(self,x,y,painted=[]):
        neighboors = {}
        for direction in directions.keys():
            addon = directions.get(direction)
            #print(addon)
            if x + addon[0] >= 0 and x+addon[0] < self.width:
                if y + addon[1] >= 0 and y+addon[1] < self.height:
                    if (x+addon[0],y+addon[1]) not in painted:
                        neighboors[direction]=(x+addon[0],y+addon[1])
                    else:
                        pass
                        #print("PAINTED:",(x+addon[0],y+addon[1]))
                else:
                    pass
                    #print("VOUTSIDE:",(x+addon[0],y+addon[1]))
            else:
                pass
                #print("HOUTSIDE:",(x+addon[0],y+addon[1]))
        return neighboors

    def backtrack(self):
        x = random.randint(3,self.width-1)
        y = random.randint(3,self.height-1)
        visited = [(x,y)]
        path = [(x,y)]
        while len(path) >0:
            x = path[-1][0]
            y = path[-1][1]
            cells = self.getNeighboors(x,y,visited)
            #print(cells)
            #print(x,y,cells)
            if len(list(cells.keys()))>0:
                direction = random.choice(list(cells.keys()))
                self.walling(x,y,direction,NOTHING)
                x = cells.get(direction)[0]
                y = cells.get(direction)[1]
                visited.append((x,y))
                path.append((x,y))
            else:
                path = path[:-1]

directions = {
    NORTH:(0,-1),SOUTH:(0,1),EAST:(1,0),WEST:(-1,0)
}


def testinglaby():
    laby = Labyrinth()
    #laby.walling(5,5,NORTH,NOTHING)
    #laby.walling(5,5,SOUTH,NOTHING)
    #laby.walling(5,5,EAST,NOTHING)
    #laby.walling(5,5,WEST,NOTHING)
    maze = laby.output()
    for row in maze:
        for cell in row:
            print(cell,end="",flush=True)
        print()

    print("NORTH:",laby.go(1,3,NORTH))
    print("SOUTH:",laby.go(1,3,SOUTH))
    print("WEST:",laby.go(1,3,WEST))
    print("EAST:",laby.go(1,3,EAST))
