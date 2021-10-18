
import random

RED = '\033[91m'
YELLOW = '\033[93m'
GREEN = '\033[92m'
END = '\033[0m'


# !------------------------------------------------------------------------------------------! #
# *  5 players (2 spies)  -   5 C 2  =  10
# *  6 players (2 spies)  -   6 C 2  =  15
# *  7 players (3 spies)  -   7 C 3  =  35
# *  8 players (3 spies)  -   8 C 3  =  56
# *  9 players (3 spies)  -   9 C 3  =  84
# * 10 players (4 spies)  -  10 C 4  =  210
# !------------------------------------------------------------------------------------------! #
# todo Research Question: Best resistance player in a 5 player game (in finding the spies)


def update_sus_meter(mission, betrayed, all_spies=False):
    total_prob = 2
    not_in_mission = []
    not_in_mission_sum = total_prob
    new_in_mission_sum = 0
    if betrayed is True:
        if all_spies is True:
            for i in sus_meter.keys():
                if i in mission:
                    # update sus and add to spy_list
                    current_sus = sus_meter.get(i)
                    not_in_mission_sum -= current_sus
                    sus_meter[i] = 1
                    new_in_mission_sum += sus_meter[i]
                else:
                    not_in_mission.append(i)
        else:
            for i in sus_meter.keys():
                if i in mission:
                    # update sus and add to spy_list
                    current_sus = sus_meter.get(i)
                    not_in_mission_sum -= current_sus
                    sus_meter[i] = current_sus * 1.2
                    new_in_mission_sum += sus_meter[i]
                else:
                    not_in_mission.append(i)
    elif betrayed is False:
        for i in sus_meter.keys():
            if i in mission:
                # update sus and add to spy_list
                current_sus = sus_meter.get(i)
                not_in_mission_sum -= current_sus
                sus_meter[i] = current_sus/1.2
                new_in_mission_sum += sus_meter[i]
            else:
                not_in_mission.append(i)

    increase_sus = (total_prob - new_in_mission_sum -
                    not_in_mission_sum) / len(not_in_mission)
    for j in not_in_mission:
        current_sus = sus_meter.get(j)
        sus_meter[j] = current_sus + increase_sus


def mission_outcome(mission, proposer, betrayals, mission_success):
    '''
    The agents on the mission are distinct and indexed between 0 and number_of_players.
    mission         - is a list of agents to be sent on a mission. 
    proposer        - is an int between 0 and number_of_players and is the index of the player who proposed the mission.
    betrayals       - is the number of people on the mission who betrayed the mission, 
    mission_success - is True if there were not enough betrayals to cause the mission to fail, False otherwise.
    It is not expected or required for this function to return anything.
    '''

    # if good, if there are betrayals => people in mission, increase sus
    if betrayals == len(mission):
        # if all agents sent on mission betrayed
        update_sus_meter(mission, False, True)

    elif betrayals == 0:
        update_sus_meter(mission, False, False)
        # for i in mission:
    else:
        update_sus_meter(mission, True)
    # if good, if there are no betrayals => people in mission, less sus
    # if betrayals == len(mission), all agents on that mission are spies

    pass

#


def print_result():
    total = 0
    for key, val in sus_meter.items():
        print(" " + str(key) + "   :  " + "{:.2f}".format(val))
        total += val
    print(YELLOW + "total = " + "{:.2f}".format(total) + END)


# sus_meter = dict()
# number_of_players = 5
# player_number = random.randint(0, number_of_players - 1)
# print(GREEN + "-- player id = " + str(player_number) + "\n" + END)


# for i in range(number_of_players):
#     # Do not include one as probability of being a spy
#     if i == player_number:
#         continue
#     sus_meter.setdefault(i, 2.0 / (number_of_players - 1))

# print_result()
# mission_outcome([1, 4], 4, 1, False)
# print("--")
# print_result()
# mission_outcome([1, 3], 4, 1, False)
# print("--")
# print_result()
# mission_outcome([0, 4], 4, 1, False)
# # # mission_outcome([0,4], 2, 1, False)
# print("--")
# print_result()

# print(GREEN + "-- player id = " + str(player_number) + END)

from itertools import combinations

# players = [0,1,2]
# temp = list(combinations(players, 2))
# print(temp)
# for i in temp:
#     for j in i:
#         print(j)
# print([(x,y,z) for x in range(3) for y in range(3) for z in range(3) if x < y < z])


agents = [0,1,2,3,4,5]
others = [0,1,3,4]
# worlds = list(combinations(agents, 2))
# for i in worlds:
#     print(i)

sus_meter = {}
worlds = list(combinations(others, 2))
world_spy_chance = float(1/len(worlds))
for i in worlds:
    sus_meter.setdefault(i, world_spy_chance)

print(sus_meter)
print(len(sus_meter))