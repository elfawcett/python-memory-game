##########
# Memory game
##########

# Game module
from Game import *

# Check for valid config & options
assert ( Opt.boardWidth * Opt.boardHeight ) % 2 == 0, 'Board needs even number of boxes'
assert ( len( Colors ) * len( Shapes ) * 2 ) >= ( Opt.boardWidth * Opt.boardHeight ), 'Not enough colors & shapes for board'

# Main loop
main()