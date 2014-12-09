from thing import *
from graphics import *

def create_panel (window):
    log("panel created")
    fg = Rectangle(Point(WINDOW_WIDTH+1,-20),
                   Point(WINDOW_WIDTH +WINDOW_RIGHTPANEL+20,WINDOW_HEIGHT+20))
    fg.setFill("darkgray")
    fg.setOutline("darkgray")
    fg.draw(window)
    fg = Text(Point(WINDOW_WIDTH + 114,
              30),"Health: ")
    fg.setFill("red")
    fg.setSize(24)
    fg.draw(window)
    fg = Text(Point(WINDOW_WIDTH + 100,
              72),"Weapon: ")
    fg.setFill("red")
    fg.setSize(24)    
    fg.draw(window)

class HealthBar (Thing):
    def __init__ (self):
        self._name = "Player's Health Bar"
        self._desc = "Don't let it run out!"
        self._sprite = Text(Point(WINDOW_WIDTH + 174,
                            30),3)
        self._sprite.setSize(24)
        self._sprite.setFill("red")
        
    def update(self,health,window):
              self._sprite.undraw()
              self._sprite = Text(Point(WINDOW_WIDTH + 174,
                                        30),health)
              self._sprite.setFill("red")
              self._sprite.setOutline("red")
              self._sprite.setSize(24)
              self._sprite.draw(window)

    def is_walkable (self):
        return True
        
class WeaponSelect (Thing):
    def __init__ (self):
        self._name = "Player's Weapon"
        self._desc = "Boom!"
        self._sprite = Text(Point(WINDOW_WIDTH + 200,
                            72),"Beam")
        self._sprite.setSize(24)
        self._sprite.setFill("red")
        
    def update(self,weapon,window):
              self._sprite.undraw()
              self._sprite = Text(Point(WINDOW_WIDTH + 200,
                                        72),weapon)
              self._sprite.setFill("red")
              self._sprite.setOutline("red")
              self._sprite.setSize(24)
              self._sprite.draw(window)

    def is_walkable (self):
        return True