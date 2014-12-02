# Olin in SPACE
# An auto-scrolling shooter

import time
import random
from graphics import *
import cProfile
import re

# Helpers
def in_level(x,y):
    return x >= 0 and y >= 0 and x < LEVEL_WIDTH and y < LEVEL_HEIGHT

def log (message):
    print time.strftime("[%H:%M:%S]",time.localtime()),message

def z_raise (elt):
    elt.canvas.tag_raise(elt.id)
 
def z_lower (elt):
    elt.canvas.tag_lower(elt.id)
    
MOVE = {
    'Left': (-1,0),
    'Right': (1,0),
    'Up' : (0,-1),
    'Down' : (0,1)
}

# Tile size of the level
LEVEL_WIDTH = 201
LEVEL_HEIGHT = 21

# Tile size of the viewport (through which you view the level)
VIEWPORT_WIDTH = 21
VIEWPORT_HEIGHT = 21   

HALFWIDTH = (VIEWPORT_WIDTH-1)/2
HALFHEIGHT = (VIEWPORT_HEIGHT-1)/2

# Pixel size of a tile (which gives you the size of the window)
TILE_SIZE = 24

# Pixel size of the viewport
WINDOW_WIDTH = TILE_SIZE * VIEWPORT_WIDTH
WINDOW_HEIGHT = TILE_SIZE * VIEWPORT_HEIGHT

# # Pixel size of the panel on the right where you can display stuff
# WINDOW_RIGHTPANEL = 200


#############################################################
# 
# The class hierarchy for objects that you can interact with
# in the world
#
# Roughly modeled from the corresponding hierarchy in our
# adventure game
#

#
# The root object
#
class Root (object):
    # default predicates

    # is this object a Thing?
    def is_thing (self):
        return False

    # is this object a MobileThing?
    def is_mobilething (self):
        return False

    # is this object the Player?
    def is_player (self):
        return False

    # can this object be walked over during movement?
    def is_walkable (self):
        return False


# A thing is something that can be interacted with and by default
# is not moveable or walkable over
#
#   Thing(name,description)
#
# A thing defines a default sprite in field _sprite
# To create a new kind of thing, subclass Thing and 
# assign it a specific sprite (see the OlinStatue below).
# 
class Thing (Root):
    def __init__ (self,name,desc):
        self._name = name
        self._description = desc
        self._sprite = Text(Point(TILE_SIZE/2,TILE_SIZE/2),"?")
        log("Thing.__init__ for "+str(self))

    def __str__ (self):
        return "<"+self.name()+">"

    # return the sprite for display purposes
    def sprite (self):
        return self._sprite

    # return the name
    def name (self):
        return self._name

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

class HealthBar (Thing):
    def __init__ (self):
        self._name = "Player's Health Bar"
        self._desc = "Don't let it run out!"
        self._sprite = Text(Point(WINDOW_WIDTH - 100,
                            30),3)
        self._sprite.setSize(24)
        self._sprite.setStyle("italic")
        self._sprite.setFill("red")

    def is_walkable (self):
        return True
     
#
# MobileThings represent persons and animals and things that move
# about possibly proactively
#
class MobileThing (Thing):
    def __init__ (self,name,desc):
        Thing.__init__(self,name,desc)
        log("MobileThing.__init__ for "+str(self))
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


# 
# Hostiles damage the player on collision 
#

class Hostile (MobileThing):
    hostiles = []
    def __init__ (self,name,desc):
        MobileThing.__init__(self,name,desc)
        log("hostile.__init__ for "+str(self))
        rect = Rectangle(Point(1,1),
                         Point(TILE_SIZE-1,TILE_SIZE-1))
        rect.setFill("red")
        rect.setOutline("red")
        self._sprite = rect
        self._direction = random.randrange(4)
        Hostile.hostiles.append(self)

    # this gets called from event queue when the time is right
    
    # def event (self,q):
        # randomDirection = random.choice(MOVE.keys())
        # self.move(MOVE[randomDirection][0],MOVE[randomDirection][1])
        # log("event for "+str(self))
        # q.enqueue(100,self);
        
        


#
# The Player mobilething
#
class Player (MobileThing):
    def __init__ (self,name):
        MobileThing.__init__(self,name,"Yours truly")
        log("Player.__init__ for "+str(self))
        pic = 't_android_red.gif'
        self._sprite = Image(Point(TILE_SIZE/2,TILE_SIZE/2),pic)
        self._invulnerable = False
        self._health = 3
                        
    def is_player (self):
        return True

    def take_damage (self,q):
        if(self._health > 1):
            log("Collision!")
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
        
#############################################################
# 
# The description of the world and the screen which displays
# the world
#
# A level contains the background stuff that you can't really
# interact with. The tiles are decorative, and do not come
# with a corresponding object in the world. (Though you can
# change that if you want.)
#
# Right now, a level is described using the following encoding
#
# 0 empty   (light green rectangle)
# 1 grass   (green rectangle)
# 2 tree    (sienna rectangle)
#
# you'll probably want to make nicer sprites at some point.


#
# This implements a random level right now. 
# You'll probably want to replace this with something that 
# implements a specific map -- perhaps of Olin?
#
class Level (object):
    def __init__ (self):
        size = LEVEL_WIDTH * LEVEL_HEIGHT
        map = [0] * size
        for i in range(100):
            map[random.randrange(size)] = 1
        for i in range(50):
            map[random.randrange(size)] = 2
        self._map = map

    def _pos (self,x,y):
        return x + (y*LEVEL_WIDTH);

    # return the tile at a given tile position in the level
    def tile (self,x,y):
        return self._map[self._pos(x,y)]



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
class Screen (object):
    def __init__ (self,level,window,cx,cy):
        self._level = level
        self._window = window
        self._cx = cx    # the initial center tile position 
        self._cy = cy    #  of the screen
        self._things = []
        # Background is black
        bg = Rectangle(Point(-20,-20),Point(WINDOW_WIDTH+20,WINDOW_HEIGHT+20))
        bg.setFill("black")
        bg.setOutline("black")
        bg.draw(window)
        # here, you want to draw the tiles that are visible
        # and possible record them for future manipulation
        # you'll probably want to change this at some point to
        # get scrolling to work right...
        self._onscreen = []
        self.firstDraw()

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
                sy = (y-(self._cy-HALFHEIGHT)) * TILE_SIZE
                elt = Rectangle(Point(sx,sy),
                Point(sx+TILE_SIZE,sy+TILE_SIZE))
                currentTile = self.tile(self._cx + HALFWIDTH+1,y)
                self.color(elt,currentTile)
                self._onscreen.append(elt)
                elt.draw(self._window)

            
        
    def firstDraw(self):
        for y in range(self._cy-HALFHEIGHT,self._cy+HALFHEIGHT+1):
            for x in range(self._cx-HALFWIDTH,self._cx+HALFWIDTH+1):
                sx = (x-(self._cx-HALFWIDTH)) * TILE_SIZE
                sy = (y-(self._cy-HALFHEIGHT)) * TILE_SIZE
                elt = Rectangle(Point(sx,sy),
                                Point(sx+TILE_SIZE,sy+TILE_SIZE))
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
        # WRITE ME!   You'll have to figure out how to manage these
        # because chances are when you scroll these will not move!


    # helper method to get at underlying window
    def window (self):
        return self._window

    

#############################################################
# 
# The event queue
#
# An event is any object that implements an event() method
# That event method gets the event queue as input, so that
# it can add to the event queue if it needs to.

class EventQueue (object):
    def __init__ (self):
        self._contents = []

    # list kept ordered by time left before firing
    def enqueue (self,when,obj):
        for (i,entry) in enumerate(self._contents):
            if when < entry[0]:
                self._contents.insert(i,[when,obj])
                break
        else:
            self._contents.append([when,obj])

    def ready (self):
        if self._contents:
            return (self._contents[0][0]==0)
        else:
            return False
        
    def dequeue_if_ready (self):
        acted = self.ready()
        while self.ready():
            entry = self._contents.pop(0)
            entry[1].event(self)
        for entry in self._contents:
            entry[0] -= 1


# A simple event class that checks for user input.
# It re-enqueues itself after the check.

class CheckInput (object):
    def __init__ (self,window,player,screen):
        self._player = player
        self._window = window
        self._screen = screen

    def event (self,q):
        key = self._window.checkKey()
        if key == 'q':
            self._window.close()
            exit(0)
        if key in ['Up','Down']:
            (dx,dy) = MOVE[key]
            self._player.move(dx,dy)
        q.enqueue(2,self)
        
# Autoscroller event
class ScrollForward (object):
    def __init__ (self,window,player,screen):
        self._player = player
        self._window = window
        self._screen = screen

    def event (self,q):
        tx = self._player._x + 1
        if in_level(tx+21,self._player._y):
            self._player._x = tx
            self._screen._cx += 1
            self._screen.shift(1,0)
            z_raise(self._player._sprite)
            for hostile in Hostile.hostiles:
                hostile._sprite.move(-1 * TILE_SIZE,0)
                z_raise(hostile._sprite)
        q.enqueue(20,self)
        
# Collision Detection 
class CheckCollision (object):
    def __init__ (self,player):
        self._player = player
        
    def event (self,q):
        for hostile in Hostile.hostiles:
          if((hostile._x == self._player._x) and (hostile._y == self._player._y) and (self._player._invulnerable == False)):
              self._player.take_damage(q)
        q.enqueue(10,self)
            
# Invulnerability timer
class PlayerShieldOff (object):
    def __init__ (self,player):
        self._player = player    
        
    def event(self,q):
        self._player._invulnerable = False
        log("Collision shield off")

# #
# # Create the right-side panel that can be used to display interesting
# # information to the player
# #
# def create_panel (window):
    # fg = Rectangle(Point(WINDOW_WIDTH+1,-20),
                   # Point(WINDOW_WIDTH+WINDOW_RIGHTPANEL+20,WINDOW_HEIGHT+20))
    # fg.setFill("darkgray")
    # fg.setOutline("darkgray")
    # fg.draw(window)
    # fg = Text(Point(WINDOW_WIDTH - 100,
                    # 30),"Olinland Redux")
    # fg.setSize(24)
    # fg.setStyle("italic")
    # fg.setFill("red")
    # fg.draw(window)


#
# The main function
# 
# It initializes everything that needs to be initialized
# Order is important for graphics to display correctly
# Note that autoflush=False, so we need to explicitly
# call window.update() to refresh the window when we make
# changes
#
def main ():
    window = GraphWin("Olinland Redux", 
                      WINDOW_WIDTH, WINDOW_HEIGHT,
                      autoflush=False)

    level = Level()
    log ("level created")

    scr = Screen(level,window,10,10)
    log ("screen created")
    
    q = EventQueue()

    Hostile("Scoundrel","A scoundrel").materialize(scr,10,10)
    Hostile("Rogue","A rogue").materialize(scr,14,10)
    Hostile("Ruffian","A ruffian").materialize(scr,18,10)
    Hostile("Jerk","A jerk").materialize(scr,22,10)
    Hostile("Awful","Wow!").materialize(scr,26,10)
    Hostile("Villain","A villain").materialize(scr,30,10)

    # create_panel(window)

    p = Player("...what's your name, bub?...").materialize(scr,0,10)
    h = HealthBar().materialize(scr,20,1)

    q.enqueue(2,CheckInput(window,p,scr))
    q.enqueue(20,ScrollForward(window,p,scr))
    q.enqueue(10,CheckCollision(p))

    while True:
        # Grab the next event from the queue if it's ready
        q.dequeue_if_ready()
        # Time unit = 10 milliseconds
        time.sleep(0.01)



if __name__ == '__main__':
    main()
    # cProfile.run('main()')
