# Olin in SPACE
# An auto-scrolling shooter

import time
import random
from graphics import *

from root import *
from thing import *
from ui import *
from mobilething import *
from player import *
from hostile import *
from level import *
from screen import *
from eventqueue import *
from helpers import *
from events import *

import cProfile

#
# EVENTS
#

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
        #firing code (probably put it in a function later)
        if (key == 'space'):
            if (self._player._weaponready == True):
                self._player._weaponready = False
                log("Fire!")
                for hostile in Hostile.hostiles:
                    # log(hostile._y)
                    if self._player._y == hostile._y:
                        hostile.die()
                q.enqueue(100, BeamCooldownOff(self._player))
                #draw beams
                sx = TILE_SIZE
                sy = self._player._y * TILE_SIZE + TILE_SIZE/8
                elt = Rectangle(Point(sx,sy),
                Point(((sx+TILE_SIZE) * VIEWPORT_WIDTH),sy+(TILE_SIZE/8)))
                elt.setFill('Blue')
                elt.setOutline('Blue')
                elt.draw(self._window)
                sx = TILE_SIZE
                sy = self._player._y * TILE_SIZE + TILE_SIZE*3/4
                elt2 = Rectangle(Point(sx,sy),
                Point(((sx+TILE_SIZE) * VIEWPORT_WIDTH),sy+(TILE_SIZE/8)))
                elt2.setFill('Blue')
                elt2.setOutline('Blue')
                elt2.draw(self._window)
                q.enqueue(10, ClearBeam(self._screen,[elt,elt2]))
                
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
            q.enqueue(2,self)
        else:
            for hostile in Hostile.hostiles:
                hostile.move(-1 * TILE_SIZE,0)
                z_raise(hostile._sprite)
        
# Spawn enemies
class SpawnWave (object):
    def __init__ (self,window,player,screen):
        self._player = player
        self._window = window
        self._screen = screen

    def event (self,q):
        if in_level(self._screen._cx + VIEWPORT_WIDTH, self._screen._cy):
            spawnX = self._screen._cx + (VIEWPORT_WIDTH - 1)/2
            Hostile("Scoundrel","A scoundrel").materialize(self._screen,spawnX,random.randint(1,20))
            Hostile("Rogue","A rogue").materialize(self._screen,spawnX,random.randint(1,20))
            Hostile("Ruffian","A ruffian").materialize(self._screen,spawnX,random.randint(1,20))
            Hostile("Jerk","A jerk").materialize(self._screen,spawnX,random.randint(1,20))
            Hostile("Awful","Wow!").materialize(self._screen,spawnX,random.randint(1,20))
            Hostile("Villain","A villain").materialize(self._screen,spawnX,random.randint(1,20))
            q.enqueue(100,self)
        else:
            log("Spawn boss now")
    
        
# Collision Detection, Enemy Cleanup
class CheckPosition (object):
    def __init__ (self,window,player,screen):
        self._player = player
        self._window = window
        self._screen = screen
        
    def event (self,q):
        for hostile in Hostile.hostiles:
          if((hostile._x == self._player._x) and (hostile._y == self._player._y) and (self._player._invulnerable == False)):
              self._player.take_damage(q)
          if(hostile._x < (self._screen._cx - (VIEWPORT_WIDTH - 1) / 2)):
              #hostile dying - check garbage collectioni
              Hostile.hostiles.remove(hostile)
        q.enqueue(10,self)
            
# Invulnerability timer
class PlayerShieldOff (object):
    def __init__ (self,player):
        self._player = player    
        
    def event(self,q):
        self._player._invulnerable = False
        log("Collision shield off")
        
# Beam weapon timer
class BeamCooldownOff (object):
    def __init__ (self,player):
        self._player = player    
        
    def event(self,q):
        self._player._weaponready = True
        log("Beam ready")
        
# Beam erase
class ClearBeam (object):
    def __init__ (self,screen,beams):
        self._screen = screen
        self._beams = beams
        
    def event(self,q):
        for beam in self._beams:
            beam.undraw()

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

    p = Player("...what's your name, bub?...").materialize(scr,0,10)
    h = HealthBar().materialize(scr,20,1)

    q.enqueue(2,CheckInput(window,p,scr))
    q.enqueue(2,ScrollForward(window,p,scr))
    q.enqueue(10,CheckPosition(window,p,scr))
    q.enqueue(10, SpawnWave(window,p,scr))

    while True:
        # Grab the next event from the queue if it's ready
        q.dequeue_if_ready()
        # Time unit = 10 milliseconds
        time.sleep(0.01)



if __name__ == '__main__':
    main()
    # cProfile.run('main()')
