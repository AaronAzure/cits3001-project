from our_agent import OurAgent   # Our project agent
from random_agent import RandomAgent
from garboA import garboa
from pandsBot import pandsbot
from game import Game

import time
from bcolors import bcolors

#run your code

agents = [
    pandsbot(name='r0'),
    RandomAgent(name='r1'),
    RandomAgent(name='r2'),
    RandomAgent(name='r3'),
    RandomAgent(name='r4'),
    RandomAgent(name='r5'),
    RandomAgent(name='r6')
]

time_start = time.time()
for i in range(1000):
    # if i % 10 == 0:
    #     print("Game", i)
    game = Game(agents)
    game.play()
time_elapsed = (time.time() - time_start)
print(bcolors.YELLOW, "{:.4f} sec".format(time_elapsed), bcolors.RESET)
print(game)
