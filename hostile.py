# 
# Hostiles damage the player on collision 
#

import random
from mobilething import *
from helpers import *
from events import *

class Hostile (MobileThing):
    hostiles = []
    def __init__ (self):
        MobileThing.__init__(self)
        # log("hostile.__init__ for "+str(self))
        rect = Rectangle(Point(1,1),
                         Point(TILE_SIZE-1,TILE_SIZE-1))
        rect.setFill("red")
        rect.setOutline("red")
        self._sprite = rect
        self._charging = False
        self._health = 1
        Hostile.hostiles.append(self)
        
    def take_damage (self,damage):
        if(self._health > damage):
            self._health -= damage
        else:
            self.die()

    def die(self):
        log("Enemy Killed!")
        self._sprite.undraw()
        Hostile.hostiles.remove(self)
        
    # this gets called from event queue when the time is right
    
    # def event (self,q):
        # randomDirection = random.choice(MOVE.keys())
        # self.move(MOVE[randomDirection][0],MOVE[randomDirection][1])
        # log("event for "+str(self))
        # q.enqueue(100,self);