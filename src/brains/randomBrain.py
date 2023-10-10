'''
This basic opponent places its army at random, and also select moves randomly.
'''

import sys
sys.path.append('..')

# (CDLTLL) import Brain

from src.brains.Brain import Brain as baseBrain
# from .Brain import Brain as baseBrain
# from brains.Brain import Brain as baseBrain

from random import shuffle, choice

from src.constants import BOARD_WIDTH

# BOARD_WIDTH_LOCAL = BOARD_WIDTH

print('Executing randomBrain.py')

print('BOARD_WIDTH: ', BOARD_WIDTH)

# (CDLTLL) class Brain(Brain.Brain):
class Brain(baseBrain):
    def __init__(self, game, army, boardwidth=None):
        print('Initializing Brain at contructor')
        self.army = army
        self.game = game

        global BOARD_WIDTH
        if boardwidth: BOARD_WIDTH = boardwidth

    def placeArmy(self, armyHeight):
        print('Begining of placeArmy')
        positions = []

        if self.army.color == "Blue":
            rows = range(armyHeight)
        else:
            # (CDLTLL
            # rows = range(BOARD_WIDTH - armyHeight, BOARD_WIDTH)
            rows = range(int(BOARD_WIDTH - armyHeight), int(BOARD_WIDTH))

        for row in rows:
            for column in range(BOARD_WIDTH):
                if self.army.getUnit(column, row) == None:
                    positions += [(column, row)]

        print('Before shuffle')
        shuffle(positions)
        print('After shuffle')

        for unit in self.army.army:
            if unit.isOffBoard():
                if positions:
                    unit.position = positions.pop()

    def findMove(self):
        move = None

        # (CDLTLL)
        # order = range(len(self.army.army))
        # shuffle(order)

        order = list(range(len(self.army.army)))
        shuffle(order)        

        for i in order:
            if move: break

            unit = self.army.army[i]
            if not unit.canMove or not unit.alive:
                continue

            (col, row) = unit.getPosition()

            if unit.walkFar:
                # (CDLTLL) convert to List so we can shuffle
                dist = list(range(1, BOARD_WIDTH))
                shuffle(dist)
            else:
                dist = [1]

            directions = []

            for d in dist:

                north = (col, row - d)
                south = (col, row + d)
                west = (col - d, row)
                east = (col + d, row)

                nw = (col - d, row - d)
                sw = (col - d, row + d)
                ne = (col + d, row - d)
                se = (col + d, row + d)

                directions += [direction for direction in [north, south, west, east] if
                              direction[0] >= 0 and direction[0] < BOARD_WIDTH and
                              direction[1] >= 0 and direction[1] < BOARD_WIDTH and
                              not self.army.getUnit(direction[0], direction[1]) and
                              self.game.legalMove(unit, direction[0], direction[1])]

                if self.game.diagonal:
                    directions += [direction for direction in [nw, sw, ne, se] if
                              direction[0] >= 0 and direction[0] < BOARD_WIDTH and
                              direction[1] >= 0 and direction[1] < BOARD_WIDTH and
                              not self.army.getUnit(direction[0], direction[1]) and
                              self.game.legalMove(unit, direction[0], direction[1])]

            if len(directions) >= 1:
                move = choice(directions)
                return ((col, row), move)

        return (None, None) # no legal move - lost!

    def observe(self, armies):
        pass