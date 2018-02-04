from rwutility import *
import time
import threading

class Journal:

    def __init__(self,x,y,width,height):
        self.x = x
        self.y = y
        self.width = width
        self.loglines = height
        self.lines = []
        self.active = True
        self.scrollLine = 0
        self.service = threading.Thread(target=self.process)

    def process(self):
        while self.active:
            while self.scrollLine <= len(self.lines):
                start = self.loglines-self.scrollLine
                for row in range(0,self.loglines):
                    if row >= start:
                        line = self.lines[row-start]
                        try:
                            locate(self.y+row,self.x,line+" "*(self.width-len(line)))
                        except Exception:
                            pass
                    else:
                        try:
                            locate(self.y+row,self.x," "*self.width)
                        except Exception:
                            pass
                self.scrollLine+=1
                time.sleep(0.05)
            time.sleep(0.5)


    def start(self):
        self.active = True
        self.service.start()

    def add(self,text):
        self.lines += wrapper(text,indent=0,width=self.width)
        while len(self.lines) > self.loglines and self.scrollLine ==len(self.lines):
            self.lines = self.lines[1:]
            self.scrollLine -= 1

    def stop(self):
        self.active = False


def how_to_use_Journal():
    cls()

    log = Journal(10,10,30,20)
    log.start()

    userinput = Userinput()
    ptn=''
    while ptn!=rw_ENTER and ptn!=rw_ESC:
        ptn = userinput.get()
        if ptn not in rw_SPECIALS:
            log.add("Another line added ;-)")
            log.add("Yeah - number ")
            log.add("")
            log.add("Du tastede "+ptn)

    log.stop()
    print("Program ended...")
