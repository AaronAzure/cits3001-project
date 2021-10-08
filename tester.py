
import random

RED = '\033[91m'
YELLOW = '\033[93m'
GREEN = '\033[92m'
END = '\033[0m'


# !------------------------------------------------------------------------------------------! #
        #*  5 players (2 spies)  -   5 C 2  =  10
        #*  6 players (2 spies)  -   6 C 2  =  15
        #*  7 players (3 spies)  -   7 C 3  =  35
        #*  8 players (3 spies)  -   8 C 3  =  56
        #*  9 players (3 spies)  -   9 C 3  =  84
        #* 10 players (2 spies)  -  10 C 4  =  210
# !------------------------------------------------------------------------------------------! #



def mission_outcome(mission, proposer, betrayals, mission_success):
    '''
    The agents on the mission are distinct and indexed between 0 and number_of_players.
    mission         - is a list of agents to be sent on a mission. 
    proposer        - is an int between 0 and number_of_players and is the index of the player who proposed the mission.
    betrayals       - is the number of people on the mission who betrayed the mission, 
    mission_success - is True if there were not enough betrayals to cause the mission to fail, False otherwise.
    It is not expected or required for this function to return anything.
    '''
    
    # if betrayals == 0 :
    #     new_prob = 0
    #     not_in_mission = 0
    #     if proposer in sus_meter.keys():
    #         sus_meter[proposer] = (sus_meter[proposer] / 2)
    #         new_prob += sus_meter[proposer]

    #     for i in range(number_of_players):
    #         if i in sus_meter.keys():
    #             if i in mission:
    #                 current_sus = sus_meter[i]
    #                 sus_meter[i] = (current_sus/2)
    #                 new_prob += sus_meter[i]
    #             else:
    #                 not_in_mission += 1
    #     temp = 1 - new_prob
    #     increase = temp / (not_in_mission)

    #     for i in range(number_of_players):
    #         if i in sus_meter.keys():
    #             if i not in mission and i != proposer:
    #                 sus_meter[i] += increase
    print(RED + str(mission) + ", proposer = " + str(proposer) + END)

    # if betrayals == 0:
    #     sums = 0
    #     not_in_mission_sums = 0
    #     not_in_mission = 0
    #     if proposer in sus_meter.keys():
    #         not_in_mission_sums = 1 - sus_meter[proposer]
    #         sus_meter[proposer] = (sus_meter[proposer] / 2)
    #         sums += sus_meter[proposer]

    #     for i in range(number_of_players):
    #         if i in sus_meter.keys():
    #             if i in mission:
    #                 current_sus = sus_meter[i]
    #                 not_in_mission_sums -= current_sus
    #                 sus_meter[i] = (current_sus/2)
    #                 sums += sus_meter[i]
    #             else:
    #                 not_in_mission += 1
    #     temp = (1 - sums) - not_in_mission_sums
    #     increase = temp / (not_in_mission - 1)

    #     for i in range(number_of_players):
    #         if i in sus_meter.keys():
    #             if i not in mission and i != proposer:
    #                 sus_meter[i] = (sus_meter[i] + increase)
    if betrayals == 0:
        sums = 0
        not_in_mission_sums = 1
        not_in_mission = 0
        if player_number != proposer:
            if proposer in sus_meter.keys():
                not_in_mission_sums -= sus_meter.get(proposer)
                sus_meter[proposer] = (sus_meter.get(proposer) / 2)
                sums += sus_meter.get(proposer)

            for i in range(number_of_players):
                if i in sus_meter.keys():
                    if i in mission:
                        current_sus = sus_meter.get(i)
                        not_in_mission_sums -= current_sus
                        sus_meter[i] = (current_sus/2)
                        sums += sus_meter.get(i)
                    else:
                        not_in_mission += 1
            temp = (1 - sums) - not_in_mission_sums
            increase = temp / (not_in_mission - 1)

            for i in range(number_of_players):
                if i in sus_meter.keys():
                    if i not in mission and i != proposer:
                        sus_meter[i] = (sus_meter.get(i) + increase)
        else:
            for i in range(number_of_players):
                if i in sus_meter.keys():
                    if i in mission:
                        current_sus = sus_meter.get(i)
                        not_in_mission_sums -= current_sus
                        sus_meter[i] = (current_sus/2)
                        sums += sus_meter.get(i)
                    else:
                        not_in_mission += 1
            temp = (1 - sums) - not_in_mission_sums
            increase = temp / not_in_mission
            for i in range(number_of_players):
                if i in sus_meter.keys():
                    if i not in mission:
                        sus_meter[i] = (sus_meter.get(i) + increase)
                    
    # if betrayals == 0:
    #     for i in range(number_of_players):
    #         # People on the mission decrease sus
    #         if i in sus_meter.keys():
    #             if i in mission:
    #                 current_sus = sus_meter[i]
    #                 # print("- " + str(current_sus))
    #                 sus_meter[i] = (current_sus / 1.5)
    #             # People not on the mission increase sus
    #             else:
    #                 current_sus = sus_meter[i]
    #                 sus_meter[i] = (current_sus * 1.5)
    # else:
    #     for i in range(number_of_players):
    #         # People on the mission decrease sus
    #         if i in sus_meter.keys():
    #             if i in mission:
    #                 current_sus = sus_meter[i]
    #                 # print("- " + str(current_sus))
    #                 sus_meter[i] = (current_sus * 1.5)
    #             # People not on the mission increase sus
    #             else:
    #                 current_sus = sus_meter[i]
    #                 sus_meter[i] = (current_sus / 1.5)


def print_result():
    total = 0
    for key, val in sus_meter.items():
        print(" " + str(key) + "   :  " + "{:.2f}".format(val))
        total += val
    print(YELLOW + "total = " + "{:.2f}".format(total) + END)




sus_meter = dict()
number_of_players = 5
player_number = random.randint(0, number_of_players - 1)
print(GREEN + "-- player id = " + str(player_number) + "\n" + END)




for i in range(number_of_players):
    # Do not include oneself as probability of being a spy
    if i == player_number:
        continue
    sus_meter.setdefault(i, 1.0 / (number_of_players - 1))
    # sus_meter[i] = (1.0 / (number_of_players - 1))

#? 1  :  
#  0  :  0.25 -> 0.0
#  2  :  0.25 -> 0.0
#! 3  :  0.25 -> 1.0
#! 4  :  0.25 -> 1.0
            # 

print_result()
mission_outcome([1,3], 4, 0, True)
print("--")
print_result()
mission_outcome([1,3], 4, 0, True)
print("--")
print_result()
mission_outcome([0,4], 4, 0, True)
# mission_outcome([0,4], 2, 1, False)
print("--")
print_result()

print(GREEN + "-- player id = " + str(player_number) + END)
