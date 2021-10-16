from our_agent import OurAgent   # Our project agent
from random_agent import RandomAgent
from game import Game


from garboA import garboa
from greedy_agent import GreedyAgent

agents = [
    garboa(name='smart alec'),
    GreedyAgent(name='g1'),
    GreedyAgent(name='g2'),
    GreedyAgent(name='g3'),
    GreedyAgent(name='g4'),
    GreedyAgent(name='g5'),
    GreedyAgent(name='g6')
]

game = Game(agents)
game.play()
print(game)
