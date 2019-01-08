# Game-specific modules
from Config import *
from Colors import *
from Shapes import *

##########
# Game options -- specific to this game
##########
Opt = type('Opt', ( object, ), {
  # Play options
  'revealSpeed' : 16
, 'boxSize'     : 40
, 'gapSize'     : 10
, 'boardWidth'  : 5
, 'boardHeight' : 4
  # Appearance options
, 'bgColor'        : Colors['navyBlue']
, 'bgLightColor'   : Colors['gray']
, 'boxColor'       : Colors['white']
, 'highlightColor' : Colors['blue']
})
# Determine margins
Opt.xMargin = int( ( Config.windowWidth - ( Opt.boardWidth * (Opt.boxSize + Opt.gapSize ))) / 2 )
Opt.yMargin = int( ( Config.windowHeight - ( Opt.boardHeight * (Opt.boxSize + Opt.gapSize ))) / 2 )
