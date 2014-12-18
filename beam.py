from thing import *

class Beam (Thing):
    def __init__ (self):
        Thing.__init__(self)
        self._sprite = Image(Point(TILE_SIZE/2,TILE_SIZE/2),'beam.gif')

    def die(self):
        self._sprite.undraw()