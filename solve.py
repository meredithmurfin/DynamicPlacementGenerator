import numpy as np
from util import reader_util, writer_util, data_util
import data
import csv, copy, pprint, logging, math
from pymdptoolbox.src.mdptoolbox import mdp
import math



class FiniteHorizonMDPSolver:

	def __init__(self, engine_subtype, all_possible_actions_for_subtype, month_to_run):
		self.engine_subtype = engine_subtype
		self.num_working_engines = data.num_engines_info[self.engine_subtype]['NUM_WORKING_ENGINES']
		self.states = data.all_possible_states[self.num_working_engines][:]
		self.num_states = len(self.states)
		self.actions = all_possible_actions_for_subtype
		self.num_actions = len(self.actions)
		self.P = np.zeros((self.num_actions, self.num_states, self.num_states))
		self.R = np.zeros(self.num_states)
		self.month_to_run = month_to_run
		self.set_variables()

	def set_variables(self):
		logging.info("Solving MDP for: " + self.engine_subtype + ", for time period: " + str(self.month_to_run))
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
						# change the current state to edit to reflect the engines being moved from the hub
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
					# change new state to reflect engines moved to it in the action
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
		reward_calculator = RewardCalculator(self.engine_subtype, current_state, self.month_to_run)
		reward = reward_calculator.get_reward()
		return reward

	def solve_MDP(self):
		fh_MDP = mdp.FiniteHorizon(self.P, self.R, discount=0.96, N=3)
		fh_MDP.run()
		logging.info("MDP RESULTS FOR: " + self.engine_subtype)
		print()
		for i in range(self.num_states):
			current_state = self.states[i]
			action_to_take = self.actions[fh_MDP.policy[i][0]]
			if self.current_action_is_possible_with_current_state(action_to_take, current_state):
				print('Current state: ' + str(current_state))
				print('Best action to take: ')
				print(action_to_take)
				new_state = [0, 0, 0, 0, 0, 0, 0]
				for engine_from in range(7):
					for engine_to in range(7):
						if action_to_take[engine_from][engine_to] > 0:
							engines_to_move = action_to_take[engine_from][engine_to]
							print("Move " + str(engines_to_move) + " engines to " + data.hubs[engine_to] + ".")
							new_state[engine_to] += engines_to_move
				print("New state: " + str(new_state))

			else:
				print('Current state: ' + str(current_state))
				print('Best action to take: NONE. Keep engines where they are.')
			print()

class RewardCalculator():

	def __init__(self, engine_subtype, current_state, month_to_run):
		# constant variables
		self.engine_subtype = engine_subtype
		self.current_state = current_state
		self.month_to_run = month_to_run
		self.aos_cost = data.aos_cost[self.engine_subtype]
		self.probability_of_repair = data.probability_of_num_repair_given_num_broken[self.engine_subtype]
		self.expected_transport_cost = data.expected_transport_cost[self.engine_subtype]
		self.num_working_engines = data.num_engines_info[self.engine_subtype]['NUM_WORKING_ENGINES']
		self.num_broken_engines_ATL = data.num_engines_info[self.engine_subtype]['NUM_BROKEN_ENGINES_ATL']
		self.num_broken_engines_MSP = data.num_engines_info[self.engine_subtype]['NUM_BROKEN_ENGINES_MSP']
		self.num_broken_engines_total = (self.num_broken_engines_ATL + self.num_broken_engines_MSP)
		self.all_possible_removal_situations = data.all_possible_removal_situations[self.engine_subtype]
		self.num_departures = data.num_departures_by_hub_monthly[self.engine_subtype][self.month_to_run]
		self.departure_ground_time = data.total_departures_ground_time_by_state_region_monthly[self.engine_subtype][self.month_to_run]
		self.RONS_RADS_ground_time = data.total_RONSRADS_ground_time_by_hub_monthly[self.engine_subtype][self.month_to_run]
		self.regression = data.regression[self.engine_subtype]
		self.total_departure_ground_time = 0
		self.set_total_departure_ground_time_of_locations_without_regression_data()
		self.expected_cost_of_current_state = 0
		self.num_engines_available_at_hubs = {}
		self.set_num_engines_available_at_hubs()
		# changing variables
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
		logging.info('Cost found: ' + str(self.expected_cost_of_current_state))
		return self.expected_cost_of_current_state

	def calculate_expected_cost_of_current_state(self):
		# iterate over the number of engines that could be repaired at ATL given the current number of engines broken at ATL
		for num_engines_repaired_ATL in range(self.num_broken_engines_ATL+1):
			# iterate over the number of engines that could be repaired at MSP given the current number of engines broken at MSP
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
		# there's a probability associated with a possible repair only if engines are broken
		self.probability_of_current_num_engines_repaired = 0
		if self.num_broken_engines_total > 0:
			self.probability_of_current_num_engines_repaired = self.probability_of_repair[self.num_broken_engines_total][self.current_num_engines_repaired_total] # P(Qm = qm)

	def consider_repaired_engines_as_working_engines_in_num_engines_available_at_hubs(self):
		self.num_engines_available_at_hubs['ATL'] += self.current_num_engines_repaired_ATL
		self.num_engines_available_at_hubs['MSP'] += self.current_num_engines_repaired_MSP

	def reset_num_engines_available_at_hubs(self):
		self.num_engines_available_at_hubs['ATL'] -= self.current_num_engines_repaired_ATL
		self.num_engines_available_at_hubs['MSP'] -= self.current_num_engines_repaired_MSP

	def look_at_all_possible_ways_in_which_removals_can_happen(self):
		'''
		given the max number of removals, iterate over all possible removal locations with the following constraints:
		- no more than 2 removals can happen outside of hubs
		- no more than 4 removals can happen at one hub
		'''
		# iterate over ever possible removal situation given the current number of total removals
		for possible_removal_situation in self.all_possible_removal_situations:
			self.current_num_removals = sum(list(map(int, possible_removal_situation)))
			# find the probability to multiply to the cost of this removal situation
			self.set_current_probability_of_removal_situation(possible_removal_situation)
			# find total cost of all actions taken this month based on the current removal situation
			
			total_cost_of_current_removal_situation = 0
			if self.probability_of_current_removal_situation > 0:
				total_cost_of_current_removal_situation = self.get_total_cost_of_current_removal_situation()
			
			probability_to_multiply = self.probability_of_current_removal_situation
			if self.num_broken_engines_total > 0:
				probability_to_multiply = (self.probability_of_current_removal_situation * self.probability_of_current_num_engines_repaired)
			# multiply the cost of this situation by the probability of it happening
			cost_of_possible_removal = (probability_to_multiply * total_cost_of_current_removal_situation)
			# then add that value to the total expected cost for this spare engine placement
			self.expected_cost_of_current_state += cost_of_possible_removal

	def set_current_probability_of_removal_situation(self, removal_situation):
		self.probability_of_current_removal_situation = -1 # P(Xs = xs)
		self.current_state_regions_of_removals_and_num_removals = {}
		self.current_state_regions_of_removals_and_removal_probabilities = {}
		for i in range(53):
			num_removals_in_state_region = int(removal_situation[i])
			if (num_removals_in_state_region > 0):
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
			else: # if no removals occur in this state region
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
			if state_region_location in self.regression: # location is a hub and there is regression available for the hub
				current_RONS_RADS_ground_time = (sum(self.RONS_RADS_ground_time[state_region_location].values())/3)
				current_num_departures = (sum(self.num_departures[state_region_location].values())/3)
				RR = self.regression[state_region_location]['RR']
				D = self.regression[state_region_location]['D']
				intercept = self.regression[state_region_location]['intercept']
				l = math.exp((RR * current_RONS_RADS_ground_time) + (D * current_num_departures) + intercept)
				if l > data.num_removals_info[self.engine_subtype]['MAX_NUM_REMOVALS_MONTHLY_' + state_region_location]:
					l = data.num_removals_info[self.engine_subtype]['MAX_NUM_REMOVALS_MONTHLY_' + state_region_location]
				probability = (math.exp(-l) * (l ** num_removals)) / math.factorial(num_removals)
				return probability
			else: # location is a hub but it has to be considered "other" for regression
				if 'OTHER' in self.regression:	
					current_RONS_RADS_ground_time = (sum(self.RONS_RADS_ground_time[state_region_location].values())/3)
					current_departure_ground_time = (sum(self.departure_ground_time[state_region_location].values())/3)
					current_num_departures = (sum(self.num_departures[state_region_location].values())/3)	
					RR = self.regression['OTHER']['RR']
					D = self.regression['OTHER']['D']
					intercept = self.regression['OTHER']['intercept']
					l = math.exp((RR * current_RONS_RADS_ground_time) + (D * current_num_departures) + intercept)	
					l = (l * current_departure_ground_time) / self.total_departure_ground_time
					if l > data.num_removals_info[self.engine_subtype]['MAX_NUM_REMOVALS_MONTHLY_' + state_region_location]:
						l = data.num_removals_info[self.engine_subtype]['MAX_NUM_REMOVALS_MONTHLY_' + state_region_location]
					probability = (math.exp(-l) * (l ** num_removals)) / math.factorial(num_removals)
					return probability
				else:
					if (num_removals == 0):
						return 1
					return 0	
		else: # location is NOT a hub and is considered "other" for regression
			if 'OTHER' in self.regression:	
				current_RONS_RADS_ground_time = (sum(self.RONS_RADS_ground_time['OTHER'].values())/3)
				current_departure_ground_time = (sum(self.departure_ground_time[state_region_location].values())/3)
				current_num_departures = (sum(self.num_departures['OTHER'].values())/3)	
				RR = self.regression['OTHER']['RR']
				D = self.regression['OTHER']['D']
				intercept = self.regression['OTHER']['intercept']
				l = math.exp((RR * current_RONS_RADS_ground_time) + (D * current_num_departures) + intercept)	
				l = (l * current_departure_ground_time) / self.total_departure_ground_time
				if l > data.num_removals_info[self.engine_subtype]['MAX_NUM_REMOVALS_MONTHLY_NON_HUBS']:
					l = data.num_removals_info[self.engine_subtype]['MAX_NUM_REMOVALS_MONTHLY_NON_HUBS']
				probability = (math.exp(-l) * (l ** num_removals)) / math.factorial(num_removals)
				return probability
			else:
				if (num_removals == 0):
					return 1
				return 0	

	def get_total_cost_of_current_removal_situation(self):
		self.there_are_removals_remaining = True 
		self.there_are_engines_remaining = True 
		# if there are no engines to place AND there are none that are being considered to be repaired during this month, then there are no engines remaining to allocate for any removals
		if (self.num_working_engines == 0) and (self.current_num_engines_repaired_total == 0):
			self.there_are_engines_remaining = False
		# store data to change throughout iteration
		self.num_removals_left_in_iteration = self.current_num_removals
		self.num_engines_available_at_hubs_in_iteration = copy.deepcopy(self.num_engines_available_at_hubs)
		self.state_regions_of_removals_and_num_removals_to_edit = copy.deepcopy(self.current_state_regions_of_removals_and_num_removals)
		self.state_regions_of_removals_and_removal_probabilities_to_edit = copy.deepcopy(self.current_state_regions_of_removals_and_removal_probabilities)
		total_cost_of_current_removal_situation = 0 # sum up the total cost of all the actions taken in the month
		# while there are removals remaining to happen AND engines remaining to service those removals
		while self.there_are_removals_remaining and self.there_are_engines_remaining:
			cost_of_removal, location_of_removal, hub_to_service_removal = self.cost_to_service_removal_from_hub_with_min_transport_cost()
			total_cost_of_current_removal_situation += cost_of_removal
			self.reset_variables_to_reflect_action_for_this_removal(cost_of_removal, location_of_removal, hub_to_service_removal)
			if self.rest_of_removals_have_no_possibility_of_happening():
				self.there_are_removals_remaining = False

		if self.there_are_removals_remaining:
			# if there are removals remaining but no engines are available to service it, incure an AOS cost for the remaining removals
			total_cost_of_current_removal_situation += (self.num_removals_left_in_iteration * self.aos_cost)
		return total_cost_of_current_removal_situation

	def rest_of_removals_have_no_possibility_of_happening(self):
		if sum(self.state_regions_of_removals_and_removal_probabilities_to_edit.values()) == 0:
			return True 
		return False

	def cost_to_service_removal_from_hub_with_min_transport_cost(self):
		removal_probabilities = list(self.state_regions_of_removals_and_removal_probabilities_to_edit.values()) # list all probabilities of the remaining removals
		regions = list(self.state_regions_of_removals_and_removal_probabilities_to_edit.keys()) # list all state regions where removals are left to occur
		# get state region of removal that has the highest probability of occurring
		state_region_of_next_removal = regions[removal_probabilities.index(max(removal_probabilities))]
		# reset data for this removal
		cost_to_service_removal_from_hub_with_min_transport_cost = -1
		hub_with_min_cost = ''
		for hub_of_engine, num_engines_at_hub in self.num_engines_available_at_hubs_in_iteration.items(): # for every hub
			if num_engines_at_hub > 0: # if that hub has an engine available to service the removal
				# find the cost to transport that engine from the hub to the state region
				cost_to_transport = self.expected_transport_cost[state_region_of_next_removal][hub_of_engine]
				if (cost_to_service_removal_from_hub_with_min_transport_cost == -1) or (cost_to_transport < cost_to_service_removal_from_hub_with_min_transport_cost):
					cost_to_service_removal_from_hub_with_min_transport_cost = cost_to_transport
					hub_with_min_cost = hub_of_engine
		return cost_to_service_removal_from_hub_with_min_transport_cost, state_region_of_next_removal, hub_with_min_cost

	def reset_variables_to_reflect_action_for_this_removal(self, cost_of_removal, location_of_removal, hub_to_service_removal):
		# remove removal from dictionary being iterated
		self.state_regions_of_removals_and_num_removals_to_edit[location_of_removal] -= 1
		# true if there are no more removals remaining to occur for this state region, false otherwise
		if (self.state_regions_of_removals_and_num_removals_to_edit[location_of_removal] == 0):
			# delete state region from both dictionaries 
			del self.state_regions_of_removals_and_num_removals_to_edit[location_of_removal]
			del self.state_regions_of_removals_and_removal_probabilities_to_edit[location_of_removal]
		else: # if there is a removal for this state region that still needs to happen
			# find the number of removals that have already occurred for this region
			removals_that_have_occurred_in_this_region = (self.current_state_regions_of_removals_and_num_removals[location_of_removal] - self.state_regions_of_removals_and_num_removals_to_edit[location_of_removal])
			# reset the probability associated with the next removal for this state region to match what number in sequence it will be
			self.state_regions_of_removals_and_removal_probabilities_to_edit[location_of_removal] = self.get_probability_of_removal(location_of_removal, (removals_that_have_occurred_in_this_region+1))
		# subtract 1 removal from the total number of removals currently iterating
		self.num_removals_left_in_iteration -= 1
		# true if there are NO removals remaining to occur in the current month, false otherwise
		if (self.num_removals_left_in_iteration == 0):
			self.there_are_removals_remaining = False
		# remove this engine from dictionary being iterated because the engine has just been used for this removal
		self.num_engines_available_at_hubs_in_iteration[hub_to_service_removal] -= 1
		# get number of engines still available
		engines_available = sum(self.num_engines_available_at_hubs_in_iteration.values()) 
		if (engines_available == 0): # true if there are NO engines available to service removals, false otherwise
			self.there_are_engines_remaining = False














