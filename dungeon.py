import json
from rwutility import *
import random

# cell bits

NOTHING     = 0x00000000

BLOCKED     = 0x00000001
ROOM        = 0x00000002
CORRIDOR    = 0x00000004

PERIMETER   = 0x00000010
ENTRANCE    = 0x00000020
DELTA       = 0x00000040
ROOM_ID     = 0x0000FFC0

ARCH        = 0x00010000
DOOR        = 0x00020000
LOCKED      = 0x00040000
TRAPPED     = 0x00080000
SECRET      = 0x00100000
PORTC       = 0x00200000
STAIR_DN    = 0x00400000
STAIR_UP    = 0x00800000

LABEL       = 0xFF000000

OPENSPACE   = ROOM | CORRIDOR
DOORSPACE   = ARCH | DOOR | LOCKED | TRAPPED | SECRET | PORTC
ESPACE      = ENTRANCE | DOORSPACE | 0xFF000000
STAIRS      = STAIR_DN | STAIR_UP

BLOCK_ROOM  = BLOCKED | ROOM;
BLOCK_CORR  = BLOCKED | PERIMETER | CORRIDOR
BLOCK_DOOR  = BLOCKED | DOORSPACE


print(ROOM == ROOM & ~NOTHING)


print(ROOM == OPENSPACE & ROOM)
print(ROOM == ROOM & OPENSPACE)

print(ROOM == (ROOM | TRAPPED | LOCKED) & ROOM)
print(OPENSPACE == ROOM & OPENSPACE)

dungeon_layout = {
  'box':[[1,1,1],[1,0,1],[1,1,1]],
  'cross':[[0,1,0],[1,1,1],[0,1,0]]
}

class Proto():
    def __init__(self,x=-1,y=-1,width=-1,height=-1):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.r1 = 0
        self.r2 = 0
        self.c1 = 0
        self.c2 = 0

    def __str__(self):
        return "[x={},y={},width={},height={}]\n[c1={},c2={},r1={},r2={}]".format(self.x,self.y,self.width,self.height,self.c1,self.c2,self.r1,self.r2)

    def bounds(self):
        self.r1 = self.y*2+1
        self.c1 = self.x*2+1
        self.r2 = (self.y+self.height)*2-1
        self.c2 = (self.x+self.width)*2-1

class Dungeon():

    def __init__(self, sizeX=39, sizeY=39, roomMin=3, roomMax=9):
        # Ensure even blocks
        self.cX = int(sizeX/2)
        self.cY = int(sizeY/2)
        self.sizeX = 2*self.cX
        self.sizeY = 2*self.cY

        self.maxX = self.sizeX-1
        self.maxY = self.sizeY-1

        self.rooms = {}
        self.roombase = int((roomMin+1)/2)
        self.roomMin = roomMin
        self.roomMax = roomMax
        self.roomradix = int((roomMax-roomMin)/2)+1

        self.removedeadends= 100
        self.islands = []

        self.roomCount = 0

        self.collision = 0
        self.verticalBounds = 0
        self.horizontalBounds = 0
        self.potentials = 0

        self.initCells()
        #self.maskCells("round")
        #self.maskCells("cross")
        #self.maskCells("box")

        self.placeRooms("packed")
        #self.placeRooms("scatter")

        self.corridor_layout="Labyrinth"
        self.corridor_layout="Straight"
        #self.corridor_layout="Bent"
        self.openRooms()
        self.corridors()
        self.cleanup()

        print("Allocated rooms",self.potentials)
        print("Collisions:",self.collision)
        print("Bounds vertical",self.verticalBounds)
        print("Bounds horizontal",self.horizontalBounds)
        print("Created rooms",len(self.rooms))


    def connected(self,roomA, roomB):
        active = []
        for island in self.islands:
            if roomA in island:
                if island not in active: active.append(island)
                #if roomB not in island : island.append(roomB)
            elif roomB in island:
                if island not in active: active.append(island)
                #if roomA not in island : island.append(roomA)
            island.sort()
        if len(active) == 0:
            self.islands.append([roomA,roomB])
        elif len(active) > 1:
            joined = []
            for subset in active:
                joined += set(subset)
                self.islands.remove(subset)
            #removal of dubblets
            self.islands.append(joined)
        self.islands.sort()

    def maxX(self):
        return self.sizeX-1

    def maxY(self):
        return self.sizeY-1

    def initCells(self):
        self.cells = [[NOTHING for x in range(0,self.sizeY+1)] for x in range(0,self.sizeX+1)]

    def output(self):
            for y in range(0,self.sizeY+1):
                for x in range(0,self.sizeX+1):
                    #if cell == NOTHING: print(".",end="",flush=True)
                    if self.cells[x][y] & BLOCKED>0: print("@@",end="",flush=True)
                    elif self.cells[x][y] & ROOM>0:
                        roomid = self.cells[x][y] >> 6
                        room =  self.rooms[roomid]
                        if x == room.get("west") and y == room.get("north"):
                            k = 0
                            for island in self.islands:
                                if roomid in island:break
                                k +=1
                            #print(" {}".format(k),end="",flush=True)
                            print("  ",end="",flush=True)
                        elif x == int(room.get("west")*0.5 + .5*room.get("east")) and y == int(room.get("north")*0.5 + .5*room.get("south")):
                            print("{:2}".format(roomid),end="",flush=True)
                        else:
                            print("  ",end="",flush=True)

                    elif self.cells[x][y] == NOTHING: print("MM",end="",flush=True)
                    elif self.cells[x][y] & DOORSPACE>0: print("()",end="",flush=True)
                    elif self.cells[x][y] & ENTRANCE>0: print("//",end="",flush=True)
                    elif self.cells[x][y] & PERIMETER>0: print("MM",end="",flush=True)
                    elif self.cells[x][y] & CORRIDOR>0: print("  ",end="",flush=True)
                    else:
                        print("OO",end="",flush=True)
                print()

    def maskCells(self,layout):
        mask = dungeon_layout.get(layout)
        if mask is None:
            self.roundmask()
        else:
            for x in range(0,self.sizeX+1):
                for y in range(0,self.sizeY+1):
                    if mask[int(x * len(mask)/(self.sizeX+1))][int(y * len(mask[0])/(self.sizeY+1))] ==0:
                        self.cells[x][y] = BLOCKED

    def roundmask(self):
        cx = int(self.sizeX /2)
        cy = int(self.sizeY /2)
        aspectratio = cx/cy
        for x in range(0,self.sizeX+1):
            for y in range(0,self.sizeY+1):
                if ((cx-x)*(cx-x) + aspectratio*aspectratio*(cy-y)*(cy-y) > aspectratio*aspectratio*cy*cy ):
                    self.cells[x][y] = BLOCKED


    def placeRooms(self,layout):
        if layout == "packed":
            self.packRooms()
        else:
            self.scatterRooms()

    def packRooms(self):
        for x in range(0,self.cX):
            posX = 2*x+1
            for y in range(0,self.cY):
                posY = 2*y+1
                if ROOM & self.cells[posX][posY]>0: continue
                if ((x == 0 or y == 0) and random.randint(0,2)>0): continue
                proto = Proto(x,y)
                self.placeRoom(proto)

    def scatterRooms(self):
        numRooms = self.allocRooms()
        print("Allocated:",numRooms)
        for i in range(0,numRooms):
            self.placeRoom()
        pass

    def allocRooms(self):
        dungeonarea = self.sizeX * self.sizeY
        roomarea = self.roomMax * self.roomMax
        return int(dungeonarea/roomarea)


    def placeRoom(self,proto=None):
        self.potentials += 1
        if proto is None: proto = Proto()
        proto = self.setRoom(proto)
        proto.bounds()
        #print(proto)
        if proto.r1 < 1 or proto.r2 > self.maxY:
            #print("boundary upper lower",self.maxY)
            self.verticalBounds +=1
            return None
        if proto.c1 < 1 or proto.c2 > self.maxX:
            #print("boundary left right",self.maxX)
            self.horizontalBounds +=1
            return None
        if self.soundRoom(proto):
            roomId = self.roomCount +1
            self.roomCount = roomId
        else:
            self.collision +=1
            #print("collision")
            return None
        for row in range(proto.r1,proto.r2+1):
            for col in range(proto.c1,proto.c2+1):
                if self.cells[col][row] & ENTRANCE>0:
                    self.cells[col][row] &= ~ESPACE
                elif self.cells[col][row] & PERIMETER>0:
                    self.cells[col][row] &= ~PERIMETER
                self.cells[col][row] |= ROOM | roomId << 6

        roomData = {"id":roomId,"row":row,"col":col,"north":proto.r1,"south":proto.r2,"west":proto.c1,"east":proto.c2,"height":proto.height,"width":proto.width}
        self.rooms[roomId] = roomData
        self.islands.append([roomId])

        for row in range(proto.r1-1,proto.r2+2):
            cell = self.cells[proto.c1-1][row]
            if not cell & (ROOM | ENTRANCE) > 0:
                self.cells[proto.c1-1][row] |= PERIMETER

            cell = self.cells[proto.c2+1][row]
            if not cell & (ROOM | ENTRANCE) > 0:
                self.cells[proto.c2+1][row] |= PERIMETER

        for col in range(proto.c1-1,proto.c2+2):
            cell = self.cells[col][proto.r1-1]
            if not cell & (ROOM | ENTRANCE) > 0:
                self.cells[col][proto.r1-1] |= PERIMETER
            cell = self.cells[col][proto.r2+1]
            if not cell & (ROOM | ENTRANCE) > 0:
                self.cells[col][proto.r2+1] |= PERIMETER

        #pass

    def setRoom(self,proto):
        while proto.height < 0:
            if proto.y > 0:
                a = self.cY - self.roombase - proto.y
                if a < 0: a=0
                if a < self.roomradix:
                    r = a
                else:
                    r = self.roomradix
                proto.height = random.randint(0,r)+self.roombase
            else:
                proto.height = random.randint(0,self.roomradix)+self.roombase

        while proto.width < 0:
            if proto.x > 0:
                a = self.cX - self.roombase - proto.x
                if a < 0: a=0
                if a < self.roomradix:
                    r = a
                else:
                    r = self.roomradix
                proto.width = random.randint(0,r)+self.roombase
            else:
                proto.width = random.randint(0,self.roomradix)+self.roombase

        while proto.x < 0:
            proto.x = int(random.randint(0,self.cX-proto.width))


        while proto.y < 0:
            proto.y = int(random.randint(0,self.cY-proto.height))

        return proto


    def soundRoom(self,proto):
        for row in range(proto.r1,proto.r2+1):
            for col in range(proto.c1,proto.c2+1):
                if BLOCKED & self.cells[col][row]>0:
                    return False
                if ROOM & self.cells[col][row] >0:
                    return False
        return True

    def openRooms(self):
        for roomid in self.rooms.keys():
            room = self.rooms.get(roomid)
            self.openRoom(room)

    def openRoom(self,room):
        doorsills = self.doorSills(room)
        if len(doorsills) >0:
            openings = self.allocOpenings(room)
            for opening in range(0,openings):
                sill = random.choice(doorsills)
                doorsills.remove(sill)
                if doorsills == []: break
                if self.cells[sill.col][sill.row] & DOORSPACE>0: break

                if sill.roomid != -1:
                    self.connected(room.get("id"),sill.roomid)

                print("Adding sill {}: {}".format(sill.direction,sill.roomid))
                for passage in range(0,2):
                    col,row = sill.passage(passage)
                    self.cells[col][row] &= ~PERIMETER
                    self.cells[col][row] |= ENTRANCE
                sill.key, sill.doortype = doortype()
                exits = room.get("exits")
                if exits is None:
                    exits = [sill]
                else:
                    exits.append(sill)
                room["exits"]=exits
                self.cells[sill.col][sill.row] |= sill.key


        #print(doorsills)

    def allocOpenings(self,room):
        roomHeight = (room.get("south")-room.get("north"))/2 +1
        roomWidth = (room.get("east")-room.get("west"))/2 +1 
        base = int((roomHeight*roomWidth)**.5)
        return base + int(random.randint(0,base))
        #return 1

    def doorSills(self,room):
        sills = []
        print("Doing SILLs for room {:10}".format(room.get("id")))
        if room["north"] >= 3:
            for c in range(room["west"],room["east"],2):
                sill = self.checkSill(c,room["north"],"north")
                if sill is not None :sills.append(sill)
        if room["south"] <= self.sizeY-3:
            for c in range(room["west"],room["east"],2):
                sill = self.checkSill(c,room["south"],"south")
                if sill is not None :sills.append(sill)
        if room["west"] >= 3:
            for r in range(room["north"],room["south"],2):
                sill = self.checkSill(room["west"],r,"west")
                if sill is not None :sills.append(sill)
        if room["east"] <= self.sizeX-3:
            for r in range(room["north"],room["south"],2):
                sill = self.checkSill(room["east"],r,"east")
                if sill is not None :sills.append(sill)
        if sills == []:
            print("no available sills in room {}".format(room.get("id")))
            print(" bounds [e:{:4},n:{:4},w:{:4},s:{:4}]".format(room.get("east"),room.get("north"),room.get("west"),room.get("south")))
        return sills

    def checkSill(self, x , y , direction):
        door = DoorRec(x,y,direction)
        if door.cell(self) & PERIMETER==0:
            print("doorcell is not PERIMETER {} with key {:08b}".format(direction,door.cell(self)))
            return None
        if door.cell(self) & BLOCK_DOOR>0:
            print("doorcell is BLOCKDOOR {} with key {:08b}".format(direction,door.cell(self)))
            return None
        if door.outer(self) & BLOCKED>0:
            print("doorouter is BLOCKED {} with key {:08b}".format(direction,door.outer(self)))
            return None
        if door.outer(self) & ROOM>0:
            outid = door.outer(self) >> 6
            door.roomid = outid
            #print("room id :",door.roomid)
        return door

    def corridors(self):
        for x in range(1,self.cX):
            posX = 2*x+1
            for y in range(1,self.cY):
                posY = 2*y+1
                #print("---------- ny tunnel -------")
                if self.cells[posX][posY] & CORRIDOR ==0:
                    self.tunnel(x,y)

    def tunnel(self,col,row,lastdirection=None):
        directions = self.tunneldirections(lastdirection)
        for direction in directions:
            if self.opentunnel(col,row,direction):

                nextcol = col + dirX.get(direction)
                nextrow = row + dirY.get(direction)
                self.tunnel(nextcol,nextrow,direction)

    def tunneldirections(self,lastdirection=None):
        dirs = list(directions)
        random.shuffle(dirs)
        probability = corridor_layout.get(self.corridor_layout)
        if lastdirection is not None and probability>0:
            if probability > random.randint(0,100): dirs = [lastdirection]+dirs
        return dirs

    def opentunnel(self, col,row, direction):
        tunnelpart = self.createtunnel(col,row,direction)
        if tunnelpart is None:
            return False
        else:
            #print("gik "+direction)
            #print(tunnelpart)
            self.delvetunnel(tunnelpart)
            return True

    def createtunnel(self,col,row,direction):
        tunnelpart = {}
        #"col":int(col*2+1),"row":int(row*2+1),"nextcol":int((col+dirX(direction))*2+1),"nextrow":int((row+dirY(direction))*2+1)
        tunnelpart["col"] = int(col*2+1)
        tunnelpart["row"] = int(row*2+1)
        tunnelpart["nextcol"] = int((col+dirX.get(direction))*2+1)
        tunnelpart["nextrow"] = int((row+dirY.get(direction))*2+1)

        tunnelpart["midcol"] = int((tunnelpart.get("col")+tunnelpart.get("nextcol"))/2)
        tunnelpart["midrow"] = int((tunnelpart.get("row")+tunnelpart.get("nextrow"))/2)
        if tunnelpart.get("nextrow")<0 or tunnelpart.get("nextrow")>self.sizeY: return None
        if tunnelpart.get("nextcol")<0 or tunnelpart.get("nextcol")>self.sizeY: return None
        k=0
        x_min,x_max = order(tunnelpart.get("midcol"),tunnelpart.get("nextcol"))
        y_min,y_max = order(tunnelpart.get("midrow"),tunnelpart.get("nextrow"))
        for x in range(x_min,x_max):
            for y in range(y_min,y_max):
                k+=1
                if self.cells[x][y] & BLOCK_CORR > 0:
                    return None
        if k ==0:
            print("============tunnelpart===",k)
            print(tunnelpart)
            print(x_min,x_max)
            print(y_min,y_max)
            raise Exception("error")
            return None
        return tunnelpart

    def delvetunnel(self,tunnelpart):
        x_min,x_max = order(tunnelpart.get("col"),tunnelpart.get("nextcol"))
        y_min,y_max = order(tunnelpart.get("row"),tunnelpart.get("nextrow"))
        for x in range(x_min,x_max):
            for y in range(y_min,y_max):
                self.cells[x][y] &= ~ENTRANCE
                self.cells[x][y] |= CORRIDOR

    def cleanup(self):
        self.collapsetunnels()
        self.fixdoors()
        self.emptyblocks()


    def collapsetunnels(self):
        for x in range(0,self.cX):
            posX = 2*x+1
            for y in range(0,self.cY):
                posY = 2*y+1
                if self.cells[posX][posY] & OPENSPACE>0 and (self.removedeadends > random.randint(0,100) or self.removedeadends == 100):
                    self.collapse(posX,posY)

    def collapse(self,col,row):
        if self.cells[col][row] & OPENSPACE >0:
            for direction in close_end.keys():
                if self.checktunnel(col,row,direction):
                    for passage in close_end.get(direction).get("close"):
                        self.cells[col+passage[0]][row+passage[1]] = NOTHING
                    nextstep = close_end.get(direction).get("recurse")
                    self.collapse(col+nextstep[0],row+nextstep[1])
                    #print("CLOSED:",col,row)

    def checktunnel(self,col,row,direction):
        for wall in close_end.get(direction).get("walled"):
            if self.cells[col+wall[0]][row+wall[1]] & OPENSPACE > 0: return False
        return True

    def fixdoors(self):
        for roomid in self.rooms.keys():
            room = self.rooms.get(roomid)
            if room.get("exits") is not None:
                for exit in room.get("exits"):
                    x,y = exit.passage(1)
                    if self.cells[x][y] & OPENSPACE == 0:
                        x,y = exit.passage(0)
                        self.cells[x][y] &= ~exit.key
                        self.cells[x][y] &= ~ENTRANCE
                    #x,y = exit.passage(0)
                    #self.cells[x][y] = NOTHING

    def emptyblocks(self):
        pass


dirX = {"north":0,"south":0,"west":-1,"east":1}
dirY = {"north":-1,"south":1,"west":0,"east":0}

corridor_layout = {'Labyrinth':0,'Bent':50,'Straight':100}
directions = ['north','south','east','west']


close_end = {
  'north':{
    'walled':[[0,-1],[1,-1],[1,0],[1,1],[0,1]],
    'close':[[0,0]],
    'recurse':[-1,0],
  },
  'south':{
    'walled':[[0,-1],[-1,-1],[-1,0],[-1,1],[0,1]],
    'close':[[0,0]],
    'recurse':[1,0],
  },
  'west':{
    'walled':[[-1,0],[-1,1],[0,1],[1,1],[1,0]],
    'close':[[0,0]],
    'recurse':[0,-1],
  },
  'east':{
    'walled':[[-1,0],[-1,-1],[0,-1],[1,-1],[1,0]],
    'close':[[0,0]],
    'recurse':[0,1],
  },
};

def order (numberA, numberB):
    return min([numberA,numberB]),max([numberA,numberB])+1

def doortype():
  probability = random.randint(0,110)
  if probability < 15: return ARCH, "Archway"
  if probability < 60: return DOOR, "Unlocked door"
  if probability < 75: return LOCKED, "Locked door"
  if probability < 90: return TRAPPED, "Trapped door"
  if probability < 100: return SECRET, "Secret door"
  return PORTC, "Portcullis"


class DoorRec():

    def __init__(self,x,y,direction):
        self.col = x + dirX.get(direction)
        self.row = y + dirY.get(direction)
        self.direction = direction
        self.outX = self.col + dirX.get(direction)
        self.outY = self.row + dirY.get(direction)
        self.roomid = -1
        self.key = 0
        self.doortype = "nothing"

    def __str__(self):
        return json.dumps({"col":self.col,"row":self.row,"code":self.key,"type":self.doortype})


    def cell(self,dungeon):
        return dungeon.cells[self.col][self.row]

    def outer(self,dungeon):
        return dungeon.cells[self.outX][self.outY]

    def passage(self,idx):
        return  self.col+dirX.get(self.direction)*idx,self.row+dirY.get(self.direction)*idx


"""
    def passage(self,dungeon,idx):
        return  dungeon.cells[self.col+dirX.get(self.direction)*idx][self.row+dirY.get(self.direction)*idx]
"""


dungeon = Dungeon(sizeX=50,sizeY=50)
dungeon.output()
print(dungeon.islands)




def inspect():
    for roomid in dungeon.rooms.keys():
        room = dungeon.rooms.get(roomid)
        exits = room.get("exits")
        for exit in exits:
            print(str(exit))

    for x in range(1,10):
        uro = list(directions)
        random.shuffle(uro)
        print(uro)

    print(dungeon.roomCount)
    for room in dungeon.rooms.keys():
        print(dungeon.rooms.get(room))
    for x in range(1,10):
        print(x)
    print(dungeon.islands)
    dungeon.connected(1,2)
    dungeon.connected(1,8)
    dungeon.connected(3,4)
    dungeon.connected(5,6)
    dungeon.connected(4,7)
    print(dungeon.islands)
    dungeon.connected(2,4)
    print(dungeon.islands)


def bitlogic():
    a = 0
    print(a)

    a |= ROOM
    print(a)
    a |= 122 << 6

    print(a)

    print(a & ROOM)
    print(a & ROOM >> 6)

    print(ROOM == a & ROOM)
    print(a >> 6)

    somecell = PERIMETER | ROOM

    if BLOCK_DOOR & somecell >0:
        print("OK")
    else:
        print("Hmmm")

    bA = 0b00000001
    bB = 0b00000010
    bC = 0b00000100
    bD = 0b00001000

    bE = bA | bB
    bF = bA | bC


    print(format(bE,'08b'))
    print(format(bF,'08b'))
    print(format(bF & bE,'08b'))
