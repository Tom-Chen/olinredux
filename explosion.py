from thing import *

# Stationary explosion sprite
class Explosion (Thing):
    def __init__ (self,x,y):
        Thing.__init__(self)
        self._sprite = Image(Point(TILE_SIZE/2,TILE_SIZE/2),'explosion1.gif')
        self._stage = 1
        self._x = x
        self._y = y

    def die(self):
        self._sprite.undraw()