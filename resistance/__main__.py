from our_agent import OurAgent   # Our project agent
from random_agent import RandomAgent
from garboA import garboa
from pandsBot import pandsbot
from game import Game

import time
from bcolors import bcolors

from tester import GAMES

#run your code

agents = [
    garboa(name='r1'),
    pandsbot(name='r0'),
    pandsbot(name='r2'),
    pandsbot(name='r3'),
    pandsbot(name='r4'),
    pandsbot(name='r5'),
    pandsbot(name='r6')
]

time_start = time.time()
for i in range(GAMES):
    if i % 10 == 0:
        print("Game",i)
    game = Game(agents)
    game.play()
time_elapsed = (time.time() - time_start)
print(bcolors.YELLOW, "{:.4f} sec".format(time_elapsed), bcolors.RESET)
print(game)
