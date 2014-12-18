import random
from mobilething import *
from hostile import *
from helpers import *

class Boss (Hostile):
    bosses = []
    spawned = False
    ready = False
    dead = False
    def __init__ (self):
        Hostile.__init__(self)
        self._sprite = Image(Point(TILE_SIZE/2,TILE_SIZE/2),'boss.gif')
        self._health = 100
        Boss.spawned = True
        Boss.bosses.append(self)
        self._halfwidth = 5
        self._halfheight = 4
        self._lastmove = 0
        
    def take_damage (self,damage):
        if(self._health > damage):
            self._health -= damage
        else:
            # self._sprite.undraw()
            Boss.dead = True
            
    def move (self,dx,dy):
        tx = self._x + dx
        ty = self._y + dy
        self._x = tx
        self._y = ty
        self._sprite.move(dx*TILE_SIZE,dy*TILE_SIZE)
        
    def is_boss(self):
        return True