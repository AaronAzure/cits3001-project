"""
@name: OurAgent
@author: Aaron Wee (22702446) and Alex Mai (22638901)
@about: CITS3001 project 2021 - resistanceAI
"""

from agent import Agent
import random


class OurAgent(Agent):
    '''A sample implementation of a random agent in the game The Resistance'''

    # * if spy internal state / memory (how sus we are) how many times we have betrayed

    #   - the more we betray, the less likely we betray again (reduce sus), depends on how close we are to winning
    # voted_to_go_on_mission = []
    # betrayal_rate = 0.0  # no_missions_failed / rounds_complete
    number_of_spies = 0
    current_mission = 0   # Current

    n_rejected_votes = 0
    n_failed_missions = 0

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

        # Reset
        self.current_mission = 0
        self.n_rejected_votes = 0
        self.n_failed_missions = 0

        #* if not spy internal state / memory (probability of index agent of being a spy)
        self.sus_meter = dict()    # int(index) -> float(probability of being a spy)

        self.number_of_spies = 0
        self.current_mission = 0

        # set the number of spies base on table size
        self.number_of_spies = Agent.spy_count.get(number_of_players)
        self.total_prob = self.number_of_spies * 1.0

        # Create probability chart for
        # if not self.is_spy():
        for i in range(number_of_players):
            # Do not include oneself as probability of being a spy
            if i == self.player_number:
                continue
            self.sus_meter.setdefault(
                i, (1.0 * self.number_of_spies) / (number_of_players - 1))


    def is_spy(self):   #! DONE
        '''
        returns True iff the agent is a spy
        '''
        return self.player_number in self.spy_list


    # * Return list of the team that will go on the mission of size @param team_size
    def propose_mission(self, team_size, betrayals_required=1):
        '''
        Expects a team_size list of distinct agents with id between 0 (inclusive) and number_of_players (exclusive)
        to be returned. 
        betrayals_required - are the number of betrayals required for the mission to fail.
        '''
        team = []
        # * Are we spy
        if self.is_spy():
            # pick up to @param betrayals_req
            team.append(self.player_number)
            betrayals_required -= 1
            while betrayals_required > 0:
                pick = random.choice(self.spy_list)                 #! NOT RANDOM -> choose less sus
                if pick not in team:
                    team.append(pick)
                    betrayals_required -= 1

            while len(team) < team_size:
                agent = random.randrange(self.number_of_players)    #! NOT RANDOM -> choose less sus
                if agent not in team and agent not in self.spy_list:
                    team.append(agent)
        else:
            team.append(self.player_number)
            while len(team) < team_size:
                agent = random.randrange(self.number_of_players)    #! NOT RANDOM -> choose less sus
                # choose a random agent that is not in the spy list
                if agent not in team and agent not in self.spy_list:
                    team.append(agent)
        return team

    def vote(self, mission, proposer):  #! DONE
        '''
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        mission  - is a list of agents (index) to be sent on a mission. 
        proposer - is an int of the index of the player who proposed the mission. (between 0 and number_of_players)
        The function should return True if the vote is for the mission, and False if the vote is against the mission.
        '''

        # * Always vote yes on the first mission, regardless if resistance or spy
        if self.current_mission == 0:
            return True

        # * Always vote yes on the fifth vote, regardless if resistance or spy
        if self.n_rejected_votes >= 4:
            return True

        # resistance
        if not self.is_spy():
            probability = self.total_prob
            for i in mission:
                # vote against any team that involves spy
                if i in self.spy_list:
                    return False
                if i in self.sus_meter.keys():
                    probability -= self.sus_meter[i]
            #* If there are no guaranteed spies, and we're in the mission, vote for
            if self.player_number in mission:
                return True
            return random.random() > (probability/self.number_of_spies)
        # spy
        else:
            spies_in = 0
            betrayals_req = Agent.fails_required[self.number_of_players][self.current_mission]
            for i in mission:
                if i in self.spy_list:
                    spies_in += 1
            if spies_in < betrayals_req:
                return False
            # There are enough spies to successfully sabotage
            else:
                return True

    def vote_outcome(self, mission, proposer, votes):
        '''
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        mission  - is a list of agents to be sent on a mission. 
        proposer - is an int of the index of the player who proposed the mission. (between 0 and number_of_players)
        votes    - is a dictionary mapping player indexes to Booleans (True if they voted for the mission, False otherwise).
        No return value is required or expected.
        '''
        # Based on votes, if we suspect someone to be a spy - if they accept: what happen?
        # Based on votes, if we suspect someone to be a spy - if they reject: what happen?

        # * Did the team can rejected?
        n_approved = 0
        for val in votes.values():
            if val:
                n_approved += 1
        # * Not majority vote, increment number of rejected votes
        if 2*n_approved <= len(self.number_of_players):
            self.n_rejected_votes += 1

        # todo - if fifth vote is rejected, assume all who rejected are spies (playing optimally)
        if self.n_rejected_votes >= 5:
            for key, val in votes.items():
                if not val and key not in self.spy_list:
                    self.spy_list.append(key)
            #! if len(self.spy_list) > self.spy_count:



        agent_involved = False
        if self.is_spy():
            pass
        else:
            #! WHAT TO DO
            for agent in mission:
                if agent in self.spy_list:
                    agent_involved = True
                    break
            # if agent_involved:
            #     for i in votes.keys():
            #         if votes[i] == True and i not in self.spy_list:
            #             self.sus_meter[i] *= 1.2

    def betray(self, mission, proposer):
        '''
        The agents on the mission are distinct and indexed between 0 and number_of_players, and include this agent.
        mission  - is a list of agents to be sent on a mission. 
        proposer - is an int of the index of the player who proposed the mission. (between 0 and number_of_players)
        The method should return True if this agent chooses to betray the mission, and False otherwise. 
        By default, spies will betray 30% of the time. 
        '''
        # based on how close we winning (game state) - betrayal rate

        # ignore proposer, does not affect our decision

        # the simple agent always betray when he's in the mission
        # reduce the betrayal rate if there are many spies in the mission
        if self.is_spy():
            spies_count = 0
            for agent in mission:
                if agent in self.spy_list:
                    spies_count += 1
            betrayals_req = Agent.fails_required[self.number_of_players][self.current_mission]
            if spies_count == len(mission) and self.current_mission == 0:   #! other scenarios, close to winning
                return False
            if spies_count > betrayals_req:
                return random.random() < (betrayals_req/spies_count)
            return True

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
        self.n_rejected_votes = 0   # Reset number of reject votes for next mission

        if not mission_success:
            self.n_failed_missions += 1
        
        # if spy, just pass
        self.current_mission += 1
        
        not_in_mission = []
        not_in_mission_sum = self.total_prob
        new_in_mission_sum = 0
        
        # if good, if there are betrayals => people in mission, increase sus
        #* Everyone sabotaged the mission
        if betrayals == len(mission):
            # if all agents sent on mission betrayed
            # self.update_sus_meter(self, mission, betrayed, all_spies)
            for i in range(self.number_of_players):
                if i in mission and i != self.player_number:
                    # update sus and add to spy_list
                #! CLEAN UP
                    current_sus = self.sus_meter.get(i)
                    not_in_mission_sum -= current_sus
                    self.sus_meter[i] = 1
                    new_in_mission_sum += self.sus_meter[i]
                    self.spy_list.append(i)
                elif i not in mission and i != self.player_number:
                    not_in_mission.append(i)
                else:
                    pass
        #* No betrayals
        elif betrayals == 0:
            for i in range(self.number_of_players):
                if i in mission and i != self.player_number:
                    # decrease sus due to mission succeeded
                    current_sus = self.sus_meter.get(i)
                    not_in_mission_sum -= current_sus
                    self.sus_meter[i] = current_sus/1.2
                    new_in_mission_sum += self.sus_meter[i]
                elif i not in mission and i != self.player_number:
                    # ones who weren't in the mission will increase sus
                    not_in_mission.append(i)
                else:
                    pass
        #* Some betrayal(s)
        else:
            for i in range(self.number_of_players):
                if i in mission and i != self.player_number:
                    # increase sus as there are some fails vote
                    current_sus = self.sus_meter.get(i)
                    not_in_mission_sum -= current_sus
                    self.sus_meter[i] = current_sus * 1.2
                    new_in_mission_sum += self.sus_meter[i]
                    self.spy_list.append(i)
                elif i not in mission and i != self.player_number:
                    not_in_mission.append(i)
                else:
                    pass

        increase_sus = (self.total_prob - new_in_mission_sum -
                        not_in_mission_sum) / len(not_in_mission)
        # update sus_meter for ones who didn't go on the mission
        for j in not_in_mission:
            current_sus = self.sus_meter.get(j)
            self.sus_meter[j] = current_sus + increase_sus
        # if good, if there are no betrayals => people in mission, less sus
        # if betrayals == len(mission), all agents on that mission are spies

    #
    def round_outcome(self, rounds_complete, missions_failed):  #! DONE
        '''
        basic informative function, where the parameters indicate:
        rounds_complete - is an int of rounds (between 0-5) that have been completed
        missions_failed - is an int of missions (between 0-3) that have failed.
        '''
        # * for our own sake
        # ratio betw rounds_complete : missions_failed, how affect us?
        # called from

        pass

    #* Game over - who won
    def game_outcome(self, spies_win, spies):   #! DONE
        '''
        basic informative function, where the parameters indicate:
        spies_win - True iff the spies caused 3+ missions to fail
        spies     - a list of the player indexes for the spies.
        '''
        # LITERALLY do nothing
        pass
