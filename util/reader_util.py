import data
import csv, logging, pprint
import pandas as pd
import numpy as np

def import_all_possible_states(filepath, data_storage):
	logging.info("Importing all states for the MDP...")
	with open(filepath, 'rt') as file:
		data_from_file = csv.reader(file)
		all_states = list(data_from_file)
		for row in all_states:
			num_working_engines = int(row[0])
			state = list(map(int, row[1:]))
			if num_working_engines not in data_storage:
				data_storage[num_working_engines] = []
			data_storage[num_working_engines].append(state)
	logging.info("All states for the MDP have been imported.")
	return data_storage

def import_all_possible_actions(data_storage):
	logging.info("Importing all actions for the MDP...")
	logging.info("Importing all 1-engine actions for the MDP...")
	data_storage[1] = import_actions(filepath='data_to_read/1_engines_all_possible_actions.csv')
	logging.info("Importing all 2-engine actions for the MDP...")
	data_storage[2] = import_actions(filepath='data_to_read/2_engines_all_possible_actions.csv')
	logging.info("Importing all 3-engine actions for the MDP...")
	data_storage[3] = import_actions(filepath='data_to_read/3_engines_all_possible_actions.csv')
	logging.info("Importing all 4-engine actions for the MDP...")
	data_storage[4] = import_actions(filepath='data_to_read/4_engines_all_possible_actions.csv')
	logging.info("Importing all 5-engine actions for the MDP...")
	data_storage[5] = import_actions(filepath='data_to_read/5_engines_all_possible_actions.csv')
	logging.info("All actions for the MDP have been imported.")
	return data_storage

def import_actions(filepath):
	data_from_file = pd.read_csv(filepath, header=None)
	data_as_numpy = pd.DataFrame(data_from_file).to_numpy()
	data_storage = []
	for action_before in data_as_numpy:
		data_storage.append((np.reshape(action_before, (7, 7), order='C')).astype(int))
	data_storage = np.array(data_storage)
	return data_storage

def import_removal_info(filepath, removals_data_storage, aos_cost_data_storage):
	logging.info("Importing all removal information...")
	with open(filepath, 'rt') as file:
		data_from_file = csv.reader(file)
		data_as_list = list(data_from_file)
		header = data_as_list[0]
		all_rows = data_as_list[1:]
		for row in all_rows:
			if '' in row[:12]:
				raise Exception("There are empty cells in the removal_info file. All information for each fleet must be inputted. Values may be zero, but they may not be blank.")
			try:
				engine_subtype = row[0]
				removals_data_storage[engine_subtype] = {
					'MAX_NUM_REMOVALS_MONTHLY_TOTAL': int(row[1]),
					'MAX_NUM_REMOVALS_MONTHLY_ATL': int(row[2]),
					'MAX_NUM_REMOVALS_MONTHLY_CVG': int(row[3]),
					'MAX_NUM_REMOVALS_MONTHLY_DTW': int(row[4]),
					'MAX_NUM_REMOVALS_MONTHLY_LAX': int(row[5]),
					'MAX_NUM_REMOVALS_MONTHLY_MSP': int(row[6]),
					'MAX_NUM_REMOVALS_MONTHLY_SEA': int(row[7]),
					'MAX_NUM_REMOVALS_MONTHLY_SLC': int(row[8]),
					'MAX_NUM_REMOVALS_MONTHLY_NON_HUBS': int(row[9])}
				aos_cost_data_storage[engine_subtype] = float(row[10])
				if row[11].upper() == 'FALSE':
					data.need_to_update_removal_info[engine_subtype] = False 
				elif row[11].upper() == 'TRUE':
					data.need_to_update_removal_info[engine_subtype] = True
				else:
					raise Exception("The value in column 12 of the removal_info file must either be TRUE, indicating the information in the file has been changed since the previous run, or FALSE, indicating the information in the file is the same as the previous run.")
			except Exception as e:
				logging.error("An exception has occurred: " + e)
				raise Exception("Make sure you are inputting integer values into the removal_info file for columns 2 through 11. String values cannot be accepted.")
	logging.info("All removal information has been imported.")
	return removals_data_storage, aos_cost_data_storage

def import_engine_info(filepath, data_storage):
	logging.info("Importing all engine information...")
	with open(filepath, 'rt') as file:
		data_from_file = csv.reader(file)
		data_as_list = list(data_from_file)
		header = data_as_list[0]
		all_rows = data_as_list[1:]
		for row in all_rows:
			if '' in row[:12]:
				raise Exception("There are empty cells in the engine_info file. All information for each fleet must be inputted. Values may be zero, but they may not be blank.")
			try:
				engine_subtype = row[0]
				data_storage[engine_subtype] = {
					'TOTAL_NUM_ENGINES': int(row[1]),
					'NUM_WORKING_ENGINES': int(row[2]),
					'NUM_BROKEN_ENGINES_ATL': int(row[3]),
					'NUM_BROKEN_ENGINES_MSP': int(row[4]),
					'CURRENT_STATE': [int(row[5]), int(row[6]), int(row[7]), int(row[8]), int(row[9]), int(row[10]), int(row[11])]}
			except Exception as e:
				logging.error("An exception has occurred: " + e)
				raise Exception("Make sure you are inputting integer values into the engine_info file for columns 2 through 11. String values cannot be accepted.")
	logging.info("All engine information has been imported.")
	return data_storage

def import_engine_subtype_data():
	logging.info("Importing expected transportation costs, probabilities of engines repaired, and regression data...")
	for engine_subtype in data.engine_subtypes:
		path = 'data_to_read/' + engine_subtype + '/' + engine_subtype
		data.expected_transport_cost = import_expected_transport_cost(
			filepath=path + '_expected_transport_cost.csv', 
			engine_subtype=engine_subtype, 
			data_storage=data.expected_transport_cost)
		data.probability_of_num_repair_given_num_broken = import_number_of_broken_engines_and_number_repaired(
			filepath=path + '_number_of_broken_engines_and_number_repaired.csv', 
			engine_subtype=engine_subtype, 
			data_storage=data.probability_of_num_repair_given_num_broken)
		data.regression = import_regression(
			filepath=path + '_regression.csv', 
			engine_subtype=engine_subtype, 
			data_storage=data.regression)
		logging.info(engine_subtype + " data has been imported.")
		
def import_expected_transport_cost(filepath, engine_subtype, data_storage):
	data_storage[engine_subtype] = {}
	with open(filepath, 'rt') as file:
		data_from_file = csv.reader(file)
		data_as_list = list(data_from_file)
		hubs_header = data_as_list[0][1:]
		all_costs = data_as_list[1:]
		for row in all_costs:
			state_region = row[0]
			costs = row[1:]
			data_storage[engine_subtype][state_region] = {}
			for i in range(7):
				data_storage[engine_subtype][state_region][hubs_header[i]] = float(costs[i])
	return data_storage

def import_number_of_broken_engines_and_number_repaired(filepath, engine_subtype, data_storage):
	data_storage[engine_subtype] = {}
	with open(filepath, 'rt') as file:
		data_from_file = csv.reader(file)
		data_as_list = list(data_from_file)
		num_broken_header = data_as_list[0][1:]
		for num in num_broken_header:
			data_storage[engine_subtype][int(num)] = {}
		all_repair_probabilities = data_as_list[1:]
		for row in all_repair_probabilities:
			num_repaired = int(row[0])
			probabilities = row[1:]
			index_count = 0
			for num in num_broken_header:
				if (int(num) >= num_repaired):
					data_storage[engine_subtype][int(num)][num_repaired] = float(probabilities[index_count])
				index_count += 1
	return data_storage

def import_regression(filepath, engine_subtype, data_storage):
	data_storage[engine_subtype] = {}
	with open(filepath, 'rt') as file:
		data_from_file = csv.reader(file)
		data_as_list = list(data_from_file)
		regression_values = data_as_list[1:]
		for row in regression_values:
			location = row[0]
			RR = row[1]
			if '' in [row[1], row[2], row[3]]:
				continue
			else:
				RR = float(row[1])
				D = float(row[2])
				intercept = float(row[3])
				data_storage[engine_subtype][location] = {'RR': RR, 'D': D, 'intercept': intercept}
	return data_storage

def import_all_possible_removal_situations(data_storage):
	logging.info("Importing all possible removal situations...")
	for engine_subtype in data.engine_subtypes:
		data_storage = import_removal_situations(
			filepath='data_to_read/' + engine_subtype + '/' + engine_subtype + '_all_possible_removal_situations.csv',
			engine_subtype=engine_subtype,
			data_storage=data_storage)
	logging.info("All possible removal situations have been imported.")
	return data_storage

def import_removal_situations(filepath, engine_subtype, data_storage):
	data_storage[engine_subtype] = []
	with open(filepath, 'rt') as file:
		data_from_file = csv.reader(file)
		data_as_list = list(data_from_file)
		for row in data_as_list:
			data_storage[engine_subtype].append(row)
	return data_storage

def import_future_data():
	logging.info("Importing future departure data and future RON/RAD data...")
	for engine_subtype in data.engine_subtypes:
		data.num_departures_by_hub_monthly = import_num_departures_by_hub_monthly(
			filepath='data_to_read/' + engine_subtype + '/' + engine_subtype + '_num_departures_by_hub_monthly.csv', 
			engine_subtype=engine_subtype, 
			data_storage=data.num_departures_by_hub_monthly)
		data.total_departures_ground_time_by_state_region_monthly = import_total_departures_ground_time_by_state_region_monthly(
			filepath='data_to_read/' + engine_subtype + '/' + engine_subtype + '_total_departures_ground_time_by_state_region_monthly.csv', 
			engine_subtype=engine_subtype, 
			data_storage=data.total_departures_ground_time_by_state_region_monthly)
		data.total_RONSRADS_ground_time_by_hub_monthly = import_total_RONSRADS_ground_time_by_hub_monthly(
			filepath='data_to_read/' + engine_subtype + '/' + engine_subtype + '_total_RONSRADS_ground_time_by_hub_monthly.csv', 
			engine_subtype=engine_subtype, 
			data_storage=data.total_RONSRADS_ground_time_by_hub_monthly)
		logging.info(engine_subtype + " data has been imported.")

def import_num_departures_by_hub_monthly(filepath, engine_subtype, data_storage):
	data_storage[engine_subtype] = {}
	with open(filepath, 'rt') as file:
		data_from_file = csv.reader(file)
		data_as_list = list(data_from_file)
		try:
			hubs_header = data_as_list[0][1:]
			values = data_as_list[1:]
			month_1 = values[0][1:] 
			month_2 = values[1][1:] 
			month_3 = values[2][1:]
		except Exception as e:
			logging.error("An exception has occurred: " + e)
			raise Exception("Make sure the data in the num_departures_by_hub_monthly file for the " + engine_subtype + " is organized with 3 rows, each row providing counts of departures for that month at that location.")
		for i in range(len(data.hubs) + 1):
			hub = hubs_header[i]
			if (hub not in data.hubs) and (hub not in ['OTHER']):
				raise Exception("The header in the num_departures_by_hub_monthly file for the " + engine_subtype + " must be organized by each valid hub with one column for OTHER.") 
			data_storage[engine_subtype][hub] = {1: int(month_1[i]), 2: int(month_2[i]), 3: int(month_3[i])}
	return data_storage

def import_total_departures_ground_time_by_state_region_monthly(filepath, engine_subtype, data_storage):
	data_storage[engine_subtype] = {}
	with open(filepath, 'rt') as file:
		data_from_file = csv.reader(file)
		data_as_list = list(data_from_file)
		try:
			state_regions_header = data_as_list[0][1:]
			values = data_as_list[1:]
			month_1 = values[0][1:]
			month_2 = values[1][1:]
			month_3 = values[2][1:]
		except Exception as e:
			logging.error("An exception has occurred: " + e)
			raise Exception("Make sure the data in the total_departures_ground_time_by_state_region_monthly file for the " + engine_subtype + " is organized with 3 rows, each row providing the total ground time from departures for that month at that location.")
		for i in range(len(data.state_regions)):
			state_region = state_regions_header[i]
			if state_region not in data.state_regions:
				raise Exception("The header in the total_departures_ground_time_by_state_region_monthly file for the " + engine_subtype + " must be organized by each valid state region.")
			data_storage[engine_subtype][state_region] = {1: int(month_1[i]), 2: int(month_2[i]), 3: int(month_3[i])}
	return data_storage

def import_total_RONSRADS_ground_time_by_hub_monthly(filepath, engine_subtype, data_storage):
	data_storage[engine_subtype] = {}
	with open(filepath, 'rt') as file:
		data_from_file = csv.reader(file)
		data_as_list = list(data_from_file)
		try:
			hubs_header = data_as_list[0][1:]
			values = data_as_list[1:]
			month_1 = values[0][1:] 
			month_2 = values[1][1:] 
			month_3 = values[2][1:]
		except Exception as e:
			logging.error("An exception has occurred: " + e)
			raise Exception("Make sure the data in the total_RONSRADS_ground_time_by_hub_monthly file for the " + engine_subtype + " is organized with 3 rows, each row providing the total ground time from RONs/RADs for that month at that location.")
		for i in range(len(data.hubs) + 1):
			hub = hubs_header[i]
			if (hub not in data.hubs) and (hub not in ['OTHER']):
				raise Exception("The header in the total_RONSRADS_ground_time_by_hub_monthly file for the " + engine_subtype + " must be organized by each valid hub with one column for OTHER.") 
			data_storage[engine_subtype][hub] = {1: int(month_1[i]), 2: int(month_2[i]), 3: int(month_3[i])}
	return data_storage
