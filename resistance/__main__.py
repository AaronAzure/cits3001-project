from os import getloadavg
from typing import Mapping
from our_agent import OurAgent   # Our project agent
from random_agent import RandomAgent

from garboA import garboa
from pandsBot import pandsbot
from bayes_agent import BayesAgent
from game import Game
from ModelBasedAgent import MAgent

import time
from bcolors import bcolors

from tester import GAMES

#run your code

agents = [
    garboa(name='spy0'),    #? spies
    garboa(name='spy1'),    #? spies
    garboa(name='spy2'),    #? spies
    pandsbot(name='r3'),
    pandsbot(name='r4'),
    pandsbot(name='r5'),
    # garboa(name='r6'),
    pandsbot(name='r7')

    # BayesAgent(name='spy0'),    #? spies
    # BayesAgent(name='spy1'),    #? spies
    # BayesAgent(name='spy2'),    #? spies
    # garboa(name='r3'),
    # garboa(name='r4'),
    # garboa(name='r5'),
    # garboa(name='r6')

    # garboa(name='spy0'),    #? spies
    # garboa(name='spy1'),    #? spies
    # garboa(name='spy2'),    #? spies
    # BayesAgent(name='r3'),
    # BayesAgent(name='r4'),
    # BayesAgent(name='r5'),
    # BayesAgent(name='r6')
]

time_start = time.time()
for i in range(GAMES):
    # if i % (50) == 0:
    #     print("Game",i)
    game = Game(agents)
    game.play()
time_elapsed = (time.time() - time_start)
print(bcolors.YELLOW, "{:.4f} sec".format(time_elapsed), bcolors.RESET)
print(game)
