from agent import Agent
import random


class OurAgent(Agent):
    '''A sample implementation of a random agent in the game The Resistance'''

    # * if not spy internal state / memory (probability of index agent of being a spy)
    sus_meter = dict()    # int(index) -> float(probability of being a spy)

    # * if spy internal state / memory (how sus we are) how many times we have betrayed

    #   - the more we betray, the less likely we betray again (reduce sus), depends on how close we are to winning
    voted_to_go_on_mission = []
    betrayal_rate = 0.0  # no_missions_failed / rounds_complete
    number_of_spies = 0
    # ? 5 C 2 = 10
    # (1 / number_of_players) %

    # ? 2 spies out of 4
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

        # set the number of spies base on table size
        self.number_of_spies = Agent.spy_count.get(number_of_players)
        self.total_prob = self.number_of_spies * 1.0
        # Create probability chart for
        if not self.is_spy():
            for i in range(number_of_players):
                # Do not include oneself as probability of being a spy
                if i == self.player_number:
                    continue
                self.sus_meter.setdefault(
                    i, (1.0 * self.number_of_spies) / (number_of_players - 1))

    #! DONE

    def is_spy(self):
        '''
        returns True iff the agent is a spy
        '''
        return self.player_number in self.spy_list

    # |                                      |
    # |  Below is where we need to add code  |
    # V                                      V

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
            print("spy choosing")
            team.append(self.player_number)
            betrayals_required -= 1
            while betrayals_required > 0:
                pick = random.choice(self.spy_list)
                if pick not in team:
                    team.append(pick)
                    betrayals_required -= 1

            while len(team) < team_size:
                agent = random.randrange(self.number_of_players)
                if agent not in team:
                    team.append(agent)
        else:
            print("resistance choosing")
            team.append(self.player_number)
            while len(team) < team_size:
                agent = random.randrange(self.number_of_players)
                # choose a random agent that is not in the spy list
                if agent not in team and agent not in self.spy_list:
                    team.append(agent)

        # * Are we good

        return team

    def vote(self, mission, proposer):
        '''
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        mission  - is a list of agents (index) to be sent on a mission. 
        proposer - is an int of the index of the player who proposed the mission. (between 0 and number_of_players)
        The function should return True if the vote is for the mission, and False if the vote is against the mission.
        '''
        # how does proposer affect our vote?
        # based on who is going on the mission, our vote is affected based on our internal state
        if not self.is_spy():
            probability = self.total_prob
            for i in mission:
                if i in self.sus_meter.keys():
                    probability -= self.sus_meter[i]
            # return random.random() < agent.memory[index of mission]
            return random.random() > (probability/self.number_of_spies)
        else:
            spies_in = 0
            for i in mission:
                if i in self.spy_list:
                    spies_in += 1
            if spies_in == 0:
                return False
            else:
                # the spies_in amount will determine the probability of we voting for the mission as a spy
                # for now, it always vote for any mission that has at least 1 spy in
                return True
        # return random.random()<0.5

    def vote_outcome(self, mission, proposer, votes):
        '''
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        mission  - is a list of agents to be sent on a mission. 
        proposer - is an int of the index of the player who proposed the mission. (between 0 and number_of_players)
        votes    - is a dictionary mapping player indexes to Booleans (True if they voted for the mission, False otherwise).
        No return value is required or expected.
        '''
        # * for our own sake
        # Based on votes, if we suspect someone to be a spy - if they accept: what happen?
        # Based on votes, if we suspect someone to be a spy - if they reject: what happen?
        agent_involved = False
        if self.is_spy():
            pass
        else:
            for agent in mission:
                if agent in self.spy_list:
                    agent_involved = True
                break
            # if agent_involved is True:
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
        if self.is_spy():
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

        # * for our sake
        # if spy, just pass
        if self.is_spy():
            pass
        else:
            not_in_mission = []
            not_in_mission_sum = self.total_prob
            new_in_mission_sum = 0
            # if good, if there are betrayals => people in mission, increase sus
            if betrayals == len(mission):
                # if all agents sent on mission betrayed
                # all_spies = True
                # betrayed = True
                # self.update_sus_meter(self, mission, betrayed, all_spies)
                for i in range(self.number_of_players):
                    if i in mission and i != self.player_number:
                        # update sus and add to spy_list
                        current_sus = self.sus_meter.get(i)
                        not_in_mission_sum -= current_sus
                        self.sus_meter[i] = 1
                        new_in_mission_sum += self.sus_meter[i]
                        self.spy_list.append(i)
                    elif i not in mission and i!= self.player_number:
                        not_in_mission.append(i)
                    else:
                        pass
            elif betrayals == 0:
                for i in range(self.number_of_players):
                    if i in mission and i != self.player_number:
                        # decrease sus due to mission succeeded
                        current_sus = self.sus_meter.get(i)
                        not_in_mission_sum -= current_sus
                        self.sus_meter[i] = current_sus/1.2
                        new_in_mission_sum += self.sus_meter[i]
                    elif i not in mission and i!= self.player_number:
                        # ones who weren't in the mission will increase sus
                        not_in_mission.append(i)
                    else:
                        pass
            else:
                for i in range(self.number_of_players):
                    if i in mission and i != self.player_number:
                        # increase sus as there are some fails vote
                        current_sus = self.sus_meter.get(i)
                        not_in_mission_sum -= current_sus
                        self.sus_meter[i] = current_sus * 1.2
                        new_in_mission_sum += self.sus_meter[i]
                        self.spy_list.append(i)
                    elif i not in mission and i!= self.player_number:
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
    def round_outcome(self, rounds_complete, missions_failed):
        '''
        basic informative function, where the parameters indicate:
        rounds_complete - the number of rounds (0-5) that have been completed
        missions_failed - the number of missions (0-3) that have failed.
        '''
        # * for our own sake
        # ratio betw rounds_complete : missions_failed, how affect us?
        # called from

        pass

    # * Game over - who won
    def game_outcome(self, spies_win, spies):
        '''
        basic informative function, where the parameters indicate:
        spies_win - True iff the spies caused 3+ missions to fail
        spies     - a list of the player indexes for the spies.
        '''
        # LITERALLY do nothing
        pass
