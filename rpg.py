from rwutility import *
import random
import time
from labyrinth import *
from journal import *

hands = {"name":"hands", "damage":1, "equip":["left","right"]}
dagger = {"name":"dagger", "damage":4, "equip":["left","right"]}
shortsword = {"name":"short sword", "damage":6, "equip":["left","right"]}
robes = {"name":"robes", "defence":1, "equip":["worn"]}
gold = {"name":"gold crowns"}
healingpotion = {"name":"healing potion [P]"}

class InventoryItem():
    def __init__(self,item,number=1):
        self.item = item
        self.number = number

class NPC():

    def __init__(self, name):
        self.name = name
        self.attack = 5
        self.defence = 2
        self.maxhitpoints = 25
        self.hitpoints = self.maxhitpoints
        self.equipped = {"right":dict(shortsword),"left":None,"worn":None}
        self.inventory = {}

    def getbonus(self,equip,bonusclass):
        item = self.equipped.get(equip)
        if item is None: return 0
        bonus = item.get(bonusclass)
        if bonus is None: return 0
        return bonus

    def defencebonus(self):
        bonus = self.defence
        bonus += self.getbonus("right","defence")
        bonus += self.getbonus("worn","defence")
        return bonus

    def attackbonus(self):
        bonus = self.attack
        bonus += self.getbonus("right","damage")
        bonus += self.getbonus("left","damage")
        return bonus

    def state(self):
        output = "Unharmed"
        if self.hitpoints/self.maxhitpoints < 1: output = "scratched"
        if self.hitpoints/self.maxhitpoints < .8: output = "wounded"
        if self.hitpoints/self.maxhitpoints < .5: output = "seriously wounded"
        if self.hitpoints/self.maxhitpoints < .5: output = "severely wounded"
        if self.hitpoints/self.maxhitpoints < .3: output = "colapsing"
        if self.hitpoints/self.maxhitpoints < .15: output = "dying"
        if self.hitpoints/self.maxhitpoints < .0: output = "dead"
        return output

    def isalive(self):
        return self.hitpoints >= 1

    def equip(self,item):
        if "right" in item["equip"]: self.equipped["right"] = item
        elif "left" in item["equip"]: self.equipped["left"] = item
        elif "worn" in item["equip"]: self.equipped["worn"] = item

    def damage(self, opponent):
        attack = self.attackbonus() - opponent.defencebonus()
        attackpower = random.randint(int(attack/2),attack)
        if attackpower == int(attack/2):
            return 0
        else:
            return attackpower

    def revive(self):
        self.hitpoints = self.maxhitpoints

    def pickup(self,item,volume=1):
        invrec = self.inventory.get(item.get("name"))
        if invrec is None:
            invrec = InventoryItem(item,volume)
            self.inventory[item.get("name")]= invrec
        else:
            invrec.number +=volume

    def getitem(self,itemname):
        return self.inventory.get(itemname)

    def dropconsume(self,itemname):
        invrec = self.inventory.get(itemname)
        if invrec is None:
            return False
        else:
            invrec.number -=1
            if invrec.number == 0:
                self.inventory.pop(itemname,None)
            return True

    def listinventory(self):
        inventories = list(self.inventory.keys())
        output = ""
        for key in inventories:
            invrec = self.inventory.get(key)
            output += key
            if invrec.number > 1:
                output += " (x{})".format(invrec.number)
            #output += sepSign(key,inventories)
            output += "\n"
        if output =="": output = "Empty"
        return output

    def moveinventory(self,external):
        for key in external.inventory:
            invrec = external.inventory.get(key)
            ownrec = self.inventory.get(key)
            if ownrec is None:
                self.inventory[key] = invrec
            else:
                ownrec.number += invrec.number

    def useInventory(self,key):
        if key == 'p' and self.dropconsume(healingpotion.get("name")):
            self.hitpoints += random.randint(3,8)
            self.hitpoints = min(self.hitpoints,self.maxhitpoints)
            return True
        return False

#print(dir(rwutility))
cls()

logwidth=70
loglines=40
panelleft=75


def attackText(damage):
    output = "light"
    if damage > 2: output = "normal"
    if damage > 4: output = "serious"
    if damage > 6: output = "severe"
    if damage > 10: output = "critical"
    if damage > 15: output = "mindblowing"
    return output

class RPGame():

    def __init__(self,player):
        self.player = player

        self.player.pickup(dict(healingpotion),1)

        self.userinput = Userinput()
        self.maze = Labyrinth()
        self.x = 0
        self.y = 0
        self.monster = 0
        self.log = Journal(2,2,logwidth,loglines)
        self.log.start()
        self.log.add("Welcome to a new adventure")
        self.doBaseScreen()

    def doCombatRound(self,enemy,action="attack"):
        self.log.add("You attack the {}".format(enemy.name))
        self.sleep(.3)
        damage = self.player.damage(enemy)
        if damage == 0:
            self.log.add("You missed!")
        else:
            enemy.hitpoints -= damage
            self.log.add("You make a {} hit.\nThe {} is {}".format(attackText(damage), enemy.name, enemy.state()))
        return enemy.isalive(),True

    def doEnemyCombat(self,enemy):
        damage = enemy.damage(self.player)
        self.log.add("The {} swings at you .. ".format(enemy.name))
        self.sleep(1)
        if damage == 0:
            self.log.add(" ... and misses!")
        else:
            self.player.hitpoints -= damage
            self.log.add(" .. and makes a {} hit.".format(attackText(damage)))
        return enemy.isalive(), self.player.isalive()

    def doCombat(self):
        import sys
        enemy = NPC("orc")
        enemy.hitpoints = random.randint(5,10)
        enemy.equip(dict(dagger))
        enemy.equip(dict(robes))
        enemy.pickup(dict(healingpotion),1)
        enemy.pickup(dict(gold),random.randint(1,10))
        enemy.attack = 3
        enemy.defence = 1

        self.log.add("An {} charges you!!\n".format(enemy.name))
        key = ''
        while enemy.isalive() and self.player.isalive():
            self.log.add("You can [A] Attack, [D] Dodge")
            self.log.add("What do you do ? ")
            key = self.userinput.get()
            if key == "a":
                enemyalive, playeralive = self.doCombatRound(enemy)
                if enemyalive:
                    self.doEnemyCombat(enemy)
                self.updateHealth()
            elif key == "d":
                if random.randint(0,10)>3:
                    self.log.add("You dodge the {}s attack".format(enemy.name))
                else:
                    if enemyalive:
                        self.doEnemyCombat(enemy)
            elif self.player.useInventory(key):
                self.log.add("Aahhhh .. You drank a potion .. ")
                self.updateHealth()
                self.updateInventory()
                if enemy.isalive():
                    self.doEnemyCombat(enemy)
            else:
                self.log.add("You cannot .. ")
        if enemy.isalive() and not self.player.isalive():
            self.log.add("You died ... Game over")
            self.log.add("Press any key to exit ...")
            key=''
            while key == '':
                key = self.userinput.get()
            cls()
            self.log.stop()
            sys.exit("Game over")
        else:
            self.log.add("The battle is over.")
            self.monster = 0
            self.player.moveinventory(enemy)
            self.updateInventory()
            self.log.add("")

    def updateInventory(self):
        locate(10,panelleft+2,"Inventory:")
        lines = wrapper(self.player.listinventory(),indent=3,width=40)
        k=0
        for line in lines:
            locate(10+k,panelleft+2,line+" "*(40-len(line)))
            k+=1

    def updateHealth(self):
        locate(8,panelleft+2,"Health:"+"*"*self.player.hitpoints+" "*(self.player.maxhitpoints-self.player.hitpoints))

    def doBaseScreen(self):
        #cls()
        locate(1,1,"+"+"-"*120+"+")
        locate(2,panelleft+2,"Player Name:"+self.player.name)
        locate(4,panelleft+2,"Attack: +"+str(self.player.attackbonus()))
        locate(6,panelleft+2,"Defence: +"+str(self.player.defencebonus()))
        self.updateHealth()
        self.updateInventory()
        #locate(9,panelleft,"+"+"-"*(80-panelleft)+"+")
        locate(loglines+2,1,"+"+"-"*120+"+")
        self.log.add("You have travelled through small cravine which ends at a dark cave entrance. \n")
        self.log.add("A foul smell strikes you as you enter the cave ...  \n")
        self.location()

    def sleep(self,timer):
        stime = time.time()
        while time.time()-stime<timer:pass

    def location(self):
        self.playerChoice()

    def exits(self):
        exits = []
        if self.maze.go(self.x, self.y, NORTH):
                exits.append("[N] North")
        if self.maze.go(self.x, self.y, SOUTH):
                exits.append("[S] South")
        if self.maze.go(self.x, self.y, WEST):
                exits.append("[W] West")
        if self.maze.go(self.x, self.y, EAST):
                exits.append("[E] East")
        if len(exits)==1:
            self.log.add("You reached a deadend.\nYou can only go "+exits[0])
        else:
            self.log.add("You can go "+doCommaSentence(exits,"or"))

    def playerChoice(self):
        import time
        key=''
        while key!='q':
            self.log.add("You are in a small condensed room with stone walls. A torch flickers in the corner.\n")
            if self.monster > 50:
                self.doCombat()
            else:
                self.exits()
                self.log.add("What do you do ? ")
                key = self.userinput.get()
                if key=='n' and self.maze.go(self.x,self.y,NORTH):
                    self.log.add("You go north\n")
                    self.y -=1
                    self.sleep(.3)
                    self.monster = random.randint(1,100)
                elif key=='s' and self.maze.go(self.x,self.y,SOUTH):
                    self.log.add("you go south\n")
                    self.y +=1
                    self.sleep(.3)
                    self.monster = random.randint(1,100)
                elif key=='e' and self.maze.go(self.x,self.y,EAST):
                    self.log.add("you go east\n")
                    self.x +=1
                    self.sleep(.3)
                    self.monster = random.randint(1,100)
                elif key=='w' and self.maze.go(self.x,self.y,WEST):
                    self.log.add("you go west\n")
                    self.x -=1
                    self.sleep(.3)
                    self.monster = random.randint(1,100)
                elif self.player.useInventory(key):
                    self.log.add("Aahhhh .. You drank a potion .. ")
                    self.updateHealth()
                    self.updateInventory()
                else:
                    self.log.add("You cannot..\n")
        self.log.add("Adventure ended .. ")
        self.sleep(2)
        self.log.stop()
        cls()
        print("Thanks for playing .. See ya next time ...\n")


#print(goDown(10))


def garbage():
    key = ''
    userinput = Userinput()

    px = 20
    py = 6

    locate(px,py,"Hello to new adventures")
    #cmd = rawput(["Hello","Bye"])
    while key!='q':
        key = userinput.get()
        if key=='a':
            locate(px,py,"You attack the ork"+" "*20)
        if key=='f':
            locate(px,py,"You try to flee"+" "*20)
        if key=='d':
            locate(px,py,"you successfully dodge the ord"+" "*20)
        if key=='s':
            locate(px,py,"you cast as spell"+" "*20)

player = NPC("Rasmus")
game = RPGame(player)
