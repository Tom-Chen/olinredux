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
from projectile import *
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
    def __init__ (self,window,player,screen,weapon):
        self._player = player
        self._window = window
        self._screen = screen
        self._weapon = weapon

    def event (self,q):
        key = self._window.checkKey()
        if key == 'q':
            self._window.close()
            exit(0)
        if key in ["1","2","3"]:
            self._player._weapon = WEAPON[key]
            self._weapon.update(self._player._weapon,self._window)
            # log(self._player._weapon + " active")
        if key in ['Up','Down']:
            (dx,dy) = MOVE[key]
            self._player.move(dx,dy)
        #firing code (probably put it in a function later)
        if (key == 'space'):
            if (self._player._weaponready == True):
                # log("Fire!")
                if(self._player._weapon == "Rapid"):
                    self._player._weaponready = False
                    Projectile(self._player._x+1,self._player._y,False,"Ally",1).materialize(self._screen,self._player._x+1,self._player._y)
                    q.enqueue(40, WeaponCooldownOff(self._player))
                if(self._player._weapon == "Splash"):
                    self._player._weaponready = False
                    Projectile(self._player._x+1,self._player._y,True,"Ally",1).materialize(self._screen,self._player._x+1,self._player._y)
                    q.enqueue(40, WeaponCooldownOff(self._player))
                  
                if(self._player._weapon == "Beam"):
                    self._player._weaponready = False
                    endx = TILE_SIZE * (VIEWPORT_WIDTH)
                    for hostile in Hostile.hostiles:
                        if self._player._y == hostile._y:
                            hostile.take_damage(3)
                            endx = (hostile._x * TILE_SIZE) - ((self._player._x-1) * TILE_SIZE)
                            break
                    #draw beams
                    sx = TILE_SIZE
                    sy = self._player._y * TILE_SIZE + TILE_SIZE/8
                    elt = Rectangle(Point(sx,sy),
                                    Point(endx,sy+(TILE_SIZE/8)))
                    elt.setFill('Blue')
                    elt.setOutline('Blue')
                    elt.draw(self._window)
                    sy = self._player._y * TILE_SIZE + TILE_SIZE*3/4
                    elt2 = Rectangle(Point(sx,sy),
                                     Point(endx,sy+(TILE_SIZE/8)))
                    elt2.setFill('Blue')
                    elt2.setOutline('Blue')
                    elt2.draw(self._window)
                    q.enqueue(10, ClearBeam(self._screen,[elt,elt2]))
                    q.enqueue(70, WeaponCooldownOff(self._player))
                
        q.enqueue(2,self)
        
# Autoscroller event
class ScrollForward (object):
    def __init__ (self,window,player,screen):
        self._player = player
        self._window = window
        self._screen = screen

    def event (self,q):
        tx = self._player._x + 1
        # only move as long as we have enough screen to scroll
        if in_level(tx+21,self._player._y):
            self._player._x = tx
            self._screen._cx += 1
            self._screen.shift(1,0)
            z_raise(self._player._sprite)
            # move hostile sprites
            for hostile in Hostile.hostiles:
                if(hostile._charging == False):
                    hostile._sprite.move(-1 * TILE_SIZE,0)
                else:
                    hostile.move(-1,0)
                    hostile._sprite.move(-1 * TILE_SIZE,0)
                z_raise(hostile._sprite)
            q.enqueue(10,self)
        else:
            # if screen isn't moving just move all hostiles regularly
            for hostile in Hostile.hostiles:
                hostile.move(-2,0)
                z_raise(hostile._sprite)
                
# Projectile movement and collision
class MoveProjectiles (object):
    def __init__ (self,window,player,screen,healthbar):
        self._player = player
        self._window = window
        self._screen = screen
        self._healthbar = healthbar

    def event (self,q):
      for projectile in Projectile.projectiles:
          projectile.move(projectile._speedx, projectile._speedy * TILE_SIZE)
          z_raise(projectile._sprite)
          if(projectile._side == "Ally"):
              if scrolling(self._screen._cx,self._screen._cy):
                  projectile._sprite.move(0.5 * projectile._speedx * TILE_SIZE,0)
              else:
                  projectile._sprite.move(projectile._speedx * TILE_SIZE,0)
              if(offscreen_right(projectile._x, self._screen._cx)):
                  projectile.die()
              for hostile in Hostile.hostiles:
                  # if (projectile._splash == False) and ((projectile._x, projectile._y) == (hostile._x, hostile._y)):
                  if ((projectile._x, projectile._y) == (hostile._x, hostile._y)):
                      hostile.take_damage(1)
                      projectile.die()
                      break
          elif (projectile._side == "Enemy"):
              projectile._sprite.move(projectile._speedx * 2 * TILE_SIZE,0)
              if(offscreen_left(projectile._x, self._screen._cx)):
                  projectile.die()
              if((projectile._x, projectile._y) == (self._player._x, self._player._y)):
                  self._player.take_damage(q)
                  self._healthbar.update(self._player._health, self._window)
                  projectile.die()
      q.enqueue(5,self)
        
# Control enemy behavior (spawning, firing, charging)
class EnemyAction (object):
    def __init__ (self,window,player,screen):
        self._player = player
        self._window = window
        self._screen = screen

    def event (self,q):
        # spawn = random.randint(0,1)
        if scrolling(self._screen._cx,self._screen._cy):
            # if(spawn == 0):
            spawnX = self._screen._cx + (VIEWPORT_WIDTH - 1)/2
            spot1,spot2,spot3,spot4,spot5,spot6 =  random.sample(range(1,20),6)
            Hostile().materialize(self._screen,spawnX,spot1)
            Hostile().materialize(self._screen,spawnX,spot2)
            Hostile().materialize(self._screen,spawnX,spot3)
            Hostile().materialize(self._screen,spawnX,spot4)
            Hostile().materialize(self._screen,spawnX,spot5)
            Hostile().materialize(self._screen,spawnX,spot6)
            for hostile in Hostile.hostiles:
                behavior = random.randint(0,4)
                if (behavior == 0):
                    Projectile(hostile._x-1,hostile._y,False,"Enemy",-1).materialize(self._screen,hostile._x-1,hostile._y)
                elif (behavior == 1):
                    hostile._charging = True
            q.enqueue(100,self)
        else:
            log("Spawn boss now")
    
        
# Collision Detection, Enemy Cleanup
class CheckPosition (object):
    def __init__ (self,window,player,screen,h):
        self._player = player
        self._window = window
        self._screen = screen
        self._healthbar = h
        
    def event (self,q):
        for hostile in Hostile.hostiles:
          if((hostile._x == self._player._x) and (hostile._y == self._player._y) and (self._player._invulnerable == False)):
              self._player.take_damage(q)
              self._healthbar.update(self._player._health, self._window)
          if(offscreen_left(hostile._x, self._screen._cx)):
              #hostile dying - check garbage collection
              Hostile.hostiles.remove(hostile)
              hostile._sprite.undraw()
        q.enqueue(10,self)
            
# Invulnerability timer
class PlayerShieldOff (object):
    def __init__ (self,player):
        self._player = player    
        
    def event(self,q):
        self._player._invulnerable = False
        # log("Collision shield off")
        
# Beam weapon timer
class WeaponCooldownOff (object):
    def __init__ (self,player):
        self._player = player    
        
    def event(self,q):
        self._player._weaponready = True
        # log("Weapon ready")
        
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
                      WINDOW_WIDTH + WINDOW_RIGHTPANEL, WINDOW_HEIGHT,
                      autoflush=False)

    level = Level()
    log ("level created")

    scr = Screen(level,window,10,10)
    log ("screen created")
    
    create_panel(window);
    
    q = EventQueue()

    p = Player().materialize(scr,0,10)
    h = HealthBar().materialize(scr,0,0)
    w = WeaponSelect().materialize(scr,0,0)

    q.enqueue(2,CheckInput(window,p,scr,w))
    q.enqueue(10,ScrollForward(window,p,scr))
    q.enqueue(5,MoveProjectiles(window,p,scr,h))
    q.enqueue(10,CheckPosition(window,p,scr,h))
    q.enqueue(10, EnemyAction(window,p,scr))

    while True:
        # Grab the next event from the queue if it's ready
        q.dequeue_if_ready()
        # Time unit = 10 milliseconds
        time.sleep(0.01)



if __name__ == '__main__':
    main()
    # cProfile.run('main()')
