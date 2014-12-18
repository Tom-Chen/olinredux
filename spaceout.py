# Olin in SPACE
# An auto-scrolling shooter

from time import sleep
import random
from math import ceil
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
from explosion import *
from beam import *
from boss import *


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
        # if key in ["1","2","3"]:
        if key in ["1","2"]:
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
                    Projectile(self._player._x+1,self._player._y,False,3,"Ally",1,"rapidshot.gif").materialize(self._screen,self._player._x+1,self._player._y)
                    q.enqueue(30, WeaponCooldownOff(self._player))
                # if(self._player._weapon == "Splash"):
                    # self._player._weaponready = False
                    # Projectile(self._player._x+1,self._player._y,True,"Ally",1,"rapidshot.gif").materialize(self._screen,self._player._x+1,self._player._y)
                    # q.enqueue(30, WeaponCooldownOff(self._player))
                  
                if(self._player._weapon == "Beam"):
                    self._player._weaponready = False
                    if Boss.spawned == False:
                        for hostile in Hostile.hostiles:
                            if self._player._y == hostile._y:
                                hostile.take_damage(3)
                                explosion = Explosion(hostile._x, hostile._y).materialize(self._screen,hostile._x, hostile._y)
                                q.enqueue(2,UpdateExplosions(self._screen,self._window,explosion))
                    elif Boss.spawned == True and Boss.ready == True:
                        boss = Boss.bosses[0]
                        if boss._y - boss._halfheight <= self._player._y <= boss._y + boss._halfheight:
                            boss.take_damage(3)
                            frontedge = boss._x - boss._halfwidth
                            explosion = Explosion(frontedge, self._player._y).materialize(self._screen,frontedge, self._player._y)
                            q.enqueue(2,UpdateExplosions(self._screen,self._window,explosion))
                    #draw beams
                    beam = Beam().materialize(self._screen,self._screen._cx, self._player._y)
                    q.enqueue(20, ClearBeam(beam))
                    q.enqueue(50, WeaponCooldownOff(self._player))
                
        q.enqueue(2,self)
        
# Autoscroller event
class ScrollForward (object):
    def __init__ (self,window,player,screen,healthbar):
        self._player = player
        self._window = window
        self._screen = screen
        self._healthbar = healthbar

    def event (self,q):
        tx = self._player._x + 1
        # only move as long as we have enough screen to scroll
        if in_level(tx+VIEWPORT_WIDTH,self._player._y):
            self._player._x = tx
            self._screen._cx += 1
            # self._screen.shift(1,0)
            # z_raise(self._player._sprite)
            # move hostile sprites
            for hostile in Hostile.hostiles:
                if(hostile._charging == False):
                    hostile._sprite.move(-1 * TILE_SIZE,0)
                else:
                    hostile.move(-1,0)
                    hostile._sprite.move(-1 * TILE_SIZE,0)
                # z_raise(hostile._sprite)
            q.enqueue(10,self)
        else:
            # if screen isn't moving just kill everything
            for hostile in Hostile.hostiles:
                if not(hostile.is_boss()):
                    explosion = Explosion(hostile._x, hostile._y).materialize(self._screen,hostile._x, hostile._y)
                    q.enqueue(2,UpdateExplosions(self._screen,self._window,explosion))
                    hostile.move(-3,0)
                    hostile.die()
                    # z_raise(hostile._sprite)
            log("Spawning Boss")
            boss = Boss().materialize(self._screen,self._screen._cx+(VIEWPORT_WIDTH),self._screen._cy)
            z_lower(boss._sprite)
            z_lower(self._screen._bg)
            q.enqueue(1,BossAct(self._window,self._screen,self._player,self._healthbar,boss))
                
# Projectile movement and collision
class MoveProjectiles (object):
    def __init__ (self,window,player,screen,healthbar):
        self._player = player
        self._window = window
        self._screen = screen
        self._healthbar = healthbar

    def event (self,q):
      for projectile in Projectile.projectiles:
          projectile.move(projectile._speedx, projectile._speedy)
          # z_raise(projectile._sprite)
          if(projectile._side == "Ally"):
              if scrolling(self._screen._cx,self._screen._cy):
                  projectile._sprite.move(0.5 * projectile._speedx * TILE_SIZE,0)
              else:
                  projectile._sprite.move(projectile._speedx * TILE_SIZE,0)
              if(offscreen_right(projectile._x, self._screen._cx)):
                  projectile.die()
              if Boss.spawned == False:
                  for hostile in Hostile.hostiles:
                      # if (projectile._splash == False) and ((projectile._x, projectile._y) == (hostile._x, hostile._y)):
                      if ((projectile._x, projectile._y) == (hostile._x, hostile._y)):
                          hostile.take_damage(projectile._damage)
                          explosion = Explosion(hostile._x, hostile._y).materialize(self._screen,hostile._x, hostile._y)
                          q.enqueue(2,UpdateExplosions(self._screen,self._window,explosion))
                          projectile.die()
                          break
              elif Boss.spawned == True and Boss.ready == True:
                  boss = Boss.bosses[0]
                  frontedge = boss._x - boss._halfwidth
                  topedge = boss._y - boss._halfheight
                  botedge = boss._y + boss._halfheight
                  if ((frontedge) <= projectile._x <= (boss._x + boss._halfwidth)) and ((topedge) < projectile._y < (botedge)):
                          boss.take_damage(projectile._damage)
                          explosion = Explosion(projectile._x, projectile._y).materialize(self._screen,projectile._x, projectile._y)
                          q.enqueue(2,UpdateExplosions(self._screen,self._window,explosion))
                          projectile.die()
                  # effectively removes corners from the hitbox - for visual purposes only!
                  elif ((frontedge+3) <= projectile._x <= (boss._x + boss._halfwidth)) and (((topedge) == projectile._y) or (projectile._y == (botedge))):
                          boss.take_damage(projectile._damage)
                          explosion = Explosion(projectile._x, projectile._y).materialize(self._screen,projectile._x, projectile._y)
                          q.enqueue(2,UpdateExplosions(self._screen,self._window,explosion))
                          projectile.die()
          elif (projectile._side == "Enemy") and Boss.spawned == False:
              projectile._sprite.move(projectile._speedx * 2 * TILE_SIZE,0)
              if(offscreen_left(projectile._x, self._screen._cx)):
                  projectile.die()
              if((projectile._x, projectile._y) == (self._player._x, self._player._y)):
                  self._player.take_damage(q,1)
                  explosion = Explosion(self._player._x, self._player._y).materialize(self._screen,self._player._x, self._player._y)
                  q.enqueue(2,UpdateExplosions(self._screen,self._window,explosion))
                  self._healthbar.update(self._player._health, self._window)
                  projectile.die()
          elif (projectile._side == "Enemy") and Boss.spawned == True:
              # log([projectile._x,projectile._y,"projectile"])
              # log([self._player._x,self._player._y,"player"])
              projectile._sprite.move(projectile._speedx * TILE_SIZE,0)
              if(offscreen_left(projectile._x, self._screen._cx)):
                  projectile.die()
              if((projectile._x, projectile._y) == (self._player._x, self._player._y)):
                  self._player.take_damage(q,1)
                  explosion = Explosion(self._player._x, self._player._y).materialize(self._screen,self._player._x, self._player._y)
                  q.enqueue(2,UpdateExplosions(self._screen,self._window,explosion))
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
        if scrolling(self._screen._cx,self._screen._cy):
            spawnX = self._screen._cx + (VIEWPORT_WIDTH - 1)/2
            spot1,spot2,spot3,spot4,spot5,spot6 =  random.sample(range(1,20),6)
            Hostile().materialize(self._screen,spawnX,spot1)
            Hostile().materialize(self._screen,spawnX,spot2)
            Hostile().materialize(self._screen,spawnX,spot3)
            Hostile().materialize(self._screen,spawnX,spot4)
            Hostile().materialize(self._screen,spawnX,spot5)
            Hostile().materialize(self._screen,spawnX,spot6)
            for hostile in Hostile.hostiles:
                if(hostile._charging == False):
                    behavior = random.randint(0,4) % 2
                    if (behavior == 0):
                        Projectile(hostile._x-1,hostile._y,False,1,"Enemy",-1,"enemyshot.gif").materialize(self._screen,hostile._x-1,hostile._y)
                    elif (behavior == 1):
                        hostile._charging = True
                        hostile._sprite.undraw()
                        hostile._sprite = Image(Point(TILE_SIZE/2,TILE_SIZE/2),"enemycharging.gif")
                        self._screen.add(hostile,hostile._x,hostile._y)
            q.enqueue(100,self)
        else: # cleanup
            for hostile in Hostile.hostiles:
                if not(hostile.is_boss()):
                    explosion = Explosion(hostile._x, hostile._y).materialize(self._screen,hostile._x, hostile._y)
                    q.enqueue(2,UpdateExplosions(self._screen,self._window,explosion))
                    hostile.move(-3,0)
                    hostile.die()
    
        
# Collision Detection, Enemy Cleanup
class CheckPosition (object):
    def __init__ (self,window,player,screen,h):
        self._player = player
        self._window = window
        self._screen = screen
        self._healthbar = h
        
    def event (self,q):
        if Boss.spawned == False:
            for hostile in Hostile.hostiles:
              if((hostile._x == self._player._x) and (hostile._y == self._player._y) and (self._player._invulnerable == False)):
                  self._player.take_damage(q,1)
                  explosion = Explosion(self._player._x, self._player._y).materialize(self._screen,self._player._x, self._player._y)
                  q.enqueue(2,UpdateExplosions(self._screen,self._window,explosion))
                  self._healthbar.update(self._player._health, self._window)
                  hostile.die()
              if(offscreen_left(hostile._x, self._screen._cx)):
                  hostile.die()
            q.enqueue(10,self)
            
# # Invulnerability timer
# class PlayerShieldOff (object):
    # def __init__ (self,player):
        # self._player = player    
        
    # def event(self,q):
        # self._player._invulnerable = False
        # # log("Collision shield off")
        
# Weapon timer
class WeaponCooldownOff (object):
    def __init__ (self,player):
        self._player = player    
        
    def event(self,q):
        self._player._weaponready = True
        # log("Weapon ready")
        
# Beam erase
class ClearBeam (object):
    def __init__ (self,beam):
        self._beam = beam
        
    def event(self,q):
        # for beam in self._beams:
            self._beam.die()

# Boom!
class UpdateExplosions(object):
    def __init__(self,screen,window,explosion):
        self._screen = screen
        self._window = window
        self._explosion = explosion

    def event(self,q):
        self._explosion._sprite.undraw()
        if(self._explosion._stage < 13):
            self._explosion._stage += 1
            self._explosion._sprite = Image(Point(TILE_SIZE/2,TILE_SIZE/2),'explosion'+str(self._explosion._stage)+'.gif')
            self._screen.add(self._explosion,self._explosion._x,self._explosion._y)
            q.enqueue(2,self)


class BossAct(object):
    def __init__(self,window,screen,player,healthbar,boss):
        self._screen = screen
        self._window = window
        self._player = player
        self._healthbar = healthbar
        self._boss = boss
    def event(self,q):
        if(self._boss._x > (self._screen._cx+5)):
            self._boss.move(-0.25,0)
            q.enqueue(5,self)
        else:
            if (Boss.dead == False):
                Boss.ready = True
                z_raise(self._boss._sprite)
                frontedge = self._boss._x - self._boss._halfwidth
                topedge = self._boss._y - self._boss._halfheight
                bottomedge = self._boss._y + self._boss._halfheight
                
                firepattern = random.randint(0,11)
                topcannon = int(self._boss._y-2)
                midcannon = int(self._boss._y)
                botcannon = int(self._boss._y+2)
                if 0 <= firepattern <= 1:
                    # log([self._boss._x,self._boss._y,"boss"])
                    # log(q._contents)
                    Projectile(int(frontedge),midcannon,False,1,"Enemy",-1,"bossshot.gif").materialize(self._screen,int(frontedge),midcannon)
                    Projectile(int(frontedge),botcannon,False,1,"Enemy",-1,"bossshot.gif").materialize(self._screen,int(frontedge),botcannon)
                    Projectile(int(frontedge),topcannon,False,1,"Enemy",-1,"bossshot.gif").materialize(self._screen,int(frontedge),topcannon)
                if 2 <= firepattern <= 3:
                    Projectile(int(frontedge),botcannon,False,1,"Enemy",-1,"bossshot.gif").materialize(self._screen,int(frontedge),botcannon)
                    Projectile(int(frontedge),topcannon,False,1,"Enemy",-1,"bossshot.gif").materialize(self._screen,int(frontedge),topcannon)
                if 4 <= firepattern <= 5:
                    Projectile(int(frontedge),midcannon,False,1,"Enemy",-1,"bossshot.gif").materialize(self._screen,int(frontedge),midcannon)
                if 6 <= firepattern <= 7:
                    Projectile(int(frontedge),botcannon,False,1,"Enemy",-1,"bossshot.gif").materialize(self._screen,int(frontedge),botcannon)
                if 8 <= firepattern <= 9:
                    Projectile(int(frontedge),topcannon,False,1,"Enemy",-1,"bossshot.gif").materialize(self._screen,int(frontedge),topcannon)

                movement = random.randint(0,6)
                if 0 <= movement <= 1 and in_level(self._boss._x, topedge)and in_level(self._boss._x, bottomedge):
                    self._boss.move(0,self._boss._lastmove)
                elif 2 <= movement <= 3 and in_level(self._boss._x, bottomedge):
                    self._boss._lastmove = 0.5
                    self._boss.move(0,self._boss._lastmove)
                elif 4 <= movement <= 5 and in_level(self._boss._x, topedge):
                    self._boss._lastmove = -0.5
                    self._boss.move(0,self._boss._lastmove)
                elif movement == 6:
                    self._boss._lastmove = 0
                q.enqueue(30,self)
            elif(Boss.dead == True): # Victory explosion!
                self._player._invulnerable = True
                log("You win!")
                q.enqueue(2,VictoryExplosions(self._window,self._screen,1))

class VictoryExplosions(object):

    def __init__(self,window,screen,counter):
        self._screen = screen
        self._window = window
        self._counter = counter
        
    def event(self,q):
        if(self._counter <= 70):
            for i in range(random.randint(1,ceil(self._counter/5)+1)):
                ex = self._screen._cx+random.randint(0-ceil(self._counter/10),9)
                ey = self._screen._cy+random.randint(-9,9)
                explosion = Explosion(ex,ey).materialize(self._screen,ex,ey)
                q.enqueue(2,UpdateExplosions(self._screen,self._window,explosion))
            self._counter += 1
            q.enqueue(5,self)
        else:
            self._screen._bg.undraw()
            self._screen._bg = Rectangle(Point(-20,-20),Point(WINDOW_WIDTH+20,WINDOW_HEIGHT+20))
            if(self._counter == 75):
                exit(0)
            elif(self._counter == 74):
                self._screen._bg.setFill("white")
                self._screen._bg.setOutline("white")
                self._screen._bg.draw(self._window)
                self._counter += 1
                q.enqueue(120,self)
            elif(self._counter == 73):
                self._screen._bg.setFill("lightgrey")
                self._screen._bg.setOutline("lightgrey")
                self._screen._bg.draw(self._window)
                self._counter += 1
                q.enqueue(80,self)
            elif(self._counter == 72):
                self._screen._bg.setFill("grey")
                self._screen._bg.setOutline("grey")
                self._screen._bg.draw(self._window)
                self._counter += 1
                q.enqueue(80,self)
            elif(self._counter == 71):
                self._screen._bg.setFill("darkgrey")
                self._screen._bg.setOutline("darkgrey")
                self._screen._bg.draw(self._window)
                self._counter += 1
                q.enqueue(80,self)



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
    # q.enqueue(2,VictoryExplosions(window,scr,1))
    q.enqueue(10,ScrollForward(window,p,scr,h))
    q.enqueue(5,MoveProjectiles(window,p,scr,h))
    q.enqueue(10,CheckPosition(window,p,scr,h))
    q.enqueue(100, EnemyAction(window,p,scr))

    while True:
        # Grab the next event from the queue if it's ready
        q.dequeue_if_ready()
        # Time unit = 10 milliseconds
        sleep(0.01)



if __name__ == '__main__':
    main()
    # cProfile.run('main()')
