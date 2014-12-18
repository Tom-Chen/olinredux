#
# A Screen is a representation of the level displayed in the 
# viewport, with a representation for all the tiles and a 
# representation for the objects in the world currently 
# visible. Managing all of that is key. 
#
# For simplicity, a Screen object contain a reference to the
# level it is displaying, and also to the window in which it
# draws its elements. So you can use the Screen object to 
# mediate access to both the level and the window if you need
# to access them.
# 
# You'll DEFINITELY want to add methods to this class. 
# Like, a lot of them.
#

from graphics import *
from helpers import *

class Screen (object):
    def __init__ (self,level,window,cx,cy):
        self._level = level
        self._window = window
        self._cx = cx    # the initial center tile position 
        self._cy = cy    #  of the screen
        self._things = []
        # Background is black
        # self._bg = Rectangle(Point(-20,-20),Point(WINDOW_WIDTH+20,WINDOW_HEIGHT+20))
        # self._bg.setFill("black")
        # self._bg.setOutline("black")
        self._bg = Image(Point(TILE_SIZE*self._cx,TILE_SIZE*self._cy),"background.gif")
        self._bg.draw(window)
        # here, you want to draw the tiles that are visible
        # and possible record them for future manipulation
        # you'll probably want to change this at some point to
        # get scrolling to work right...
        self._onscreen = []
        # self.firstDraw()

    def color(self,elt,currentTile):
        if currentTile == 0:
            elt.setFill('black')
            elt.setOutline('black')
        if currentTile == 1:
            elt.setFill('sienna')
            elt.setOutline('sienna')
        elif currentTile == 2:
            elt.setFill('darkgrey')
            elt.setOutline('darkgrey')
        elif currentTile == 3:
            elt.setFill('darkblue')
            elt.setOutline('darkblue')
        elif currentTile == 4:
            elt.setFill('darkred')
            elt.setOutline('darkred')
        
    def shift(self,dx,dy):
        # moves all current tiles. If tiles move offscreen (based on their point1) remove them
        for tile in self._onscreen:
            tile.move(-dx*TILE_SIZE,-dy*TILE_SIZE)
            if tile.p1.x < 0 and tile.p1.x/TILE_SIZE +1 > VIEWPORT_WIDTH and tile.p1.y < 0 and title.p1.y/TILE_SIZE + 1 > VIEWPORT_HEIGHT:
                tile.undraw()
                self._onscreen.remove(tile)
        # redraw new tiles
        if(dx != 0):
            if(dx == 1):
                sx = (VIEWPORT_WIDTH-1) * TILE_SIZE
            if(dx == -1):
                sx = 0
            for y in range(self._cy-HALFHEIGHT,self._cy+HALFHEIGHT+1):
                # small star test
                sy = (y-(self._cy-HALFHEIGHT)) * TILE_SIZE
                elt = Rectangle(Point(sx+6,sy+6),
                Point(sx+TILE_SIZE-6,sy+TILE_SIZE-6))
                currentTile = self.tile(self._cx + HALFWIDTH+1,y)
                self.color(elt,currentTile)
                self._onscreen.append(elt)
                elt.draw(self._window)

            
        
    def firstDraw(self):
        for y in range(self._cy-HALFHEIGHT,self._cy+HALFHEIGHT+1):
            for x in range(self._cx-HALFWIDTH,self._cx+HALFWIDTH+1):
                sx = (x-(self._cx-HALFWIDTH)) * TILE_SIZE
                sy = (y-(self._cy-HALFHEIGHT)) * TILE_SIZE
                # small star test
                elt = Rectangle(Point(sx+6,sy+6),
                                Point(sx+TILE_SIZE-6,sy+TILE_SIZE-6))
                currentTile = self.tile(x,y)
                self.color(elt,currentTile)
                self._onscreen.append(elt)
                elt.draw(self._window)

    # return the tile at a given tile position
    def tile (self,x,y):
        return self._level.tile(x,y)

    # add a thing to the screen at a given position
    def add (self,item,x,y):
        # first, move object into given position
        item.sprite().move((x-(self._cx-(VIEWPORT_WIDTH-1)/2))*TILE_SIZE,
                           (y-(self._cy-(VIEWPORT_HEIGHT-1)/2))*TILE_SIZE)
        item.sprite().draw(self._window)


    # helper method to get at underlying window
    def window (self):
        return self._window