import time

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

WEAPON = {
  "1": "Beam",
  "2": "Rapid"
}

# GLOBAL VARIABLES

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

WINDOW_RIGHTPANEL = 260