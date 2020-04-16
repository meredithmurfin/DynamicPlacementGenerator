from util import reader_util, writer_util, data_util
import data
from pymdptoolbox.src.mdptoolbox import mdp
import numpy as np
import csv, copy, pprint, logging, math

class FiniteHorizonMDPSolver:

	def __init__(self, engine_subtype):
		self.engine_subtype = engine_subtype
		self.num_working_engines = data.engines_info[self.engine_subtype]['NUM_WORKING_ENGINES']
		self.states = data.states_by_subtype[self.engine_subtype]
		self.num_states = len(self.states)
		self.actions = data.actions_by_subtype[self.engine_subtype]
		self.num_actions = len(self.actions)
		self.P = np.zeros((self.num_actions, self.num_states, self.num_states))
		self.R = np.zeros(self.num_states)
		self.set_variables()

	def set_variables(self):
		print()
		logging.info("Solving MDP for: " + self.engine_subtype)
		logging.info("Setting P and R variables for MDP...")
		for state_index in range(self.num_states):
			current_state = self.states[state_index]
			for action_index in range(self.num_actions):
				current_action = self.actions[action_index]
				if self.current_action_is_possible_with_current_state(current_action, current_state):
					self.P[action_index][state_index] = self.get_transition_probabilities_if_current_action_possible(current_action)
				else:
					self.P[action_index][state_index] = self.get_transition_probabilities_if_current_action_not_possible(state_index)
			self.R[state_index] = self.get_reward(current_state)

	def current_action_is_possible_with_current_state(self, current_action, current_state):
		current_state_to_edit = current_state[:]
		# Iterate over every index of the current action
		for engine_from in range(7):
			for engine_to in range(7):
				num_engines_to_move_from_current_hub = current_action[engine_from][engine_to]
				# If the current index indicates engines are moved from one hub to another
				if num_engines_to_move_from_current_hub > 0:
					num_engines_at_current_hub = current_state_to_edit[engine_from]
					# If the number of engines at the hub to move engines from is equal to zero
					if num_engines_at_current_hub == 0:
						return False # The action is not possible
					# If the number of engines to move from the hub is greater than the number of engines at the hub
					elif num_engines_to_move_from_current_hub > num_engines_at_current_hub:
						return False # The action is not possible
					else:
						# Change the current state to edit to reflect the engines being moved from the hub
						current_state_to_edit[engine_from] -= num_engines_to_move_from_current_hub
		return True # The action is possible

	def get_transition_probabilities_if_current_action_possible(self, current_action):
		probabilities = np.zeros((self.num_states,))
		new_state = [0, 0, 0, 0, 0, 0, 0]
		for engine_from in range(7):
			for engine_to in range(7):
				num_engines_to_move_to_hub = current_action[engine_from][engine_to]
				# If the current index indicates engines are moved from one hub to another
				if num_engines_to_move_to_hub > 0:
					# Change new state to reflect engines moved to it in the action
					new_state[engine_to] += num_engines_to_move_to_hub
		new_state_index = self.states.index(new_state)
		# Performing this action on the current state will 100% result in this new state
		probabilities[new_state_index] = 1
		return probabilities

	def get_transition_probabilities_if_current_action_not_possible(self, state_index):
		# Performing this (impossible) action on the current state will 100% result in the SAME state
		probabilities = np.zeros((self.num_states,))
		probabilities[state_index] = 1
		return probabilities

	def get_reward(self, current_state):
		reward_calculator = RewardCalculator(self.engine_subtype, current_state)
		reward = reward_calculator.get_reward()
		return reward

	def solve_MDP(self):
		fh_MDP = mdp.FiniteHorizon(self.P, self.R, discount=0.96, N=3)
		fh_MDP.run()
		print()
		logging.info("MDP RESULTS FOR " + self.engine_subtype + ":")
		print()
		for i in range(self.num_states):
			current_state = self.states[i]
			action_to_take = self.actions[fh_MDP.policy[i][0]]
			if current_state == data.engines_info[self.engine_subtype]['CURRENT_STATE']:
				if self.current_action_is_possible_with_current_state(action_to_take, current_state):
					new_state = [0, 0, 0, 0, 0, 0, 0]
					for engine_from in range(7):
						for engine_to in range(7):
							if action_to_take[engine_from][engine_to] > 0:
								engines_to_move = action_to_take[engine_from][engine_to]
								new_state[engine_to] += engines_to_move
					if current_state != new_state:
						print('Current state: ' + str(current_state))
						print('Best action to take: ')
						print(action_to_take)
						print("New state: " + str(new_state))
						data.engines_info[self.engine_subtype]['CURRENT_STATE'] = new_state
					else:
						print('Current state: ' + str(current_state))
						print('Best action to take: NONE. Keep engines where they are.')
				else:
					print('Current state: ' + str(current_state))
					print('Best action to take: NONE. Keep engines where they are.')

class RewardCalculator():

	def __init__(self, engine_subtype, current_state):
		self.engine_subtype = engine_subtype
		self.current_state = current_state

		self.aos_cost = data.aos_cost[self.engine_subtype]
		self.probability_of_repair = data.probability_of_num_repair_given_num_broken[self.engine_subtype]
		self.expected_transport_cost = data.expected_transport_cost[self.engine_subtype]
		self.num_working_engines = data.engines_info[self.engine_subtype]['NUM_WORKING_ENGINES']
		self.num_broken_engines_ATL = data.engines_info[self.engine_subtype]['NUM_BROKEN_ENGINES_ATL']
		self.num_broken_engines_MSP = data.engines_info[self.engine_subtype]['NUM_BROKEN_ENGINES_MSP']
		self.num_broken_engines_total = (self.num_broken_engines_ATL + self.num_broken_engines_MSP)
		self.all_possible_removal_situations = data.all_possible_removal_situations[self.engine_subtype]
		self.num_departures = data.num_departures_by_hub_monthly[self.engine_subtype]
		self.departure_ground_time = data.total_departures_ground_time_by_state_region_monthly[self.engine_subtype]
		self.RONS_RADS_ground_time = data.total_RONSRADS_ground_time_by_hub_monthly[self.engine_subtype]
		self.regression = data.regression[self.engine_subtype]

		self.total_departure_ground_time = 0
		self.set_total_departure_ground_time_of_locations_without_regression_data()
		self.expected_cost_of_current_state = 0
		self.num_engines_available_at_hubs = {}
		self.set_num_engines_available_at_hubs()
		self.current_num_engines_repaired_ATL = 0 
		self.current_num_engines_repaired_MSP = 0  
		self.current_num_engines_repaired_total = 0
		self.probability_of_current_num_engines_repaired = 0
		self.current_num_removals = 0
		self.current_state_regions_of_removals_and_num_removals = {}
		self.current_state_regions_of_removals_and_removal_probabilities = {}
		self.probability_of_current_removal_situation = 0
		self.num_removals_left_in_iteration = 0
		self.num_engines_available_at_hubs_in_iteration = {}
		self.state_regions_of_removals_and_num_removals_to_edit = {}
		self.state_regions_of_removals_and_removal_probabilities_to_edit = {}
		self.there_are_removals_remaining = True 
		self.there_are_engines_remaining = True 

	def set_total_departure_ground_time_of_locations_without_regression_data(self):
		for location, ground_time in self.departure_ground_time.items():
			self.total_departure_ground_time += (sum(ground_time.values())/3)
		for location in self.regression.keys():
			if location != 'OTHER':
				self.total_departure_ground_time -= (sum(self.departure_ground_time[location].values())/3)

	def set_num_engines_available_at_hubs(self):
		for i in range(7):
			self.num_engines_available_at_hubs[data.hubs[i]] = self.current_state[i]

	def get_reward(self):
		logging.info('Currently finding expected cost associated with spare placement: ' + str(self.current_state))
		self.calculate_expected_cost_of_current_state()
		logging.info('Cost of removal situation found: ' + str(self.expected_cost_of_current_state))
		cost_to_perform_action = self.get_cost_to_perform_action()
		logging.info("Cost of taking the action: " + str(cost_to_perform_action))
		self.expected_cost_of_current_state += cost_to_perform_action
		return self.expected_cost_of_current_state

	def get_cost_to_perform_action(self):
		state_to_transport_from = data.engines_info[self.engine_subtype]['CURRENT_STATE'][:]
		total_cost_of_action = 0 
		current_state_to_edit = self.current_state[:]
		possible_moves = {} 
		for transport_to in range(7): # Index of num engines in new state
			if current_state_to_edit[transport_to] > 0: # If there are engines at this hub in the new state
				possible_moves[data.hubs[transport_to]] = {} # Update possible_moves to include this hub as a place where engines need to be transported to
				for transport_from in range(7): # Index of num engines in previous state
					if state_to_transport_from[transport_from] > 0: # If there are engines at this hub in the previous state
						# Add this hub as a place that could potentially transport an engine to the current hub needed to transport engines to 
						# The value is the cost to move an engine from this hub to the hub that needs an engine
						possible_moves[data.hubs[transport_to]][data.hubs[transport_from]] = self.expected_transport_cost[data.hubs[transport_to]][data.hubs[transport_from]]
		engines_need_to_be_transported = True 
		while engines_need_to_be_transported:
			min_transportation_cost = -1 # Keep track of the next engine transport with the minimum cost
			transport_to_hub = '' # Hub to transport engine to with minimum cost
			transport_from_hub = '' # Hub to transport engine from with minimum cost
			for transport_to, transport_from_and_cost in possible_moves.items(): # For every possible move
				costs_of_current_transport_to = list(transport_from_and_cost.values()) 
				current_hubs_to_transport_from = list(transport_from_and_cost.keys())
				min_cost_of_current_transport_to = min(costs_of_current_transport_to) # Find the engine transport with the minimum cost for this hub to transport to
				# If min_transportation_cost has not been set yet OR if the current possible engine transport is less than the min_transportation_cost
				if (min_transportation_cost == -1) or (min_cost_of_current_transport_to < min_transportation_cost):
					min_transportation_cost = min_cost_of_current_transport_to # Set new minimum cost
					transport_to_hub = transport_to
					transport_from_hub = current_hubs_to_transport_from[costs_of_current_transport_to.index(min_cost_of_current_transport_to)]
			# Reset variables to reflect the transport of this engine 
			total_cost_of_action += min_transportation_cost
			transport_to_hub_index = data.hubs.index(transport_to_hub)
			current_state_to_edit[transport_to_hub_index] -= 1
			if current_state_to_edit[transport_to_hub_index] == 0:
				del possible_moves[transport_to_hub]
			transport_from_hub_index = data.hubs.index(transport_from_hub)	
			state_to_transport_from[transport_from_hub_index] -= 1
			if state_to_transport_from[transport_from_hub_index] == 0:
				for hub_to in possible_moves.keys():
					del possible_moves[hub_to][transport_from_hub]
			if len(possible_moves) == 0: # If there are no more engines to transport
				engines_need_to_be_transported = False
		return total_cost_of_action

	def calculate_expected_cost_of_current_state(self):
		# Iterate over the number of engines that could be repaired at ATL given the current number of engines broken at ATL
		for num_engines_repaired_ATL in range(self.num_broken_engines_ATL+1):
			# Iterate over the number of engines that could be repaired at MSP given the current number of engines broken at MSP
			for num_engines_repaired_MSP in range(self.num_broken_engines_MSP+1):
				self.set_current_engines_repaired_variables(num_engines_repaired_ATL, num_engines_repaired_MSP)
				self.get_current_probability_of_num_engines_repaired()
				self.consider_repaired_engines_as_working_engines_in_num_engines_available_at_hubs()
				self.look_at_all_possible_ways_in_which_removals_can_happen()
				self.reset_num_engines_available_at_hubs()

	def set_current_engines_repaired_variables(self, num_engines_repaired_ATL, num_engines_repaired_MSP):
		self.current_num_engines_repaired_ATL = num_engines_repaired_ATL
		self.current_num_engines_repaired_MSP = num_engines_repaired_MSP
		self.current_num_engines_repaired_total = (self.current_num_engines_repaired_ATL + self.current_num_engines_repaired_MSP)

	def get_current_probability_of_num_engines_repaired(self):
		# There's a probability associated with a possible repair only if engines are broken
		self.probability_of_current_num_engines_repaired = 0
		if self.num_broken_engines_total > 0:
			self.probability_of_current_num_engines_repaired = self.probability_of_repair[self.num_broken_engines_total][self.current_num_engines_repaired_total] 

	def consider_repaired_engines_as_working_engines_in_num_engines_available_at_hubs(self):
		self.num_engines_available_at_hubs['ATL'] += self.current_num_engines_repaired_ATL
		self.num_engines_available_at_hubs['MSP'] += self.current_num_engines_repaired_MSP

	def reset_num_engines_available_at_hubs(self):
		self.num_engines_available_at_hubs['ATL'] -= self.current_num_engines_repaired_ATL
		self.num_engines_available_at_hubs['MSP'] -= self.current_num_engines_repaired_MSP

	def look_at_all_possible_ways_in_which_removals_can_happen(self):
		# Iterate over ever possible removal situation given the current number of total removals
		for possible_removal_situation in self.all_possible_removal_situations:
			self.current_num_removals = sum(list(map(int, possible_removal_situation)))
			# Find the probability to multiply to the cost of this removal situation
			self.set_current_probability_of_removal_situation(possible_removal_situation)
			# Find total cost of all actions taken this month based on the current removal situation
			total_cost_of_current_removal_situation = 0
			if self.probability_of_current_removal_situation > 0:
				total_cost_of_current_removal_situation = self.get_total_cost_of_current_removal_situation()
			probability_to_multiply = self.probability_of_current_removal_situation
			if self.num_broken_engines_total > 0:
				probability_to_multiply = (self.probability_of_current_removal_situation * self.probability_of_current_num_engines_repaired)
			# Multiply the cost of this situation by the probability of it happening
			cost_of_possible_removal = (probability_to_multiply * total_cost_of_current_removal_situation)
			# Then add that value to the total expected cost for this spare engine placement
			self.expected_cost_of_current_state += cost_of_possible_removal

	def set_current_probability_of_removal_situation(self, removal_situation):
		self.probability_of_current_removal_situation = -1
		self.current_state_regions_of_removals_and_num_removals = {}
		self.current_state_regions_of_removals_and_removal_probabilities = {}
		for i in range(53):
			num_removals_in_state_region = int(removal_situation[i])
			if (num_removals_in_state_region > 0): # If at least 1 removal occurs in this state region
				state_region_of_removal = data.state_regions[i] 
				probability = self.get_probability_of_removal(state_region_of_removal, num_removals_in_state_region)
				self.current_state_regions_of_removals_and_num_removals[state_region_of_removal] = num_removals_in_state_region
				self.current_state_regions_of_removals_and_removal_probabilities[state_region_of_removal] = self.get_probability_of_removal(state_region_of_removal, 1)
				if probability == 0:
					self.probability_of_current_removal_situation = 0
					break
				elif (self.probability_of_current_removal_situation == -1):
					self.probability_of_current_removal_situation = probability
				else:
					self.probability_of_current_removal_situation *= probability 
			else: # If no removals occur in this state region
				state_region = data.state_regions[i]
				probability = self.get_probability_of_removal(state_region, 0)
				if probability == 0:
					self.probability_of_current_removal_situation = 0
					break
				elif (self.probability_of_current_removal_situation == -1):
					self.probability_of_current_removal_situation = probability
				else:
					self.probability_of_current_removal_situation *= probability 

	def get_probability_of_removal(self, state_region_location, num_removals):
		if state_region_location in data.hubs:
			if state_region_location in self.regression: # Location is a hub and there is regression available for the hub
				probability = self.get_probability_if_location_is_hub(state_region_location, num_removals)
			else: # Location is a hub but it has to be considered "other" for regression
				if 'OTHER' in self.regression:	
					probability = self.get_probability_if_location_is_hub_but_no_regression_is_available_for_hub(state_region_location, num_removals)
				else:
					if (num_removals == 0):
						return 1
					return 0	
		else: # Location is NOT a hub and is considered "other" for regression
			if 'OTHER' in self.regression:	
				probability = self.get_probability_if_location_is_non_hub(state_region_location, num_removals)
			else:
				if (num_removals == 0):
					return 1
				return 0	
		return probability

	def get_probability_if_location_is_hub(self, state_region_location, num_removals):
		current_RONS_RADS_ground_time = (sum(self.RONS_RADS_ground_time[state_region_location].values())/3)
		current_num_departures = (sum(self.num_departures[state_region_location].values())/3)
		RR, D, intercept = self.get_coefficients(state_region_location)
		l = math.exp((RR * current_RONS_RADS_ground_time) + (D * current_num_departures) + intercept)
		if l > data.removals_info[self.engine_subtype]['MAX_NUM_REMOVALS_MONTHLY_' + state_region_location]:
			l = data.removals_info[self.engine_subtype]['MAX_NUM_REMOVALS_MONTHLY_' + state_region_location]
		probability = (math.exp(-l) * (l ** num_removals)) / math.factorial(num_removals)
		return probability

	def get_probability_if_location_is_hub_but_no_regression_is_available_for_hub(self, state_region_location, num_removals):
		current_RONS_RADS_ground_time = (sum(self.RONS_RADS_ground_time[state_region_location].values())/3)
		current_departure_ground_time = (sum(self.departure_ground_time[state_region_location].values())/3)
		current_num_departures = (sum(self.num_departures[state_region_location].values())/3)	
		RR, D, intercept = self.get_coefficients('OTHER')
		l = math.exp((RR * current_RONS_RADS_ground_time) + (D * current_num_departures) + intercept)	
		l = (l * current_departure_ground_time) / self.total_departure_ground_time
		if l > data.removals_info[self.engine_subtype]['MAX_NUM_REMOVALS_MONTHLY_' + state_region_location]:
			l = data.removals_info[self.engine_subtype]['MAX_NUM_REMOVALS_MONTHLY_' + state_region_location]
		probability = (math.exp(-l) * (l ** num_removals)) / math.factorial(num_removals)
		return probability

	def get_probability_if_location_is_non_hub(self, state_region_location, num_removals):
		current_RONS_RADS_ground_time = (sum(self.RONS_RADS_ground_time['OTHER'].values())/3)
		current_departure_ground_time = (sum(self.departure_ground_time[state_region_location].values())/3)
		current_num_departures = (sum(self.num_departures['OTHER'].values())/3)	
		RR, D, intercept = self.get_coefficients('OTHER')
		l = math.exp((RR * current_RONS_RADS_ground_time) + (D * current_num_departures) + intercept)	
		l = (l * current_departure_ground_time) / self.total_departure_ground_time
		if l > data.removals_info[self.engine_subtype]['MAX_NUM_REMOVALS_MONTHLY_NON_HUBS']:
			l = data.removals_info[self.engine_subtype]['MAX_NUM_REMOVALS_MONTHLY_NON_HUBS']
		probability = (math.exp(-l) * (l ** num_removals)) / math.factorial(num_removals)
		return probability

	def get_coefficients(self, location):
		RR = self.regression[location]['RR']
		D = self.regression[location]['D']
		intercept = self.regression[location]['intercept']
		return RR, D, intercept

	def get_total_cost_of_current_removal_situation(self):
		self.there_are_removals_remaining = True 
		self.there_are_engines_remaining = True 
		# If there are no engines to place AND there are none that are being considered to be repaired during this month, then there are no engines remaining to allocate for any removals
		if (self.num_working_engines == 0) and (self.current_num_engines_repaired_total == 0):
			self.there_are_engines_remaining = False
		# Store data to change throughout iteration
		self.num_removals_left_in_iteration = self.current_num_removals
		self.num_engines_available_at_hubs_in_iteration = copy.deepcopy(self.num_engines_available_at_hubs)
		self.state_regions_of_removals_and_num_removals_to_edit = copy.deepcopy(self.current_state_regions_of_removals_and_num_removals)
		self.state_regions_of_removals_and_removal_probabilities_to_edit = copy.deepcopy(self.current_state_regions_of_removals_and_removal_probabilities)
		total_cost_of_current_removal_situation = 0 # sum up the total cost of all the actions taken in the month
		# While there are removals remaining to happen AND engines remaining to service those removals
		while self.there_are_removals_remaining and self.there_are_engines_remaining:
			cost_of_removal, location_of_removal, hub_to_service_removal = self.cost_to_service_removal_from_hub_with_min_transport_cost()
			total_cost_of_current_removal_situation += cost_of_removal
			self.reset_variables_to_reflect_action_for_this_removal(cost_of_removal, location_of_removal, hub_to_service_removal)
			if self.rest_of_removals_have_no_possibility_of_happening():
				self.there_are_removals_remaining = False
		if self.there_are_removals_remaining:
			# If there are removals remaining but no engines are available to service it, incure an AOS cost for the remaining removals
			total_cost_of_current_removal_situation += (self.num_removals_left_in_iteration * self.aos_cost)
		return total_cost_of_current_removal_situation

	def rest_of_removals_have_no_possibility_of_happening(self):
		if sum(self.state_regions_of_removals_and_removal_probabilities_to_edit.values()) == 0:
			return True 
		return False

	def cost_to_service_removal_from_hub_with_min_transport_cost(self):
		removal_probabilities = list(self.state_regions_of_removals_and_removal_probabilities_to_edit.values()) # List all probabilities of the remaining removals
		regions = list(self.state_regions_of_removals_and_removal_probabilities_to_edit.keys()) # List all state regions where removals are left to occur
		# Get state region of removal that has the highest probability of occurring
		state_region_of_next_removal = regions[removal_probabilities.index(max(removal_probabilities))]
		# Reset data for this removal
		cost_to_service_removal_from_hub_with_min_transport_cost = -1
		hub_with_min_cost = ''
		for hub_of_engine, num_engines_at_hub in self.num_engines_available_at_hubs_in_iteration.items(): # for every hub
			if num_engines_at_hub > 0: # If that hub has an engine available to service the removal
				# Find the cost to transport that engine from the hub to the state region
				cost_to_transport = self.expected_transport_cost[state_region_of_next_removal][hub_of_engine]
				if (cost_to_service_removal_from_hub_with_min_transport_cost == -1) or (cost_to_transport < cost_to_service_removal_from_hub_with_min_transport_cost):
					cost_to_service_removal_from_hub_with_min_transport_cost = cost_to_transport
					hub_with_min_cost = hub_of_engine
		return cost_to_service_removal_from_hub_with_min_transport_cost, state_region_of_next_removal, hub_with_min_cost

	def reset_variables_to_reflect_action_for_this_removal(self, cost_of_removal, location_of_removal, hub_to_service_removal):
		# Remove removal from dictionary being iterated
		self.state_regions_of_removals_and_num_removals_to_edit[location_of_removal] -= 1
		# True if there are no more removals remaining to occur for this state region, false otherwise
		if (self.state_regions_of_removals_and_num_removals_to_edit[location_of_removal] == 0):
			# Delete state region from both dictionaries 
			del self.state_regions_of_removals_and_num_removals_to_edit[location_of_removal]
			del self.state_regions_of_removals_and_removal_probabilities_to_edit[location_of_removal]
		else: # If there is a removal for this state region that still needs to happen
			# Find the number of removals that have already occurred for this region
			removals_that_have_occurred_in_this_region = (self.current_state_regions_of_removals_and_num_removals[location_of_removal] - self.state_regions_of_removals_and_num_removals_to_edit[location_of_removal])
			# Reset the probability associated with the next removal for this state region to match what number in sequence it will be
			self.state_regions_of_removals_and_removal_probabilities_to_edit[location_of_removal] = self.get_probability_of_removal(location_of_removal, (removals_that_have_occurred_in_this_region+1))
		# Subtract 1 removal from the total number of removals currently iterating
		self.num_removals_left_in_iteration -= 1
		# True if there are NO removals remaining to occur in the current month, false otherwise
		if (self.num_removals_left_in_iteration == 0):
			self.there_are_removals_remaining = False
		# Remove this engine from dictionary being iterated because the engine has just been used for this removal
		self.num_engines_available_at_hubs_in_iteration[hub_to_service_removal] -= 1
		# Get number of engines still available
		engines_available = sum(self.num_engines_available_at_hubs_in_iteration.values()) 
		if (engines_available == 0): # True if there are NO engines available to service removals, false otherwise
			self.there_are_engines_remaining = False














