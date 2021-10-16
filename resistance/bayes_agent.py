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
        
        # print()
        # print(" player number is", bcolors.YELLOW + str(player_number), bcolors.RESET)
        # time.sleep(0.25)

        #* Record game state
        self.current_mission = 0
        self.spy_wins = 0
        self.res_wins = 0
        self.n_rejected_votes = 0
        self.n_failed_missions = 0

        # * if not spy internal state / memory (probability of index agent of being a spy)
        # int(index) -> float(probability of being a spy)
        self.sus_meter = {}
        # set the number of spies base on table size
        # generate sus_meter for players, default 0
        spy_chance = float(self.number_of_spies/self.number_of_players)
        for i in self.others:
            self.sus_meter.setdefault(i, spy_chance)

    def is_spy(self):
        '''
        returns True iff the agent is a spy
        '''
        return self.player_number in self.spy_list

    def maybe_last_turn(self):
        '''Return True if only one more round to win/lose, False otherwise.'''
        return (self.spy_wins == 2) or (self.res_wins == 2)

    # * Return list of the team that will go on the mission of size @param team_size
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
        # if self.is_spy():
        #     # Pick up to (@param betrayals_required) to go on the mission
        #     for i in sorted(list(self.spy_list), key=lambda i: self.sus_meter[i])[0:betrayals_required-1]:
        #         if i not in team:
        #             team.append(i)
        #     if len(team) < betrayals_required:
        #         team.append(sorted(list(self.spy_list), key=lambda i: self.sus_meter[i])[
        #                     betrayals_required])
        #     # fill the rest of team with least sus resistance players
        #     for i in sorted([i for i in self.sus_meter.keys() if i not in self.spy_list], key=lambda i: self.sus_meter[i]):
        #         team.append(i)
        #         if len(team) == team_size:
        #             break
        #* Player is resistance
        # else:
        #     count = 0
        #     sus_rank = sorted([i for i in self.sus_meter.keys() if i != self.player_number], key=lambda i: self.sus_meter[i])
        #     while len(team) < team_size:
        #         team.append(sus_rank[count])
        #         count += 1
        return team

    def vote(self, mission, proposer):
        '''
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        mission  - is a list of agents (index) to be sent on a mission. 
        proposer - is an int of the index of the player who proposed the mission. (between 0 and number_of_players)
        The function should return True if the vote is for the mission, and False if the vote is against the mission.
        '''
        return True

    def vote_outcome(self, mission, proposer, votes):
        '''
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        mission  - is a list of agents to be sent on a mission. 
        proposer - is an int of the index of the player who proposed the mission. (between 0 and number_of_players)
        votes    - is a dictionary mapping player indexes to Booleans (True if they voted for the mission, False otherwise).
        No return value is required or expected.
        '''
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
            return spies_count == betrayals_req or self.maybe_last_turn() 

    def mission_outcome(self, mission, proposer, betrayals, mission_success):
        '''
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        mission         - is a list of agents to be sent on a mission. 
        proposer        - is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        betrayals       - is the number of people on the mission who betrayed the mission, 
        mission_success - is True if there were not enough betrayals to cause the mission to fail, False otherwise.
        It is not expected or required for this function to return anything.
        '''
        # n_combinations = factorial(len(mission)) / (factorial(betrayals) * factorial(len(mission) - betrayals))
        # worlds = list(combinations(mission, betrayals))
        # for i in self.others:
        #     for w in worlds:
        #         for agent in w:
        #             prob_b = self.sus_meter[agent]
        #     self.sus_meter[i] = self.sus_meter[i]
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
        # print()
        if spies_win and self.is_spy():
            # print(bcolors.GREEN, bcolors.UNDERLINE, "You WON!", bcolors.RESET)
            self.times_won += 1
        elif not spies_win and self.is_spy():
            pass
            # print(bcolors.GREEN, bcolors.UNDERLINE, "You LOST!", bcolors.RESET)
        elif spies_win and not self.is_spy():
            pass
            # print(bcolors.GREEN, bcolors.UNDERLINE, "You LOST!", bcolors.RESET)
        elif not spies_win and not self.is_spy():
            # print(bcolors.GREEN, bcolors.UNDERLINE, "You WON!", bcolors.RESET)
            self.times_won += 1
        # print()
        self.n_games += 1
        if (self.n_games >= 10000):
            print(bcolors.GREEN, "{:.2f}%".format(self.times_won / self.n_games * 100), "({})".format(self.n_games), bcolors.RESET)
        # time.sleep(1)
        pass
