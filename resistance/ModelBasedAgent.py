import random
import math

class MAgent:
    '''An abstract super class for an agent in the game The Resistance.
    new_game and *_outcome methods simply inform agents of events that have occured,
    while propose_mission, vote, and betray require the agent to commit some action.'''

    #game parameters for agents to access
    #python is such that these variables could be mutated, so tournament play
    #will be conducted via web sockets.
    #e.g. self.mission_size[8][3] is the number to be sent on the 3rd mission in a game of 8
    mission_sizes = {
            5:[2,3,2,3,3], \
            6:[3,3,3,3,3], \
            7:[2,3,3,4,5], \
            8:[3,4,4,5,5], \
            9:[3,4,4,5,5], \
            10:[3,4,4,5,5]
            }
    #number of spies for different game sizes
    spy_count = {5:2, 6:2, 7:3, 8:3, 9:3, 10:4} 
    #e.g. self.betrayals_required[8][3] is the number of betrayals required for the 3rd mission in a game of 8 to fail
    fails_required = {
            5:[1,1,1,1,1], \
            6:[1,1,1,1,1], \
            7:[1,1,1,2,1], \
            8:[1,1,1,2,1], \
            9:[1,1,1,2,1], \
            10:[1,1,1,2,1]
            }
    def __init__(self, name):
        self.name             = name
    
    def __str__(self):
        return 'Agent '+self.name

    def __repr__(self):
        return self.__str__()

    def new_game(self, number_of_players, player_number, spies):
        self.is_spy = True if len(spies) > 0 else False
        self.spies_alibi = spies
        self.num_of_players = number_of_players
        self.id = player_number
        self.misbehavior = {}
        self.votes = []
        self.curr_round = 0
        self.rounds_completed = 0
        self.spies_has_won = 0
        self.vote_times = 0
        self.player = [i for i in range(self.num_of_players)]
        self.i_won_as_resis = False
        self.i_won_as_spies = False
        for i in range(self.num_of_players):
            self.misbehavior[i] = 0
        if self.is_spy:
            self.spies_alibi.remove(self.id)
    
    def propose_mission(self, team_size, fails_required = 1):
        if self.rounds_completed == self.curr_round:
            self.curr_round += 1
        team = []
        team.append(self.id)
        if self.curr_round == 1:
            while len(team) < team_size:
                candidate = random.randint(0, self.num_of_players - 1)
                if candidate != self.id and candidate not in team:
                    team.append(candidate)

        elif self.is_spy:
            resistance = list(set(self.spies_alibi + [self.id]).symmetric_difference(set(self.player)))
            # print("resistance is ", resistance)
            if fails_required > 1:
                spy_with_min_misbehavior = self.spies_alibi[0]
                for i in range(1,len(self.spies_alibi)):
                    if self.misbehavior[self.spies_alibi[i]] < self.misbehavior[spy_with_min_misbehavior]:
                        spy_with_min_misbehavior = self.spies_alibi[i]
                team.append(spy_with_min_misbehavior)
            j = 0
            while len(team) < team_size:
                team.append(resistance[j])
                j += 1
        else:
            sort = dict(sorted(self.misbehavior.items(), key=lambda item:item[1]))
            sort = list(sort)
            i = 0
            while len(team) < team_size:
                if sort[i] != self.id:
                    team.append(sort[i])
                i += 1
        return team
        
    def suspects(self):
        sort = dict(sorted(self.misbehavior.items(), key=lambda item:item[1]))
        sort = list(sort)
        sort.reverse()
        return sort[:self.spy_count[self.num_of_players] + 1]

    def vote(self, mission, proposer):
        if self.curr_round == self.rounds_completed:
            self.curr_round += 1
        if self.curr_round == 1:
            return True
        if proposer == self.id:
            return True
        fails_required = self.fails_required[self.num_of_players][self.curr_round - 1]
        if self.is_spy:
            if len(list(set(self.spies_alibi + [self.id]) & set(mission))) < fails_required:
                return False
        else:
            suspects = self.suspects()
            if len(list(set(suspects) & set(mission))) >= fails_required:
                return False
        return True

    def vote_outcome(self, mission, proposer, votes):
        self.vote_times += 1
        round_vote = []
        for i in range(self.num_of_players):
            if i in votes:
                round_vote.append(True)
            else:
                round_vote.append(False)
        self.votes.append(round_vote)

    def betray(self, mission, proposer):
        if self.curr_round == 1:
            return False
        spies_on_mission = list(set(self.spies_alibi + [self.id]) & set(mission))
        fail_required = self.fails_required[self.num_of_players][self.curr_round - 1]
        if len(spies_on_mission) < fail_required:
            return False
        if len(mission) == 2:
            if self.spies_has_won == 0 or self.spies_has_won == 2:
                return True
            return False
        return True

    def mission_outcome(self, mission, proposer, num_fails, mission_success):
        if self.vote_times != self.curr_round:
            window = self.curr_round
            while window < self.vote_times:
                for k in self.player:
                    if self.votes[window - 1][k] is True:
                        self.misbehavior[k] += 1
                window += 1
        if mission_success:
            if num_fails >= 1:
                for i in mission:
                    self.misbehavior[i] += 1
            for j in self.player:
                if self.votes[self.vote_times - 1][j] is False:
                    self.misbehavior[j] += 1
        else:
            for i in mission:
                    self.misbehavior[i] += 1
            if self.curr_round != 1:
                for j in self.player:
                    if self.votes[self.vote_times - 1][j] is True:
                        self.misbehavior[j] += 1
            if num_fails > 1:
                self.misbehavior[proposer] += 1
        
    def round_outcome(self, rounds_complete, missions_failed):
        self.rounds_completed = rounds_complete
        self.spies_has_won = missions_failed

    def game_outcome(self, resistance_win, spies):
        if resistance_win:
            if not self.is_spy:
                self.i_won_as_resis = True

        else:
            if self.is_spy:
                self.i_won_as_spies = True

        return self.i_won_as_resis, self.i_won_as_spies