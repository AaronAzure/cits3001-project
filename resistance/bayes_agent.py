"""
@name: OurAgent
@author: Aaron Wee (22702446) and Alex Mai (22638901)
@about: CITS3001 project 2021 - resistanceAI
"""

from agent import Agent
from math import factorial
from itertools import combinations
import random

# ! DELETE
from bcolors import bcolors
from tester import GAMES    #! DELETE
import time


class BayesAgent(Agent):
    '''An agent which utilise the Bayesian Analysis in the game The Resistance'''
    
    times_won = 0
    n_games = 0

    def __init__(self, name='Bayes'):
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
        self.players = [i for i in range(number_of_players)]
        self.others = [i for i in range(number_of_players) if i != self.player_number]
        self.number_of_spies = Agent.spy_count.get(number_of_players)

        #* Record game state
        self.current_mission = 0
        self.spy_wins = 0
        self.res_wins = 0
        self.n_rejected_votes = 0
        self.n_failed_missions = 0

        #* any team of this length without us(resistance) is guaranteed at least 1 spy
        self.number_of_non_spies = number_of_players - self.number_of_spies

        # * if not spy internal state / memory (probability of index agent of being a spy)
        # int(index) -> float(probability of being a spy)
        self.sus_meter = {}
        # set the number of spies base on table size
        # generate sus_meter for players, default 0
        # worlds = list(combinations(self.others, 2))
        # world_spy_chance = float(1/self.len(worlds))
        initial_sus = (self.number_of_spies)/(self.number_of_players)
        for i in self.others:
            self.sus_meter.setdefault(i, initial_sus)
        
        # spy_chance = float(self.number_of_spies/self.number_of_players)
        # for i in self.others:
        #     self.sus_meter.setdefault(i, spy_chance)

    def is_spy(self):
        '''
        returns True iff the agent is a spy
        '''
        return self.player_number in self.spy_list

    def maybe_last_turn(self):
        '''Return True if only one more round to win/lose, False otherwise.'''
        return (self.spy_wins == 2) or (self.res_wins == 2)


    def bayes_anaylsis(self, group, sus_action_weight, sus_factor):
        prob_action = []
        prob_of_betray = sus_action_weight
        for i in self.others:
            spy_chance = sus_factor
            if i in group:
                prob = prob_of_betray
                prob *= spy_chance
            else:
                prob = 1 - prob_of_betray
                prob *= (1 - spy_chance)
            
            prob_action.append(self.sus_meter.get(i) * prob)

        # print(prob_action)
        for i in range(len(self.others)):
            self.sus_meter[self.others[i]] = (prob_action[i] / sum(prob_action)) * self.number_of_spies


    #* Return list of the team that will go on the mission of size @param team_size
    def propose_mission(self, team_size, betrayals_required=1):
        '''
        Expects a team_size list of distinct agents with id between 0 (inclusive) and number_of_players (exclusive)
        to be returned. 
        betrayals_required - are the number of betrayals required for the mission to fail.
        '''
        team = []
        # Always include ourselves
        team.append(self.player_number)

        #* Player is a spy
        if self.is_spy():
            least_sus = sorted(self.sus_meter, key=self.sus_meter.get)

            # Pick up to (@param betrayals_required) to go on the mission
            for i in least_sus:
                if i in self.spy_list and i not in team:
                    team.append(i)
                if len(team) >= team_size:
                    break

            # fill the rest of team with least sus resistance players
            for i in least_sus:
                if i not in team:
                    team.append(i)
                if len(team) >= team_size:
                    break
        #* Player is resistance
        else:
            least_sus = sorted(self.sus_meter, key=self.sus_meter.get)

            while len(team) < team_size:
                agent = least_sus.pop(0)
                team.append(agent)

        return team

    def vote(self, mission, proposer):
        '''
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        mission  - is a list of agents (index) to be sent on a mission. 
        proposer - is an int of the index of the player who proposed the mission. (between 0 and number_of_players)
        The function should return True if the vote is for the mission, and False if the vote is against the mission.
        '''
        #* Always vote FOR your selected team
        if proposer == self.player_number:
            return True

        #* Always vote yes on the first mission, regardless if resistance or spy
        if self.current_mission == 0:
            return True

        #* Always vote yes on the fifth vote, regardless if resistance or spy
        if self.n_rejected_votes >= 4:
            return True

        #* As a spy, vote for all missions that include enough spy to sabotage the mission!
        if self.is_spy():
            spies_count = len([i for i in mission if i in self.spy_list])
            betrayals_req = Agent.fails_required[self.number_of_players][self.current_mission]

            return spies_count >= betrayals_req

        #* If I'm not on the team and the team is equal to the number of actual resistance members
        if len(mission) == self.number_of_non_spies and self.player_number not in mission:
            return False

        most_sus = 0
        most_sus_agent = 0
        least_sus = 1
        for agent, sus_score in self.sus_meter.items():
            if sus_score > most_sus:
                most_sus = sus_score
                most_sus_agent = agent
            if sus_score < least_sus:
                least_sus = sus_score
                
        return most_sus_agent not in mission

    def vote_outcome(self, mission, proposer, votes):
        '''
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        mission  - is a list of agents to be sent on a mission. 
        proposer - is an int of the index of the player who proposed the mission. (between 0 and number_of_players)
        votes    - is a dictionary mapping player indexes to Booleans (True if they voted for the mission, False otherwise).
        No return value is required or expected.
        '''
        #* Did the team get rejected?
        n_approved = len(votes)
        #* Not majority vote, increment number of rejected votes
        if 2*n_approved <= self.number_of_players:
            self.n_rejected_votes += 1

        not_in_mission = [i for i in self.others if i not in mission]
        voted_against = [i for i in self.others if i not in votes]

        #* Increase sus value if leader did not choose themself
        if proposer not in mission:
            self.bayes_anaylsis([proposer], 0.55, 0.55)

        #* Increase sus value for those that voted AGAINST the first mission
        if self.current_mission == 0 and self.n_rejected_votes == 0 and len(voted_against) > 0:
            self.bayes_anaylsis(voted_against, 0.55, 0.55)

        #* Increase sus value for those that voted AGAINST on the fifth vote
        if self.n_rejected_votes == 4 and len(voted_against) > 0:
            self.bayes_anaylsis(voted_against, 0.8, 0.8)

        #* Increase sus value for those out of team of suslength, but voted FOR
        less_sus_agents = [i for i in votes if len(mission) == self.number_of_non_spies and i not in mission and i != self.player_number]
        if len(less_sus_agents) > 0: 
            self.bayes_anaylsis(less_sus_agents, 0.2, 0.2)
        
        pass

    def betray(self, mission, proposer):
        '''
        The agents on the mission are distinct and indexed between 0 and number_of_players, and include this agent.
        mission  - is a list of agents to be sent on a mission. 
        proposer - is an int of the index of the player who proposed the mission. (between 0 and number_of_players)
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
            return (spies_count == betrayals_req) or self.maybe_last_turn() 

    def mission_outcome(self, mission, proposer, betrayals, mission_success):
        '''
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        mission         - is a list of agents to be sent on a mission. 
        proposer        - is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        betrayals       - is the number of people on the mission who betrayed the mission, 
        mission_success - is True if there were not enough betrayals to cause the mission to fail, False otherwise.
        It is not expected or required for this function to return anything.
        '''
        #* Record the mission status
        if mission_success:
            self.res_wins += 1
        else:
            self.spy_wins += 1

        self.n_rejected_votes = 0   # Reset number of reject votes for next mission

        # self.bayes_anaylsis(mission, 0.8, max((betrayals/len(mission)), 0.1))
        prob_action = []
        prob_of_betray = 0.8
        for i in self.others:
            spy_chance = max((betrayals/len(mission)), 0.1)
            if i in mission:
                prob_action_given_is_spy = prob_of_betray
                prob_action_given_is_spy *= spy_chance
                # print("--", "{:.2f}".format(prob_of_betray), i, spy_chance)
            else:
                prob_action_given_is_spy = (1 - prob_of_betray)
                prob_action_given_is_spy *= (1 - spy_chance)
            #     print("--", "{:.2f}".format(1 - prob_of_betray), i, (1 - spy_chance))
            # print(self.sus_meter.get(i), i, prob_action_given_is_spy)
            prob_action.append(self.sus_meter.get(i) * prob_action_given_is_spy)

        # print([ '%.2f' % elem for elem in prob_action ])
        # print(sum(prob_action))
        for i in range(len(self.others)):
            self.sus_meter[self.others[i]] = (prob_action[i] / sum(prob_action)) * self.number_of_spies
        
        self.current_mission += 1
        pass

    def round_outcome(self, rounds_complete, missions_failed):
        '''
        basic informative function, where the parameters indicate:
        rounds_complete - the number of rounds (0-5) that have been completed
        missions_failed - the number of missions (0-3) that have failed.
        '''
        pass

    # * Game over - who won
    def game_outcome(self, spies_win, spies):
        '''
        basic informative function, where the parameters indicate:
        spies_win - True iff the spies caused 3+ missions to fail
        spies     - a list of the player indexes for the spies.
        '''
        if not spies_win and self.is_spy():
            self.times_won += 1
        elif spies_win and self.is_spy():
            pass
        elif not spies_win and not self.is_spy():
            pass
        elif spies_win and not self.is_spy():
            self.times_won += 1
        
        self.n_games += 1
        
        if (self.n_games >= GAMES):
            print(bcolors.GREEN, "Bayes_ind = {:.2f}%".format(self.times_won / self.n_games * 100), "({})".format(self.n_games), bcolors.RESET)
        
        pass
