from our_agent import OurAgent   # Our project agent
from random_agent import RandomAgent
from garboA import garboa
from garboA import garboa
from game import Game

agents = [
    garboa(name='r0'),
    RandomAgent(name='r1'),
    RandomAgent(name='r2'),
    RandomAgent(name='r3'),
    RandomAgent(name='r4'),
    RandomAgent(name='r5'),
    RandomAgent(name='r6')
]

# for i in range(1):
for i in range(10000):
    game = Game(agents)
    game.play()
print(game)
