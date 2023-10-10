'''
This opponent randomly chooses from one of the better brains, so that the player doesn't know 
beforehand what they're up against.
'''

# (CDLTLL) import Brain
# (CDLTLL) import CarefulBrain
# (CDLTLL) import SmartBrain

from brains.Brain import Brain as baseBrain
from brains.CarefulBrain import Brain as carefulBrain
from brains.SmartBrain import Brain as smartBrain

from random import choice

BRAINS = [carefulBrain, smartBrain]

class Brain(baseBrain):
    def __init__(self, game, army, boardwidth=None):
        self.actualBrain = choice(BRAINS).Brain(game, army, boardwidth)
        # print self.actualBrain

    def placeArmy(self, armyHeight):
        return self.actualBrain.placeArmy(armyHeight)

    def findMove(self):
        return self.actualBrain.findMove()
