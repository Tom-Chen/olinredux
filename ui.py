from thing import *
from graphics import *

def create_panel (window):
    log("panel created")
    fg = Rectangle(Point(WINDOW_WIDTH+1,-20),
                   Point(WINDOW_WIDTH +WINDOW_RIGHTPANEL+20,WINDOW_HEIGHT+20))
    fg.setFill("darkgray")
    fg.setOutline("black")
    fg.draw(window)
    fg = Text(Point(WINDOW_WIDTH + 114,
              30),"Health: ")
    fg.setFill("darkgreen")
    fg.setSize(24)
    fg.draw(window)
    fg = Text(Point(WINDOW_WIDTH + 100,
              72),"Weapon: ")
    fg.setFill("darkgreen")
    fg.setSize(24)    
    fg.draw(window)
    log("UI created")

class HealthBar (Thing):
    def __init__ (self):
        self._sprite = Text(Point(WINDOW_WIDTH + 174,
                            30),10)
        self._sprite.setSize(24)
        self._sprite.setFill("darkgreen")
        
    def update(self,health,window):
              self._sprite.undraw()
              self._sprite = Text(Point(WINDOW_WIDTH + 174,
                                        30),health)
              self._sprite.setFill("darkgreen")
              self._sprite.setOutline("darkgreen")
              self._sprite.setSize(24)
              self._sprite.draw(window)

    def is_walkable (self):
        return True
        
class WeaponSelect (Thing):
    def __init__ (self):
        self._sprite = Text(Point(WINDOW_WIDTH + 200,
                            72),"Beam")
        self._sprite.setSize(24)
        self._sprite.setFill("darkgreen")
        
    def update(self,weapon,window):
              self._sprite.undraw()
              self._sprite = Text(Point(WINDOW_WIDTH + 200,
                                        72),weapon)
              self._sprite.setFill("red")
              self._sprite.setOutline("darkgreen")
              self._sprite.setSize(24)
              self._sprite.draw(window)

    def is_walkable (self):
        return True