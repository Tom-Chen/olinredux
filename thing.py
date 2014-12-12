# A thing is something that can be interacted with and by default
# is not moveable or walkable over
#
#   Thing()
#
# A thing defines a default sprite in field _sprite
# To create a new kind of thing, subclass Thing and 
# assign it a specific sprite (see the OlinStatue below).
#

from root import *
from graphics import *
from helpers import * 


class Thing (Root):
    def __init__ (self):
        self._sprite = Text(Point(TILE_SIZE/2,TILE_SIZE/2),"?")
        # log("Thing.__init__ for "+str(self))

    def __str__ (self):
        return "<"+self+">"

    # return the sprite for display purposes
    def sprite (self):
        return self._sprite

    # return the position of the thing in the level array
    def position (self):
        return (self._x,self._y)
        
    # return the description
    def description (self):
        return self._description

    # creating a thing does not put it in play -- you have to 
    # call materialize, passing in the screen and the position
    # where you want it to appear
    def materialize (self,screen,x,y):
        screen.add(self,x,y)
        self._screen = screen
        self._x = x
        self._y = y
        return self

    def is_thing (self):
        return True

    def is_walkable (self):
        return False