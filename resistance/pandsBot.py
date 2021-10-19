from agent import Agent
import random

from bcolors import bcolors


class pandsbot(Agent):
    '''A sample implementation of a random agent in the game The Resistance'''

    def __init__(self, name='Rando'):
        '''
        Initialises the agent.
        Nothing to do here.
        '''
        self.name = name
        self.times_won = 0
        self.n_games = 0

    def new_game(self, number_of_players, player_number, spy_list):
        '''
        initialises the game, informing the agent of the 
        number_of_players, the player_number (an id number for the agent in the game),
        and a list of agent indexes which are the spies, if the agent is a spy, or empty otherwise
        '''
        self.number_of_players = number_of_players
        self.player_number = player_number
        self.spy_list = spy_list

        # list of all agent indexes (including oneself)
        self.players = [i for i in range(number_of_players)]
        # list of other agent indexes (excluding oneself)
        self.others = [i for i in range(
            number_of_players) if i != self.player_number]

        #* set the number of spies base on table size
        self.number_of_spies = Agent.spy_count.get(number_of_players)

        #* any team of this length without us(resistance) is guaranteed at least 1 spy
        self.sus_length = number_of_players - self.number_of_spies

        self.current_mission = 0
        self.n_rejected_votes = 0
        self.spy_wins = 0
        self.res_wins = 0

        #* associates - list describing trust between two players. (e.g. associates[0][1] means how much does player 0 trust player 1)
        #* suspect_teams - list containing all possible spies combination, initial value at 0
        initial_sus = self.number_of_spies/number_of_players
        if self.number_of_spies == 2:
            self.associates = [[Probability(initial_sus)
                                for i in range(number_of_players)] for j in range(number_of_players)]
            self.suspect_teams = [[(x, y), 0] for x in range(
                number_of_players) for y in range(number_of_players) if x < y]
        elif self.number_of_spies == 3:
            self.associates = [[Probability(initial_sus)
                                for i in range(number_of_players)] for j in range(number_of_players)]
            self.suspect_teams = [[(x, y, z), 0] for x in range(number_of_players) for y in range(
                number_of_players) for z in range(number_of_players) if x < y < z]
        else:
            self.associates = [[Probability(initial_sus)
                                for i in range(number_of_players)] for j in range(number_of_players)]
            self.suspect_teams = [[(x, y, z, t), 0] for x in range(number_of_players) for y in range(
                number_of_players) for z in range(number_of_players) for t in range(number_of_players) if x < y < z < t]

        # player not in team, team == 3, vote for mission
        # suspicious action and possible good actions get updates after vote completed
        self.sus_actions = [Variable(0, 0) for i in range(number_of_players)]

        #* player in team, votes against team with
        self.good_actions = [Variable(0, 0) for i in range(number_of_players)]

        # support suspects get updates after mission is done
        self.voted_for_sus = [Variable(initial_sus, 1.0)
                              for i in range(number_of_players)]

        # suspects - list of all individual players, initial sus at 0
        # the idea is to update the suspects value after each event, then update other arrays such as associates or suspect_teams
        self.suspects = [Probability(0.0) for i in range(number_of_players)]
        # print("player number is", player_number)

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
        # calculate how suspicious x[0] pair (spy1 friend for spy2, spy2 friend for spy1, and etc)
        for x in self.suspect_teams:
            sus_value = 1
            #* calculate/retreive the sus value of each individual agent
            for i in range(self.number_of_spies):
                if self.suspects[x[0][i]].estimate() != 0:
                    sus_value *= self.suspects[x[0][i]].estimate()
            #* This agent is not guaranteed to be a spy
            if sus_value < 1:
                collusiveness = 1
                #* Determine how collusive two agents are
                for i in range(self.number_of_spies):
                    for j in range(self.number_of_spies):
                        if i != j:
                            collusiveness *= self.associates[x[0]
                                                             [i]][x[0][j]].estimate()
                new_sus_value = 0.50 + 0.50 * collusiveness
                temp2 = 0.25
                temp3 = 0.0
                temp4 = 0.0
                for i in range(self.number_of_spies):
                    temp2 *= self.voted_for_sus[x[0][i]].estimate()
                    temp3 += self.sus_actions[x[0][i]].estimate()
                    temp4 += self.good_actions[x[0][i]].estimate()
                new_sus_value *= (0.75 + temp2)
                new_sus_value *= sus_value
                new_sus_value *= 0.4 + 0.6 * (temp3)/2
                new_sus_value *= 1 - 0.1 * (temp3)/2
                x[1] = new_sus_value
            #* This agent is guaranteed to be a spy
            else:
                x[1] = sus_value

    def maybe_last_turn(self):
        '''1 more round to win/lose?'''
        return (self.spy_wins == 2) or (self.res_wins == 2)

    def get_most_sus_team(self):
        '''
        Return the team with the highest sus value
        '''
        tmp = [i for i in self.suspect_teams if self.player_number not in i[0]]
        result = max(tmp, key=lambda p: p[1])
        #* Most sus team
        if result[1] > 0:
            return result[0], result[1]
        #* Team all equally sus
        else:
            return []

    def get_sus_value(self, agent):
        value = (0.75 + 0.25 * self.voted_for_sus[agent].estimate())
        value *= self.suspects[agent].estimate()
        value *= 0.4 + 0.6 * (self.sus_actions[agent].estimate())
        value *= 1 - 0.1 * (self.good_actions[agent].estimate())
        return value

    def get_good_players(self):
        # get all players that is not in the most suspicious team
        bad, value = self.get_most_sus_team()
        temp = set(self.others)-set(bad)
        result = sorted(temp, key=lambda p: self.get_sus_value(p))

        return result

    def propose_mission(self, team_size, betrayals_required=1):
        '''
        expects a team_size list of distinct agents with id between 0 (inclusive) and number_of_players (exclusive)
        to be returned. 
        betrayals_required are the number of betrayals required for the mission to fail.
        '''
        team = []
        # always include myself
        team.append(self.player_number)
        if self.current_mission == 0:
            while len(team) < team_size:
                pick = random.choice(self.players)
                if pick not in team:
                    team.append(pick)
            return team

        less_sus_agents = self.get_good_players()
        #* player is resistance
        if not self.is_spy():
            # add agents from good players list
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
            betrayals_req = Agent.fails_required[self.number_of_players][self.current_mission]

            return spies_count >= betrayals_req

        #* If I'm not on the team and it's a team of sus length!
        if len(mission) == self.sus_length and not self.player_number in mission:
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
        if 2*n_approved <= self.number_of_players:
            self.n_rejected_votes += 1

        not_in_mission = [i for i in self.players if i not in mission]

        #* Increase sus value if leader did not choose themself
        self.sus_actions[proposer].sampleBool(proposer not in mission)

        for agent in self.others:

            #* Increase sus value for those that voted AGAINST the first mission
            self.sus_actions[agent].sampleBool(agent not in votes and self.current_mission == 0 and self.n_rejected_votes == 0)

            #* Increase sus value for those that voted AGAINST on the fifth vote
            self.sus_actions[agent].sampleBool(agent not in votes and self.n_rejected_votes == 4)

            #* Increase sus value for those out of team of suslength, but voted FOR
            self.sus_actions[agent].sampleBool(agent in votes and len(mission) == self.sus_length and agent not in mission)

            #* Increase sus value for those in team, but votes AGAINST
            self.good_actions[agent].sampleBool(agent not in votes and agent in mission)

            if agent == proposer:
                #* Spy does not choose second spy in team
                for p2 in not_in_mission:
                    self.associates[agent][p2].new_sample(1, len(not_in_mission))
            else:
                #* for all agents not in mission that voted FOR, could possibly be in cahoots with someone on the mission
                if agent not in mission:
                    if (agent in votes):
                        for p2 in mission:
                            self.associates[agent][p2].new_sample(
                                1, len(mission))
                    else:
                        for p2 in not_in_mission:
                            self.associates[agent][p2].new_sample(
                                1, len(not_in_mission))

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
        #* Record the mission status
        if mission_success:
            self.res_wins += 1
        else:
            self.spy_wins += 1

        self.n_rejected_votes = 0   # Reset number of reject votes for next mission

        # Agents who were not in the mission
        not_in_mission = [i for i in mission if i != self.player_number]

        #* Record how often an agent is involved in a mission that was sabotaged
        if betrayals > 0:
            for i in mission:
                self.suspects[i].new_sample(betrayals, len(mission))

        #* Record how often an agent is not involved in a sabotaged mission
        if betrayals < self.number_of_spies:
            for i in not_in_mission:
                self.suspects[i].new_sample(
                    self.number_of_spies - betrayals, len(not_in_mission))

        #* Keep track of suspicious behaviours
        #* Record agents who voted FOR missions that got sabotaged and voted AGAINST missions that were successful
        if self.current_mission > 0:
            for p in not_in_mission:
                val = int((p in self.last_votes and betrayals > 0) or (p not in self.last_votes and betrayals == 0))
                self.voted_for_sus[p].new_sample(val, 1)

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
        if not spies_win and self.is_spy():
            # print(bcolors.GREEN, bcolors.UNDERLINE, "You WON!", bcolors.RESET)
            self.times_won += 1
        elif spies_win and self.is_spy():
            # print(bcolors.GREEN, bcolors.UNDERLINE, "You LOST!", bcolors.RESET)
            pass
        elif not spies_win and not self.is_spy():
            # print(bcolors.GREEN, bcolors.UNDERLINE, "You LOST!", bcolors.RESET)
            pass
        elif spies_win and not self.is_spy():
            # print(bcolors.GREEN, bcolors.UNDERLINE, "You WON!", bcolors.RESET)
            self.times_won += 1
        # print()
        self.n_games += 1
        # print(bcolors.GREEN, bcolors.UNDERLINE, self.player_number, bcolors.RESET)
        if (self.n_games >= 1000):
            print(bcolors.GREEN, "{:.2f}%".format(
                self.times_won / self.n_games * 100), "Pands = ({})".format(self.n_games), bcolors.RESET)
        pass


class Probability(object):
    """ Class for initialize and update probability """

    def __init__(self, v0):
        self.value = v0
        self.n = 0

    def __repr__(self):
        # return "%0.2f%% (%i)" % (100.0 * float(self.value), self.n)
        return "{:.2f}%".format(100.0 * float(self.value))
        # return "%0.2f%% " % (100.0 * float(self.value))

    # def sample(self, value):
    #     self.new_sample(value, 1)

    def new_sample(self, value, n):
        self.value = 1 - (1 - self.value)*(1 - float(value) / float(n))
        self.n += n

    def new_sampleNeg(self, value, n):
        self.value *= (1 - float(value) / float(n))

    def estimate(self):
        return self.value


class Variable(object):
    def __init__(self, v0, n0):
        self.total = v0
        self.samples = n0

    def __repr__(self):
        if self.samples:
            # return "%0.2f%% (%i)" % ((100.0 * float(self.total) / float(self.samples)), self.samples)
            return "%0.2f%% " % ((100.0 * float(self.total) / float(self.samples)))
        else:
            return "UNKNOWN"

    def sampleBool(self, value):
        self.new_sample(int(value), 1)

    def new_sample(self, value, n=1):
        self.total += value
        self.samples += n

    def estimate(self):
        if self.samples > 0:
            return float(self.total) / float(self.samples)
        else:
            return 0.0
