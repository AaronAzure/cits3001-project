from agent import Agent
import random

class OurAgent(Agent):        
    '''A sample implementation of a random agent in the game The Resistance'''

    #* if not spy internal state / memory (probability of index agent of being a spy)
    sus_meter = dict()    # int(index) -> float(probability of being a spy)

    #* if spy internal state / memory (how sus we are) how many times we have betrayed
    #   - the more we betray, the less likely we betray again (reduce sus), depends on how close we are to winning
    voted_to_go_on_mission = []
    betrayal_rate = 0.0 # no_missions_failed / rounds_complete

    #? 5 C 2 = 10
    # (1 / number_of_players) %

    #? 2 spies out of 4
    # 0 1 2 3 , 0 = 25% -> 30%   (spies)
    # 0 1 2 3 , 1 = 25% -> 30%   (spies)
    # 0 1 2 3 , 2 = 25% -> 25%  
    # 0 1 2 3 , 3 = 25% -> 15%  


    # 0 1 2 3 4 | 0 = 40% -> 60%  #! (spies)
    # 0 1 2 3 4 | 1 = 10% -> 15%  
    # 0 1 2 3 4 | 2 = 05% -> 00%
    # 0 1 2 3 4 | 3 = 20% -> 10%
    # 0 1 2 3 4 | 4 = 25% -> 35%   #! (spies)

    def __init__(self, name='Rando'):
        '''
        Initialises the agent.
        Nothing to do here.
        '''
        self.name = name

    def new_game(self, number_of_players, player_number, spy_list):
        '''
        initialises the game - informing the agent of the 
        number_of_players    - the player_number (an id number for the agent in the game),
        and a list of agent indexes which are the spies, if the agent is a spy, or empty otherwise
        '''
        self.number_of_players = number_of_players
        self.player_number = player_number
        self.spy_list = spy_list

    def is_spy(self):
        '''
        returns True iff the agent is a spy
        '''
        return self.player_number in self.spy_list

    # |                                      |
    # |  Below is where we need to add code  |
    # V                                      V

    #* Return list of the team that will go on the mission of size @param team_size
    def propose_mission(self, team_size, betrayals_required=1):
        '''
        Expects a team_size list of distinct agents with id between 0 (inclusive) and number_of_players (exclusive)
        to be returned. 
        betrayals_required - are the number of betrayals required for the mission to fail.
        '''
        team = []
        #* Are we spy
        if self.is_spy():
            # pick up to @param betrayals_req
            pass

        while len(team) < team_size:
            agent = random.randrange(team_size)
            if agent not in team:
                team.append(agent)

        #* Are we good
        
        return team        


    def vote(self, mission, proposer):
        '''
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        mission  - is a list of agents to be sent on a mission. 
        proposer - is an int of the index of the player who proposed the mission. (between 0 and number_of_players)
        The function should return True if the vote is for the mission, and False if the vote is against the mission.
        '''
        # how does proposer affect our vote?
        # based on who is going on the mission, our vote is affected based on our internal state

        # return random.random() < agent.memory[index of mission]
        return random.random()<0.5


    def vote_outcome(self, mission, proposer, votes):
        '''
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        mission  - is a list of agents to be sent on a mission. 
        proposer - is an int of the index of the player who proposed the mission. (between 0 and number_of_players)
        votes    - is a dictionary mapping player indexes to Booleans (True if they voted for the mission, False otherwise).
        No return value is required or expected.
        '''
        #* for our own sake
        # Based on votes, if we suspect someone to be a spy - if they accept: what happen? 
        # Based on votes, if we suspect someone to be a spy - if they reject: what happen? 
        pass


    def betray(self, mission, proposer):
        '''
        The agents on the mission are distinct and indexed between 0 and number_of_players, and include this agent.
        mission  - is a list of agents to be sent on a mission. 
        proposer - is an int of the index of the player who proposed the mission. (between 0 and number_of_players)
        The method should return True if this agent chooses to betray the mission, and False otherwise. 
        By default, spies will betray 30% of the time. 
        '''
        # If in mission there is another spy, lower chance of betrarying
        # If the only spy in mission is you, 
        # based on how close we winning (game state) - betrayal rate

        # ignore proposer, does not affect our decision

        # If we betray, the proposer (may or may not be a spy also) and us will be more sus
        if self.is_spy():
            return random.random()<0.3

    # up to 5 missions
    def mission_outcome(self, mission, proposer, betrayals, mission_success):
        '''
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        mission         - is a list of agents to be sent on a mission. 
        proposer        - is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        betrayals       - is the number of people on the mission who betrayed the mission, 
        mission_success - is True if there were not enough betrayals to cause the mission to fail, False otherwise.
        It is not expected or required for this function to return anything.
        '''
        #* for our sake
        # if spy, just pass
        # if good, if there are betrayals => people in mission, increase sus
        # if good, if there are no betrayals => people in mission, less sus
        # if betrayals == len(mission), all agents on that mission are spies

        pass

    # 
    def round_outcome(self, rounds_complete, missions_failed):
        '''
        basic informative function, where the parameters indicate:
        rounds_complete - the number of rounds (0-5) that have been completed
        missions_failed - the number of missions (0-3) that have failed.
        '''
        #* for our own sake
        # ratio betw rounds_complete : missions_failed, how affect us?
        # called from 

        pass
    
    #* Game over - who won
    def game_outcome(self, spies_win, spies):
        '''
        basic informative function, where the parameters indicate:
        spies_win - True iff the spies caused 3+ missions to fail
        spies     - a list of the player indexes for the spies.
        '''
        # LITERALLY do nothing
        pass



