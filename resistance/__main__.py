# from our_agent import RandomAgent   # Our project agent
from random_agent import RandomAgent
from game import Game

agents = [
    OurAgent(name='r0'),
    RandomAgent(name='r1'),
    RandomAgent(name='r2'),
    RandomAgent(name='r3'),
    RandomAgent(name='r4'),
    RandomAgent(name='r5'),
    RandomAgent(name='r6')
]

game = Game(agents)
game.play()
print(game)
