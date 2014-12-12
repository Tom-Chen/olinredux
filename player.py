#
# The Player mobilething
#

from mobilething import *
from helpers import *
from events import *

class Player (MobileThing):
    def __init__ (self):
        MobileThing.__init__(self)
        # log("Player.__init__ for "+str(self))
        pic = 't_android_red.gif'
        self._sprite = Image(Point(TILE_SIZE/2,TILE_SIZE/2),pic)
        self._invulnerable = False
        self._health = 10
        self._weaponready = True
        self._weapon = "Beam"
        
        # 1 beam
        # 2 rapid
        # 3 splash
                        
    def is_player (self):
        return True

    def take_damage (self,q):
        if(self._health > 1):
            log("Ouch!")
            self._invulnerable = True
            self._health -= 1
            log(("Remaining Health: " +  str(self._health)))
            log("Collision shield on")
            q.enqueue(120,PlayerShieldOff(self))
            
        else:
            self.die()

    def die (self):
        log("Game Over!")
        exit(0)