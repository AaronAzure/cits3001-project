from agent import Agent
import random

class PandsBot(Agent):        
    '''A sample implementation of a random agent in the game The Resistance'''

    def __init__(self, name='Rando'):
        '''
        Initialises the agent.
        Nothing to do here.
        '''
        self.name = name

    def new_game(self, number_of_players, player_number, spy_list):
        '''
        initialises the game, informing the agent of the 
        number_of_players, the player_number (an id number for the agent in the game),
        and a list of agent indexes which are the spies, if the agent is a spy, or empty otherwise
        '''
        self.number_of_players = number_of_players
        self.player_number = player_number
        self.spy_list = spy_list

        self.spy_list = spy_list
        self.players = [i for i in range(number_of_players)]
        
        self.current_mission = 0
        self.spy_wins = 0
        self.res_wins = 0
        # set the number of spies base on table size
        self.number_of_spies = Agent.spy_count.get(number_of_players)
        if self.number_of_spies == 2:
            self.friends = [[Probability(self.number_of_spies/number_of_players) for x in range(number_of_players)] for y in range(number_of_players)]
            self.SuspectTeams = [[(x,y),0] for x in range(number_of_players) for y in range(number_of_players) if x < y]
        elif self.number_of_spies == 3:
            self.friends = [[Probability(self.number_of_spies/number_of_players) for x in range(number_of_players)] for y in range(number_of_players)]
            self.SuspectTeams = [[(x,y,z),0] for x in range(number_of_players) for y in range(number_of_players) for z in range(number_of_players) if x < y < z]
        else:
            self.friends = [[Probability(self.number_of_spies/number_of_players) for x in range(number_of_players)] for y in range(number_of_players)]
            self.suspectsTeam = [[(x,y,z,t),0] for x in range(number_of_players) for y in range(number_of_players) for z in range(number_of_players) for t in range(number_of_players) if x < y < z < t]
        print("friend lists are", self.friends)
        print("Suspect teams are", self.SuspectTeams)

    def is_spy(self):
        '''
        returns True iff the agent is a spy
        '''
        return self.player_number in self.spy_list

    def maybe_last_turn(self):
        '''1 more round to win/lose?'''
        return (self.spy_wins == 2) or (self.res_wins == 2)

    # def _getBadPair(self):
    #     #get the most suspicious pair
    #     tmp = [x for x in self.SuspectTeams if self.player_number not in x[0]]
    #     result = max(tmp, key=lambda p: (random.uniform(0.9, 1.0))*p[1])
    #     #result = tmp
    #     if result[0] > 0:#random.uniform(0, 0.5):-------------------------------------------
    #         return result[0],result[1]
    #     else:
    #         return []

    def propose_mission(self, team_size, betrayals_required = 1):
        '''
        expects a team_size list of distinct agents with id between 0 (inclusive) and number_of_players (exclusive)
        to be returned. 
        betrayals_required are the number of betrayals required for the mission to fail.
        '''
        team = []
        # always include myself
        team.append(self.player_number)


        return team        

    def vote(self, mission, proposer):
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        The function should return True if the vote is for the mission, and False if the vote is against the mission.
        '''
        return random.random()<0.5

    def vote_outcome(self, mission, proposer, votes):
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        votes is a dictionary mapping player indexes to Booleans (True if they voted for the mission, False otherwise).
        No return value is required or expected.
        '''
        #nothing to do here
        pass

    def betray(self, mission, proposer):
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players, and include this agent.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        The method should return True if this agent chooses to betray the mission, and False otherwise. 
        By default, spies will betray 30% of the time. 
        '''
        if self.is_spy():
            #* Reduce the betrayal rate if there are many spies in the mission
            spies_count = len([p for p in mission if p in self.spy_list])
            betrayals_req = Agent.fails_required[self.number_of_players][self.current_mission]

            #* If there are more spies than the required number of betrayals
            if spies_count > betrayals_req:
                #* Less likely to betray
                return random.random() < (betrayals_req/spies_count)

            #* If the required number of betrayals is equal to number of spies in the mission
            return spies_count == betrayals_req or self.maybe_last_turn() 

    def mission_outcome(self, mission, proposer, betrayals, mission_success):
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        betrayals is the number of people on the mission who betrayed the mission, 
        and mission_success is True if there were not enough betrayals to cause the mission to fail, False otherwise.
        It iss not expected or required for this function to return anything.
        '''
        #nothing to do here
        pass

    def round_outcome(self, rounds_complete, missions_failed):
        '''
        basic informative function, where the parameters indicate:
        rounds_complete, the number of rounds (0-5) that have been completed
        missions_failed, the numbe of missions (0-3) that have failed.
        '''
        #nothing to do here
        pass
    
    def game_outcome(self, spies_win, spies):
        '''
        basic informative function, where the parameters indicate:
        spies_win, True iff the spies caused 3+ missions to fail
        spies, a list of the player indexes for the spies.
        '''
        #nothing to do here
        pass

# class for initialize and update probability
class Probability(object):
    def __init__(self, v0):
        self.value = v0
        self.n = 0

    def sample(self, value):
        self.sampleExt(value, 1)

    def sampleExt(self, value, n):
        self.value = 1 - (1 - self.value)*(1 - float(value) / float(n))
        self.n += n
        
    def sampleExtNeg(self, value, n):
        self.value *= (1- float(value) / float(n))

    def estimate(self):
        return self.value

    def __repr__(self):
        #return "%0.2f%% (%i)" % (100.0 * float(self.value), self.n)
        return "%0.2f%% " % (100.0 * float(self.value))

