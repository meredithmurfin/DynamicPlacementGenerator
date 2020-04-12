import copy, logging
import numpy as np
import data

def convert_actions_to_arrays(data):
	logging.info("Converting actions...")
	old_data = data[:]
	new_data = []
	for action in data:
		new_action = []
		for i in range(7):
			action_row = np.asarray(action[:7])
			new_action.append(action_row)
			del action[:7]
		new_data.append(np.array(new_action))
	return new_data

def find_all_possible_actions_for_subtype(num_engines, num_removals_info):
	logging.info("Finding all actions possible for this subtype...")
	all_possible_actions = data.all_possible_actions[num_engines]
	all_possible_actions_for_subtype = []
	max_engines_ATL = num_removals_info['MAX_NUM_REMOVALS_MONTHLY_ATL'] + 1
	max_engines_CVG = num_removals_info['MAX_NUM_REMOVALS_MONTHLY_CVG'] + 1 
	max_engines_DTW = num_removals_info['MAX_NUM_REMOVALS_MONTHLY_DTW'] + 1
	max_engines_LAX = num_removals_info['MAX_NUM_REMOVALS_MONTHLY_LAX'] + 1
	max_engines_MSP = num_removals_info['MAX_NUM_REMOVALS_MONTHLY_MSP'] + 1
	max_engines_SEA = num_removals_info['MAX_NUM_REMOVALS_MONTHLY_SEA'] + 1
	max_engines_SLC = num_removals_info['MAX_NUM_REMOVALS_MONTHLY_SLC'] + 1
	max_engines_hubs = [max_engines_ATL, max_engines_CVG, max_engines_DTW, max_engines_LAX, max_engines_MSP, max_engines_SEA, max_engines_SLC]
	for action in all_possible_actions:
		engines_moved_to_hubs = [sum(x) for x in zip(*action)]
		possible = True
		for i in range(7):
			if engines_moved_to_hubs[i] > max_engines_hubs[i]:
				possible = False
				break
		if possible:
			all_possible_actions_for_subtype.append(action)
	all_possible_actions_for_subtype = np.array(all_possible_actions_for_subtype)
	logging.info("All actions possible for this subtype have been found.")
	return all_possible_actions_for_subtype