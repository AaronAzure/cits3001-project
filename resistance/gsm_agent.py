"""
@name: gsm_agent
@author: Aaron Wee (22702446) and Alex Mai (22638901)
@about: CITS3001 project 2021 - resistanceAI
"""
import random
from itertools import combinations


class GSMAgent():
    '''A sample implementation of a random agent in the game The Resistance'''

    # game parameters for agents to access
    # python is such that these variables could be mutated, so tournament play
    # will be conducted via web sockets.
    mission_sizes = {
            5:[2,3,2,3,3], \
            6:[2,3,4,3,4], \
            7:[2,3,3,4,4], \
            8:[3,4,4,5,5], \
            9:[3,4,4,5,5], \
            10:[3,4,4,5,5]
    }
    # number of spies for different game sizes
    spy_count = {5:2, 6:2, 7:3, 8:3, 9:3, 10:4} 
    fails_required = {
            5:[1,1,1,1,1], \
            6:[1,1,1,1,1], \
            7:[1,1,1,2,1], \
            8:[1,1,1,2,1], \
            9:[1,1,1,2,1], \
            10:[1,1,1,2,1]
    }

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

        #* list of all agent indexes (including oneself)
        self.players = [i for i in range(number_of_players)]
        #* list of other agent indexes (excluding oneself)
        self.others = [i for i in range(number_of_players) if i != self.player_number]

        #* set the number of spies base on table size
        self.number_of_spies = self.spy_count.get(number_of_players)

        #* any team of this length without us(resistance) is guaranteed at least 1 spy
        self.non_spies = number_of_players - self.number_of_spies

        self.current_mission = 0
        self.n_rejected_votes = 0
        self.spy_wins = 0
        self.res_wins = 0

        #* associates - list describing trust between two players. (e.g. associates[0][1] means how much does player 0 trust player 1)
        #* suspect_teams - list containing all possible spies combination, initial value at 0
        initial_sus = self.number_of_spies/number_of_players
        self.associates = [[Probability(initial_sus) for i in range(number_of_players)] for j in range(number_of_players)]
        
        worlds = combinations(self.others, self.number_of_spies)
        self.suspect_teams = []
        for i in worlds:
            self.suspect_teams.append([i, 0])

        #* List of suspicious actions over the number of actions
        self.sus_actions = dict()
        actions_vals = 0
        n_actions = 0
        for i in self.others:
            self.sus_actions.setdefault(i, [actions_vals, n_actions])

        #* List of good actions over the number of actions
        self.good_actions = dict()
        actions_vals = 0
        n_actions = 0
        for i in self.others:
            self.good_actions.setdefault(i, [actions_vals, n_actions])

        #* List of agents counting the number of times they voted FOR who we believe to be a spy
        self.voted_for_sus = dict()
        for i in self.others:
            self.voted_for_sus.setdefault(i, [initial_sus, 1.0])

        #* List of individual sus value
        self.suspects = dict()
        self.suspects = [Probability(0.0) for i in range(number_of_players)]

    def is_spy(self):
        '''
        returns True iff the agent is a spy
        '''
        return self.player_number in self.spy_list

    def update_suspects_team(self):
        '''
        Update the sus value of all possible spy teams after sus value of individual is updated
        this function is called in vote_outcome and mission_outcome
        '''
        #* Calculate how plausible a possible combination of spies are
        for team in self.suspect_teams:
            sus_value = 1
            possible_spy_members = []
            for i in range(self.number_of_spies):
                possible_spy_members.append(team[0][i])
            #* calculate/retreive the sus value of each individual agent
            for i in range(self.number_of_spies):
                if self.suspects[team[0][i]].value != 0:
                    sus_value *= self.suspects[team[0][i]].value
            #* This agent is not guaranteed to be a spy
            if sus_value < 1:
                collusiveness = 1
                #* Determine how collusive two agents are
                for i in range(self.number_of_spies):
                    for j in range(self.number_of_spies):
                        if i != j:
                            collusiveness *= self.associates[team[0][i]][team[0][j]].value
                new_sus_value = 0.50 + 0.50 * collusiveness
                voted_for_sus_val = 0.25
                sus_actions_val = 0.0
                good_actions_val = 0.0
                for i in possible_spy_members:
                    if self.voted_for_sus.get(i)[1] > 0:
                        voted_for_sus_val += (self.voted_for_sus[i][0]/self.voted_for_sus[i][1])

                    if self.sus_actions.get(i)[1] > 0:
                        sus_actions_val += (self.sus_actions[i][0]/self.sus_actions[i][1])

                    if self.good_actions.get(i)[1] > 0:
                        good_actions_val += (self.good_actions[i][0]/self.good_actions[i][1])

                new_sus_value *= (0.75 + voted_for_sus_val)
                new_sus_value *= sus_value
                new_sus_value *= 0.4 + 0.6 * (sus_actions_val)/self.number_of_spies
                new_sus_value *= 1 - 0.3 * (good_actions_val)/self.number_of_spies
                team[1] = new_sus_value
            #* This agent is guaranteed to be a spy
            else:
                team[1] = sus_value

    def maybe_last_turn(self):
        '''
        Return true if there is one more round to win/lose, regardless if spy or resistance.
        false otherwise.
        '''
        return (self.spy_wins == 2) or (self.res_wins == 2)

    def get_most_sus_team(self):
        '''
        Return the team with the highest sus value
        '''
        #* Most sus team
        temp = [i for i in self.suspect_teams if self.player_number not in i[0]]
        result = max(temp, key=lambda p: p[1])
        if result[1] > 0:
            return result[0]
        #* Everyone equally sus
        else:
            return []

    def get_sus_value(self, agent):
        '''
        Return sus value of agent
        '''
        voted_for_sus_value = 0
        if self.voted_for_sus[agent][1] > 0:
            voted_for_sus_value += (self.voted_for_sus[agent][0]/self.voted_for_sus[agent][1])
        value = (0.75 + 0.25 * voted_for_sus_value)
        
        sus_actions_value = 0
        if self.sus_actions[agent][1] > 0:
            sus_actions_value = (self.sus_actions[agent][0]/self.sus_actions[agent][1])
        value *= 0.4 + 0.6 * sus_actions_value

        value *= self.suspects[agent].value

        good_actions_value = 0
        if self.good_actions[agent][1] > 0:
            good_actions_value += (self.good_actions[agent][0]/self.good_actions[agent][1])
        value *= 1 - 0.1 * good_actions_value
        
        return value

    def get_less_sus_agents(self):
        '''
        Return the team with the lowest sus value
        '''
        bad = self.get_most_sus_team()
        temp = set(self.others) - set(bad)
        result = sorted(temp, key=lambda p: self.get_sus_value(p))
        
        return result

    def propose_mission(self, team_size, betrayals_required=1):
        '''
        expects a team_size list of distinct agents with id between 0 (inclusive) and number_of_players (exclusive)
        to be returned. 
        betrayals_required are the number of betrayals required for the mission to fail.
        '''
        team = []
        #* always include myself
        team.append(self.player_number)
        if self.current_mission == 0:
            while len(team) < team_size:
                pick = random.choice(self.players)
                if pick not in team:
                    team.append(pick)
            return team

        less_sus_agents = self.get_less_sus_agents()
        #* player is resistance
        if not self.is_spy():
            #* add agents who are less sus
            for agent in less_sus_agents:
                if len(team) < team_size:
                    team.append(agent)
        #* player is spy
        else:
            #* add fellow spies from less_sus_agents list till @param betrayal_required
            for agent in less_sus_agents:
                if agent in self.spy_list and betrayals_required < len(team):
                    team.append(agent)
            while betrayals_required < len(team):
                pick = random.choice(self.spy_list)
                if pick not in team:
                    team.append(pick)
            for agent in less_sus_agents:
                if agent not in team and len(team) < team_size:
                    team.append(agent)
        return team

    def vote(self, mission, proposer):
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        The function should return True if the vote is for the mission, and False if the vote is against the mission.
        '''

        #* Always vote FOR your selected team
        if proposer == self.player_number:
            return True

        #* Always vote FOR on the first mission, regardless if resistance or spy
        if self.current_mission == 0 and self.n_rejected_votes == 0:
            return True

        #* Always vote FOR on the fifth vote, regardless if resistance or spy
        if self.n_rejected_votes == 4:
            return True

        #* As a spy, vote for all missions that include enough spy to sabotage the mission!
        if self.is_spy():
            spies_count = len([i for i in mission if i in self.spy_list])
            betrayals_req = self.fails_required[self.number_of_players][self.current_mission]

            return spies_count >= betrayals_req

        #* If I'm not on the team and the team is equal to the number of actual resistance members
        if len(mission) == self.non_spies and self.player_number not in mission:
            return False

        most_sus_team = self.get_most_sus_team()
        return most_sus_team in mission

    def vote_outcome(self, mission, proposer, votes):
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        votes - list of agents (index) that voted FOR the mission
        is a dictionary mapping player indexes to Booleans (True if they voted for the mission, False otherwise).
        No return value is required or expected.
        '''
        #* Did the team get rejected?
        n_approved = len(votes)
        #* Not majority vote, increment number of rejected votes
        if 2 * n_approved <= self.number_of_players:
            self.n_rejected_votes += 1

        not_in_mission = [i for i in self.players if i not in mission]

        #* Increase sus value if leader did not choose themself
        if proposer != self.player_number:
            action_val = (proposer not in mission)
            self.sus_actions[proposer] = [self.sus_actions.get(proposer)[0] + (action_val), self.sus_actions.get(proposer)[1] + 1]

        #* Based on heuristics, increase each player sus value
        for agent in self.others:
            #* Increase sus value for those that voted AGAINST the first mission
            action_val = (agent not in votes and self.current_mission == 0 and self.n_rejected_votes == 0)
            self.sus_actions[agent] = [self.sus_actions[agent][0] + (action_val), self.sus_actions[agent][1] + 1]

            #* Increase sus value for those that voted AGAINST on the fifth vote
            action_val = (agent not in votes and self.n_rejected_votes == 4)
            self.sus_actions[agent] = [self.sus_actions[agent][0] + (action_val), self.sus_actions[agent][1] + 1]

            #* Increase sus value for those out of team of suslength, but voted FOR
            action_val = (agent in votes and len(mission) == self.non_spies and agent not in mission)
            self.sus_actions[agent] = [self.sus_actions[agent][0] + (action_val), self.sus_actions[agent][1] + 1]

            #* Increase sus value for those in team, but votes AGAINST
            action_val = (agent not in votes and agent in mission)
            self.good_actions[agent] = [self.good_actions[agent][0] + (action_val), self.good_actions[agent][1] + 1]

            if agent == proposer:
                #* Spy does not choose second spy in team
                for p2 in not_in_mission:
                    self.associates[agent][p2].adjust_probability(1, len(not_in_mission))
            else:
                #* for all agents not in mission that voted FOR, could possibly be in cahoots with someone on the mission
                if agent not in mission:
                    if (agent in votes):
                        for p2 in mission:
                            self.associates[agent][p2].adjust_probability(1, len(mission))
                    else:
                        for p2 in not_in_mission:
                            self.associates[agent][p2].adjust_probability(1, len(not_in_mission))

        self.update_suspects_team()

        self.last_votes = votes

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
            betrayals_req = self.fails_required[self.number_of_players][self.current_mission]

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
        #* Record the mission status
        if mission_success:
            self.res_wins += 1
        else:
            self.spy_wins += 1

        self.n_rejected_votes = 0   # Reset number of reject votes for next mission

        #* Agents other than player in the mission
        others_in_mission = [i for i in mission if i != self.player_number]
        not_in_mission = [i for i in self.others if i not in mission and i != self.player_number]

        #* Record how often an agent is involved in a mission that was sabotaged
        if betrayals > 0:
            for i in others_in_mission:
                self.suspects[i].adjust_probability(betrayals, len(others_in_mission))

        #* Record how often an agent is not involved in a sabotaged mission
        if betrayals < self.number_of_spies:
            for i in not_in_mission:
                self.suspects[i].adjust_probability(self.number_of_spies - betrayals, len(not_in_mission))

        #* Keep track of suspicious behaviours
        #* Record agents who voted FOR missions that got sabotaged and voted AGAINST missions that were successful
        if self.current_mission > 0:
            for i in others_in_mission:
                val = int((i in self.last_votes and betrayals > 0) or (i not in self.last_votes and betrayals == 0))
                self.voted_for_sus[i] = [self.voted_for_sus[i][0] + (val), self.voted_for_sus[i][1] + 1]

        self.update_suspects_team()
        self.current_mission += 1

    def round_outcome(self, rounds_complete, missions_failed):
        '''
        basic informative function, where the parameters indicate:
        rounds_complete, the number of rounds (0-5) that have been completed
        missions_failed, the number of missions (0-3) that have failed.
        '''
        # nothing to do here
        pass

    def game_outcome(self, spies_win, spies):
        '''
        basic informative function, where the parameters indicate:
        spies_win, True iff the spies caused 3+ missions to fail
        spies, a list of the player indexes for the spies.
        '''
        pass


class Probability(object):
    """ Class for initializing and updating probability """

    def __init__(self, v0):
        self.value = v0
        self.n = 0

    def adjust_probability(self, value, n):
        self.value = 1 - (1 - self.value) * (1 - float(value) / float(n))
        self.n += n