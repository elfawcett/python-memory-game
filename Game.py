# Vendor modules
import pygame, random, sys
from pygame.locals import *
# App modules
from Opt import *

##########
# Main game function
##########
def main( savedSession = None ):
  global fpsClock, displaySurf # probably remove the global from these and just pass them into functions

  # Init
  pygame.init()

  fpsClock    = pygame.time.Clock()
  displaySurf = pygame.display.set_mode(( Config.windowWidth, Config.windowHeight ))

  pygame.display.set_caption( Config.title )

  # Session vars -- relative to the current play session
  Session = type('Session', ( object, ), {
    'mouseX'         : 0
  , 'mouseY'         : 0
  # , 'mainBoard'      : getRandomizedBoard() # could use savedSession's returned board here
  # , 'revealedBoxes'  : generateRevealedBoxesData( False )
  , 'firstSelection' : None
  , 'mouseClicked'   : False
  })
  mainBoard     = getRandomizedBoard()
  revealedBoxes = generateRevealedBoxesData( False )

  # If savedSession exists, use it to init Session?

  # Static content
  displaySurf.fill( Opt.bgColor )
  startGameAnimation( mainBoard )
  mouseX         = 0
  mouseY         = 0
  firstSelection = None
  mouseClicked   = False
  
  # Main loop
  while True:
    mouseClicked = False

    displaySurf.fill( Opt.bgColor )
    drawBoard( mainBoard, revealedBoxes )

    # Event loop
    for event in pygame.event.get():
      if event.type == MOUSEMOTION:
        mouseX, mouseY = event.pos

      if event.type == MOUSEBUTTONUP:
        mouseX, mouseY = event.pos
        mouseClicked = True

      # Quit game on QUIT or ESCAPE
      if event.type == QUIT or ( event.type == KEYUP and event.key == K_ESCAPE ):
        quitGame( pygame, sys )

    # Game logic
    boxX, boxY = getBoxAtPixel( mouseX, mouseY )
    if boxX != None and boxY != None:
      if not revealedBoxes[ boxX ][ boxY ]:
        drawHighlightBox( boxX, boxY )    

      if not revealedBoxes[ boxX ][ boxY ] and mouseClicked:
        revealBoxesAnimation( mainBoard, [( boxX, boxY )] )
        revealedBoxes[ boxX ][ boxY ] = True

        if firstSelection == None:
          firstSelection = ( boxX, boxY )
        else:
          shape1, color1 = getShapeAndColor( mainBoard, firstSelection[ 0 ], firstSelection[ 1 ] )
          shape2, color2 = getShapeAndColor( mainBoard, boxX, boxY )

          if shape1 != shape2 or color1 != color2:
            pygame.time.wait( 1000 )
            coverBoxesAnimation( mainBoard, [( firstSelection[ 0 ], firstSelection[ 1 ]), ( boxX, boxY )])
            revealedBoxes[ firstSelection[ 0 ]][ firstSelection[ 1 ]] = False
            revealedBoxes[ boxX ][ boxY ] = False
          elif hasWon( revealedBoxes ):
            gameWonAnimation( mainBoard )
            pygame.time.wait( 2000 )

            # Reset
            mainBoard = getRandomizedBoard()
            revealedBoxes = generateRevealedBoxesData( False )

            drawBoard( mainBoard, revealedBoxes )
            pygame.display.update()
            pygame.time.wait( 1000 )

            startGameAnimation( mainBoard )

          firstSelection = None

    # Redraw and tick
    pygame.display.update()
    fpsClock.tick( Config.fps )


##########
# Game functions
##########

# make separate modules for all of these functions (board module, boxes module, etc)
def getRandomizedBoard():
  # Master list of possible icons (color-to-shape)
  icons = []
  for color in Colors:
    for shape in Shapes:
      icons.append(( Shapes[ shape ], Colors[ color ] ))

  # Randomize order of icons
  random.shuffle( icons )
  # Determine number of icons required by board area
  iconsRequired = int(( Opt.boardWidth * Opt.boardHeight ) / 2 )
  # Create two of each used icon
  icons = icons[ :iconsRequired ] * 2
  # Shuffle resulting set of icons
  random.shuffle( icons )

  # Create the board model
  # Iterates through available tiles, column by column,
  #  for each row adds the first available set of icons from the
  #  shuffled duplicate icons list
  board = []
  for x in range( Opt.boardWidth ):
    column = []
    for y in range ( Opt.boardHeight ):
      column.append( icons[0] )
      del icons[0]
    board.append( column )

  return board

def generateRevealedBoxesData( val ):
  revealedBoxes = []
  for i in range( Opt.boardWidth ):
    # [val] * 7: creates an array of val, 7 items long
    revealedBoxes.append( [ val ] * Opt.boardHeight )
  return revealedBoxes

def quitGame( pygame, sys ):
  pygame.quit()
  sys.exit()


# Animation functions
def startGameAnimation( board ):
  # Reveal boxes 8 at a time
  coveredBoxes = generateRevealedBoxesData( False )
  boxes = []
  for x in range( Opt.boardWidth ):
    for y in range( Opt.boardHeight ):
      boxes.append( ( x, y ) )
  random.shuffle( boxes )
  boxGroups = splitIntoGroupsOf( 8, boxes )

  drawBoard( board, coveredBoxes )
  for boxGroup in boxGroups:
    revealBoxesAnimation( board, boxGroup )
    coverBoxesAnimation( board, boxGroup )

def drawBoard( board, revealed ):
  # Draws all boxes
  for boxX in range( Opt.boardWidth ):
    for boxY in range( Opt.boardHeight ):
      left, top = leftTopCoordsOfBox( boxX, boxY )
      if not revealed[boxX][boxY]:
        # Draw covered box
        pygame.draw.rect( displaySurf, Opt.boxColor, ( left, top, Opt.boxSize, Opt.boxSize ))
      else:
        # Draw revealed icon
        shape, color = getShapeAndColor( board, boxX, boxY )
        drawIcon( shape, color, boxX, boxY )

def splitIntoGroupsOf( groupSize, list ):
  # Splits a list into a list of lists
  result = []
  for i in range(0, len( list ), groupSize ):
    result.append( list[ i:i + groupSize ] )
  return result

def leftTopCoordsOfBox( boxX, boxY ):
  # Converts board coords to pixel coords
  left = boxX * ( Opt.boxSize + Opt.gapSize ) + Opt.xMargin
  top  = boxY * ( Opt.boxSize + Opt.gapSize ) + Opt.yMargin
  return ( left, top )

def getBoxAtPixel( x, y ):
  for boxX in range( Opt.boardWidth ):
    for boxY in range( Opt.boardHeight ):
      left, top = leftTopCoordsOfBox( boxX, boxY )
      boxRect = pygame.Rect( left, top, Opt.boxSize, Opt.boxSize )
      if boxRect.collidepoint( x, y ):
        return ( boxX, boxY )
  return ( None, None )

def drawIcon( shape, color, boxX, boxY ):
  # Convenience
  quarter = int( Opt.boxSize * 0.25 )
  half    = int( Opt.boxSize * 0.5)

  left, top = leftTopCoordsOfBox( boxX, boxY )

  # Draw Shapes
  if shape == Shapes['donut']:
    pygame.draw.circle( displaySurf, color, ( left + half, top + half), half - 5 )
    pygame.draw.circle( displaySurf, Opt.bgColor, ( left + half, top + half ), quarter - 5 )

  elif shape == Shapes['square']:
    pygame.draw.rect( displaySurf, color, ( left + quarter, top + quarter, Opt.boxSize - half, Opt.boxSize - half ))

  elif shape == Shapes['diamond']:
    pygame.draw.polygon( displaySurf, color, ( ( left + half, top ), ( left + Opt.boxSize - 1, top + half ), ( left + half, top + Opt.boxSize - 1 ), ( left, top + half ) ))

  elif shape == Shapes['lines']:
    for i in range( 0, Opt.boxSize, 4 ):
      pygame.draw.line( displaySurf, color, ( left, top + i ), ( left + i, top ))
      pygame.draw.line( displaySurf, color, ( left, top + Opt.boxSize - 1 ), ( left + Opt.boxSize - 1, top + i ))

  elif shape == Shapes['oval']:
    pygame.draw.ellipse( displaySurf, color, ( left, top + quarter, Opt.boxSize, half ))

def getShapeAndColor( board, boxX, boxY ):
  # Returns tuple of shape, color from within the board
  return board[boxX][boxY][0], board[boxX][boxY][1]

def drawBoxCovers( board, boxes, coverage ):
  for box in boxes:
    left, top = leftTopCoordsOfBox( box[0], box[1] )
    pygame.draw.rect( displaySurf, Opt.bgColor, ( left, top, Opt.boxSize, Opt.boxSize ))
    shape, color = getShapeAndColor( board, box[0], box[1] )
    drawIcon( shape, color, box[0], box[1] )
    if coverage > 0:
      pygame.draw.rect( displaySurf, Opt.boxColor, ( left, top, coverage, Opt.boxSize ))
    pygame.display.update()
    fpsClock.tick( Config.fps )

def revealBoxesAnimation( board, boxesToReveal ):
  for coverage in range( Opt.boxSize, ( -Opt.revealSpeed ) - 1, -Opt.revealSpeed ):
    drawBoxCovers( board, boxesToReveal, coverage )

def coverBoxesAnimation( board, boxesToCover ):
  for coverage in range( 0, Opt.boxSize + Opt.revealSpeed, Opt.revealSpeed ):
    drawBoxCovers( board, boxesToCover, coverage )

def drawHighlightBox( boxX, boxY ):
  left, top = leftTopCoordsOfBox( boxX, boxY )
  pygame.draw.rect( displaySurf, Opt.highlightColor, ( left - 5, top - 5, Opt.boxSize + 10, Opt.boxSize + 10 ), 4 )

def gameWonAnimation( board ):
  coveredBoxes = generateRevealedBoxesData( True )
  color1 = Opt.bgLightColor
  color2 = Opt.bgColor

  for i in range( 13 ):
    color1, color2 = color2, color1
    displaySurf.fill( color1 )
    drawBoard( board, coveredBoxes )
    pygame.display.update()
    pygame.time.wait( 300 )

def hasWon( revealedBoxes ):
  for i in revealedBoxes:
    if False in i:
      return False
  return True
