from mobilething import *
from helpers import *

# Moves and does damage on contact
# Projectiles can die on collision
class Projectile (MobileThing):
    projectiles = []
    def __init__ (self,x,y,splash,damage,side,speedx,sprite):
        MobileThing.__init__(self)
        self._sprite = Image(Point(TILE_SIZE/2,TILE_SIZE/2),sprite)
        self._x = x
        self._y = y
        self._damage = damage
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
        # log("Projectile dead")
        Projectile.projectiles.remove(self)
        
    # def event (self,q):
        # self.move(speedx,speedy)
        # q.enqueue(5,self);