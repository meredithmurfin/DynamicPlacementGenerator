import data
import copy, logging
import numpy as np

def minimize_states_and_actions_to_iterate():
	logging.info("Minimizing states and actions to iterate for each engine type...")
	for engine_subtype in data.engine_subtypes:
		num_working_engines = data.engines_info[engine_subtype]['NUM_WORKING_ENGINES']
		current_state = data.engines_info[engine_subtype]['CURRENT_STATE'][:]
		if num_working_engines > 3: 
			data.states_by_subtype[engine_subtype] = get_unique_list_of_lists(minimize_states(current_state, num_working_engines))[:]
			data.actions_by_subtype[engine_subtype] = minimize_actions(current_state, num_working_engines)
		else:
			data.states_by_subtype[engine_subtype] = get_unique_list_of_lists(data.all_possible_states[num_working_engines])[:]
			data.actions_by_subtype[engine_subtype] = data.all_possible_actions[num_working_engines][:]
	logging.info("The number of states and actions to iterate have been minimized.")
 
def get_unique_list_of_lists(a_list):
	unique_list_of_lists = []
	for l in a_list:
		if l not in unique_list_of_lists:
			unique_list_of_lists.append(l)
	return unique_list_of_lists

def minimize_states(current_state, num_working_engines):
	max_num_engines_currently_at_any_hub = max(current_state)
	all_states = data.all_possible_states[num_working_engines]
	states_minimized = []
	if max_num_engines_currently_at_any_hub > 1: # If at least one hub currently has more than 1 engine
		num_hubs_with_max_num_engines = current_state.count(max_num_engines_currently_at_any_hub)
		if num_hubs_with_max_num_engines > 1: # If more than one hub currently has more than 1 engine
			indices_of_hubs_with_max_num_engines = [i for i, num in enumerate(current_state) if num == max_num_engines_currently_at_any_hub]
			indices_of_hubs_with_max_num_engines.sort()
			for state in all_states: # For every possible state being considered
				state_to_edit = state[:]
				num_engines_at_hubs_with_max_num_engines = []
				for i in reversed(indices_of_hubs_with_max_num_engines):
					num_engines_at_hubs_with_max_num_engines.append(state_to_edit.pop(i))
				# If at least 1 engine is at each hub with maximum number of engines allowed AND all other hubs have 3 or less engines
				if all(num >= 1 for num in num_engines_at_hubs_with_max_num_engines) and (max(state_to_edit) <= 3):
					states_minimized.append(state)
		else: # If one hub currently has more than 1 engine 
			index_of_hub_with_max_num_engines = current_state.index(max_num_engines_currently_at_any_hub)
			for state in all_states: # For every possible state being considered
				state_to_edit = state[:]
				num_at_hub_with_max_num_engines = state_to_edit.pop(index_of_hub_with_max_num_engines)
				# If at least 1 engine is at hub with maximum number of engines allowed AND all other hubs have 3 or less engines
				if (num_at_hub_with_max_num_engines >= 1) and (max(state_to_edit) <= 3):
					states_minimized.append(state)
	else: # If there is max 1 engine currently at any hub
		for state in all_states:
			if max(state) <= 3: # If no more than 3 engines are at any one hub for the new state
				states_minimized.append(state)
	return states_minimized

def minimize_actions(current_state, num_working_engines):
	all_actions = data.all_possible_actions[num_working_engines][:]
	actions_minimized = []
	for action in all_actions:
		current_state_to_edit = current_state[:]
		valid = True
		for engine_from in range(7):
			for engine_to in range(7):
				if valid:
					num_engines_to_move = action[engine_from][engine_to]
					# If the current index indicates engines are moved from one hub to another
					if num_engines_to_move > 0:
						num_engines_at_current_hub = current_state_to_edit[engine_from]
						# If the number of engines at the hub to move engines from is equal to zero
						if num_engines_at_current_hub == 0:
							valid = False # The action is not valid
						# If the number of engines to move from the hub is greater than the number of engines at the hub
						elif num_engines_to_move > num_engines_at_current_hub:
							valid = False # The action is not valid
						else:
							# Edit the current state to reflect the engines being moved from the hub
							current_state_to_edit[engine_from] -= num_engines_to_move
		if valid:
			actions_minimized.append(action)
	actions_minimized = np.array(actions_minimized)
	return actions_minimized

def validate_removal_and_engine_info():
	for engine_subtype in data.engine_subtypes:
		assert (engine_subtype in data.aos_cost), "No AOS cost was provided for " + engine_subtype + " in the removal_info file. Please provide ALL info for this engine subtype in the removal_info file."
		assert (data.aos_cost[engine_subtype] > 0), "AOS cost for " + engine_subtype + " is not set to a positive value. Please provide a positive value indicating the expected AOS cost for this engine type in the removal_info file."
		assert (engine_subtype in data.engines_info), "No engine data was provided for " + engine_subtype + " in the engine_info file. Please provide ALL info for this engine subtype in the engine_info file."
		assert (data.engines_info[engine_subtype]['TOTAL_NUM_ENGINES'] <= 5), "The program is limited to running only for engine types with 5 or less total engines. The " + engine_subtype + " has more than 5 engines."
		total_engines = data.engines_info[engine_subtype]['NUM_WORKING_ENGINES'] + data.engines_info[engine_subtype]['NUM_BROKEN_ENGINES_ATL'] + data.engines_info[engine_subtype]['NUM_BROKEN_ENGINES_MSP']
		assert (data.engines_info[engine_subtype]['TOTAL_NUM_ENGINES'] == total_engines), "The total number of engines does not equal the sum of engines working, engines broken at ATL, and engines broken at MSP for the " + engine_subtype + ". Make sure the value in the TOTAL_NUM_ENGINES column is equal to the sum of values in the TOTAL_NUM_WORKING, NUM_BROKEN_ATL, and NUM_BROKEN_MSP columns."
		assert (data.engines_info[engine_subtype]['NUM_WORKING_ENGINES'] == sum(data.engines_info[engine_subtype]['CURRENT_STATE'])), "The number of working engines does not equal the sum of engines currently at each hub for the " + engine_subtype + ". Make sure the value in the TOTAL_NUM_WORKING column is equal to the sum of values in the NUM_WORKING columns for each hub."

def validate_engine_subtype_data():
	pass







