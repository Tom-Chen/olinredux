#
# MobileThings represent persons and animals and things that move
# about possibly proactively
#

from thing import *
from helpers import *



class MobileThing (Thing):
    def __init__ (self):
        Thing.__init__(self)
        # log("MobileThing.__init__ for "+str(self))
        rect = Rectangle(Point(1,1),
                         Point(TILE_SIZE-1,TILE_SIZE-1))
        rect.setFill("red")
        rect.setOutline("red")
        self._sprite = rect

    # A helper method to register the mobilething with the event queue
    # Call this method with a queue and a time delay before
    # the event is called
    # Note that the method returns the object itself, so we can
    # use method chaining, which is cool (though not as cool as
    # bowties...)
    
    def register (self,q,freq):
        self._freq = freq
        q.enqueue(freq,self)
        return self
        
    # A mobilething has a move() method that you should implement
    # to enable movement

    def move (self,dx,dy):
        tx = self._x + dx
        ty = self._y + dy
        if in_level(tx,ty):
            self._x = tx
            self._y = ty
            self._sprite.move(dx*TILE_SIZE,dy*TILE_SIZE)

    def is_mobilething (self):
        return True

    def is_walkable (self):
        return False