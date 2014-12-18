from thing import *

class Explosion (Thing):
    def __init__ (self,x,y):
        Thing.__init__(self)
        self._sprite = Image(Point(TILE_SIZE/2,TILE_SIZE/2),'explosion1.gif')
        self._stage = 1
        self._x = x
        self._y = y
        
    def update(self):
        self._stage += 1
        if self._stage < 5:
            self._sprite = Image(Point(TILE_SIZE/2,TILE_SIZE/2),'explosion'+str(self._stage)+'.gif')
            self._sprite.undraw()
        else:
            self.die()

    def die(self):
        self._sprite.undraw()