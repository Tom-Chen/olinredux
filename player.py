#
# The Player mobilething
#

from mobilething import *
from helpers import *

class Player (MobileThing):
    def __init__ (self):
        MobileThing.__init__(self)
        # log("Player.__init__ for "+str(self))
        self._sprite = Image(Point(TILE_SIZE/2,TILE_SIZE/2),'mainship.gif')
        self._invulnerable = False
        self._health = 10
        self._weaponready = True
        self._weapon = "Beam"
        
        # 1 beam
        # 2 rapid
        # 3 splash
                        
    def is_player (self):
        return True

    def take_damage (self,q,damage):
        if(self._health > 1):
            # log("Ouch!")
            # self._invulnerable = True
            self._health -= damage
            # log(("Remaining Health: " +  str(self._health)))
            # log("Collision shield on")
            # q.enqueue(150,PlayerShieldOff(self))
            
        else:
            self.die()

    def die (self):
        log("Game Over!")
        exit(0)
        
class PlayerShieldOff (object):
    def __init__ (self,player):
        self._player = player    
        
    def event(self,q):
        self._player._invulnerable = False
        log("Collision shield off")