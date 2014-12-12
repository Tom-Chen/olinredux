from mobilething import *
from helpers import *
from events import *

class Projectile (MobileThing):
    projectiles = []
    def __init__ (self,x,y,splash,side,speedx):
        MobileThing.__init__(self)
        # log("hostile.__init__ for "+str(self))
        rect = Rectangle(Point(1,1),
                         Point(TILE_SIZE-1,TILE_SIZE-1))
        rect.setFill("yellow")
        rect.setOutline("yellow")
        self._sprite = rect
        self._x = x
        self._y = y
        self._damage = 1
        self._speedx = speedx
        self._speedy = 0
        self._side = side
        self._splash = splash
        Projectile.projectiles.append(self)
        
    def move (self,dx,dy):
        tx = self._x + dx
        ty = self._y + dy
        if in_level(tx,ty):
            self._x = tx
            self._y = ty
            
    def die(self):
        self._sprite.undraw()
        log("Projectile dead")
        Projectile.projectiles.remove(self)
        
    def event (self,q):
        self.move(speedx,speedy)
        q.enqueue(5,self);