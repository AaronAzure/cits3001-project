"""
@name: OurAgent
@author: Aaron Wee (22702446) and Alex Mai (22638901)
@about: CITS3001 project 2021 - resistanceAI
"""

from agent import Agent
import random

from bcolors import bcolors


class garboa(Agent):
    '''A sample implementation of a random agent in the game The Resistance'''

    times_won = 0
    n_games = 0

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
        self.players = [i for i in range(number_of_players)]

        #* Record game state
        self.current_mission = 0
        self.n_rejected_votes = 0
        self.n_failed_missions = 0

        # set the number of spies base on table size
        self.number_of_spies = Agent.spy_count.get(number_of_players)

        #* if not spy internal state / memory (probability of index agent of being a spy)
        # int(index) -> float(probability of being a spy)
        self.sus_meter = {}
        # generate sus_meter for players, default suspicious level 0
        for i in self.players:
            self.sus_meter.setdefault(i, 0)

    def is_spy(self):
        '''
        returns True iff the agent is a spy
        '''
        return self.player_number in self.spy_list


    #* Return list of the team that will go on the mission of size @param team_size
    def propose_mission(self, team_size, betrayals_required=1):
        '''
        Expects a team_size list of distinct agents with id between 0 (inclusive) and number_of_players (exclusive)
        to be returned. 
        betrayals_required - are the number of betrayals required for the mission to fail.
        '''
        team = []
        #* Player is a spy
        if self.is_spy():
            #* Pick up to (@param betrayals_required) to go on the mission

            #* add ourselves and choose least sus spies up to @param betrayals_required
            team.append(self.player_number)
            for i in sorted(list(self.spy_list), key=lambda i: self.sus_meter[i])[0:betrayals_required-1]:
                if i not in team:
                    team.append(i)
            # if len(team) < betrayals_required:
            #     print(sorted(list(self.spy_list), key=lambda i: self.sus_meter[i]))
            #     team.append(sorted(list(self.spy_list), key=lambda i: self.sus_meter[i])[betrayals_required])

            #* fill the rest of team with least sus resistance players
            for i in sorted([i for i in self.sus_meter.keys() if i not in self.spy_list], key=lambda i: self.sus_meter[i]):
                team.append(i)
                if len(team) == team_size:
                    break
        #* Player is resistance
        else:
            #* add ourselves and least sus agent{s}
            team.append(self.player_number)
            
            #* sort the sus_meter in ascending order
            sus_rank = sorted([i for i in self.sus_meter.keys() if i != self.player_number], key=lambda i: self.sus_meter[i])
            count = 0
            while len(team) < team_size:
                team.append(sus_rank[count])
                count += 1
        return team

    def vote(self, mission, proposer):
        '''
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        mission  - is a list of agents (index) to be sent on a mission. 
        proposer - is an int of the index of the player who proposed the mission. (between 0 and number_of_players)
        The function should return True if the vote is for the mission, and False if the vote is against the mission.
        '''
        #* Always vote yes on the first mission, regardless if resistance or spy
        if self.current_mission == 0:
            return True

        #* Always vote yes on the fifth vote, regardless if resistance or spy
        if self.n_rejected_votes >= 4:
            return True

        sus_rank = sorted([i for i in self.sus_meter.keys()], key=lambda i: self.sus_meter[i], reverse=True)
        if self.player_number in sus_rank:
            sus_rank.remove(self.player_number)

        #* Player is resistance
        if not self.is_spy():
            #* vote AGAINST if there are guaranteed spy in the proposed team
            if (self.number_of_players - self.number_of_spies == len(mission)):
                if self.player_number not in mission:
                    return False

            #* vote AGAINST if there is someone in the top sus list
            for i in range(self.number_of_spies):
                if sus_rank[i] in mission:
                    return False

            #* vote AGAINST if there are guaranteed spy in the proposed team
            if self.spy_list in mission:
                return False

            #* if we are not in the mission, then depending on the current mission, vote against
            if self.player_number not in mission:
            # if self.player_number not in mission and (random.Random() < (0.1 * (self.current_mission+1))):
                return False
            return True
        #* Player is a spy
        else:
            spies_in = 0
            betrayals_req = Agent.fails_required[self.number_of_players][self.current_mission]

            #* vote AGAINST, if there is not enough spies to betray
            for i in mission:
                if i in self.spy_list:
                    spies_in += 1

            #* Vote for if there are enough spies to successfully sabotage
            return (spies_in >= betrayals_req)

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

        #* assume all who rejected the fifth vote are spies (playing optimally)
        if not self.is_spy():
            if self.n_rejected_votes >= 5:
                for agent in votes:
                    self.spy_list.append(agent)

        #* if someone vote AGAINST in the first mission
        if self.current_mission == 0:
            for agent in range(self.number_of_players):
                if agent not in votes:
                    self.sus_meter[agent] += 20

        #* if it is not the first mission
        if self.current_mission > 0 and self.n_rejected_votes < 5:
            #* When there is a spy NOT in the team, voting AGAINST the team, let's assume there are no spies on the team
            if len(list(filter(lambda agent: self.sus_meter[agent] >= 700 and agent not in mission and agent not in votes, self.players))) > 0:
                for i in mission:
                    self.sus_meter[i] -= 450
            mission_filtered = list(filter(lambda i: self.sus_meter[i] < 700, mission))

            #* if we are not in the mission with the specific mission length, the team is guaranteed to contain spies (as what a resistance will think)
            if self.player_number not in mission and len(mission) == self.number_of_players - self.number_of_spies:
                #* anyone not in the mission and vote FOR is sus (as spy wants the mission team to include spies)
                not_mission_voted_true = [i for i in self.players if i not in mission and i in votes]

                if len(mission_filtered) < self.number_of_players - self.number_of_spies:
                    for agent in not_mission_voted_true:
                        self.sus_meter[agent] += 400
                    return
                for agent in not_mission_voted_true:
                    self.sus_meter[agent] += 300
        self.last_votes = votes

    def betray(self, mission, proposer):
        '''
        The agents on the mission are distinct and indexed between 0 and number_of_players, and include this agent.
        mission  - is a list of agents to be sent on a mission. 
        proposer - is an int of the index of the player who proposed the mission. (between 0 and number_of_players)
        The method should return True if this agent chooses to betray the mission, and False otherwise. 
        By default, spies will betray 30% of the time. 
        '''
        #* reduce the betrayal rate if there are many spies in the mission
        if self.is_spy():
            #* Reduce the betrayal rate if there are many spies in the mission
            spies_count = 0
            for agent in mission:
                if agent in self.spy_list:
                    spies_count += 1
            betrayals_req = Agent.fails_required[self.number_of_players][self.current_mission]

            #* If there are more spies than the required number of betrayals
            if spies_count > betrayals_req:
                #* Less likely to betray
                return random.random() < (betrayals_req/spies_count)

            #* If the required number of betrayals is equal to number of spies in the mission
            elif spies_count == betrayals_req:
                #* 100% betray
                return True

            #* If the required number of betrayals is more than to number of spies in the mission,
            #* then it is pointless to betray, and try to blend in
            return False
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
        #* fact resistance = -1000
        #* fact spy = 1000
        # sus ~ 150
        self.n_rejected_votes = 0   # Reset number of reject votes for next mission
        if not mission_success:
            self.n_failed_missions += 1
        #* for our sake
        self.current_mission += 1
        not_in_mission = [p for p in self.players if p not in mission]
        if betrayals > 0:
            not_betrayed = len(mission) - betrayals

            #* not involved in mission or playing as spy
            if self.player_number not in mission or self.is_spy():
                if not_betrayed == 0:
                    for agent in mission:
                        self.sus_meter[agent] += 1000
                        if not self.is_spy():
                            self.spy_list.append(agent)
                    for agent in not_in_mission:
                        self.sus_meter[agent] -= (1000 * betrayals) / len(not_in_mission)

                elif betrayals == self.number_of_spies and not_betrayed > 0:
                    for agent in mission:
                        self.sus_meter[agent] += 150
                    for agent in not_in_mission:
                        self.sus_meter[agent] -= 1000

                elif betrayals != self.number_of_spies and not_betrayed > 0:
                    total_n_people_on_mission = 5
                    for agent in mission:
                        self.sus_meter[agent] += (25 * (total_n_people_on_mission - not_betrayed))
                    for agent in not_in_mission:
                        self.sus_meter[agent] -= (25 * (total_n_people_on_mission - not_betrayed))

            #* playing as resistance and involved in mission
            elif self.player_number in mission and not self.is_spy():
                if betrayals == len(mission) - 1:
                    for agent in [p for p in mission if not p == self.player_number]:
                        self.sus_meter[agent] += 1000
                        if not self.is_spy():
                            self.spy_list.append(agent)
                    self.sus_meter[self.player_number] += 100
                    if betrayals == self.number_of_spies:
                        for agent in not_in_mission:
                            self.sus_meter[agent] -= 1000
                    else:
                        for agent in not_in_mission:
                            self.sus_meter[agent] -= 100

            if not self.is_spy():
                if self.current_mission > 0 and self.current_mission != 3:
                    self.sus_meter[proposer] += 50
                    for p in filter(lambda i: i != proposer, self.last_votes):
                        self.sus_meter[p] += 25
                
                #* Mission 4 that usually require 2 betrayals
                if self.current_mission == 3 and not mission_success:
                    for i in [i for i in self.last_votes if i not in mission]:
                        self.sus_meter[i] += 700
        else:
            for agent in mission:
                self.sus_meter[agent] -= 25

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
