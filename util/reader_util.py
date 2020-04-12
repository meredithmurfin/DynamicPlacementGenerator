import csv, logging
import pandas as pd
import numpy as np
from util import data_util
import data, pprint

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
	data_storage[1] = import_actions(filepath='data_to_read/general/actions/1_engines_all_possible_actions.csv')
	logging.info("Importing all 2-engine actions for the MDP...")
	data_storage[2] = import_actions(filepath='data_to_read/general/actions/2_engines_all_possible_actions.csv')
	logging.info("Importing all 3-engine actions for the MDP...")
	data_storage[3] = import_actions(filepath='data_to_read/general/actions/3_engines_all_possible_actions.csv')
	logging.info("Importing all 4-engine actions for the MDP...")
	data_storage[4] = import_actions(filepath='data_to_read/general/actions/4_engines_all_possible_actions.csv')
	logging.info("Importing all 5-engine actions for the MDP...")
	data_storage[5] = import_actions(filepath='data_to_read/general/actions/5_engines_all_possible_actions.csv')
	logging.info("All actions for the MDP have been imported.")
	return data_storage

def import_actions(filepath):
	data_from_file = pd.read_csv(filepath, header=None)
	data_as_numpy = pd.DataFrame(data_from_file).to_numpy()
	data_storage = []
	for action_before in data_as_numpy:
		data_storage.append((np.reshape(action_before, (7, 7), order='C')).astype(int))
	data_storage = np.array(data_storage)
	logging.info("All actions for the MDP have been imported.")
	return data_storage

def import_engine_removal_info(filepath, engines_data_storage, removals_data_storage, aos_cost_data_storage):
	logging.info("Importing all engine removal information...")
	with open(filepath, 'rt') as file:
		data_from_file = csv.reader(file)
		data_as_list = list(data_from_file)
		header = data_as_list[0]
		all_rows = data_as_list[1:]
		for row in all_rows:
			engine_subtype = row[1]
			engines_data_storage[engine_subtype] = {
				'TOTAL_NUM_ENGINES': int(row[2]),
				'NUM_WORKING_ENGINES': int(row[3]),
				'NUM_BROKEN_ENGINES_ATL': int(row[4]),
				'NUM_BROKEN_ENGINES_MSP': int(row[5])}
			removals_data_storage[engine_subtype] = {
				'MAX_NUM_REMOVALS_MONTHLY_TOTAL': int(row[6]),
				'MAX_NUM_REMOVALS_MONTHLY_ATL': int(row[7]),
				'MAX_NUM_REMOVALS_MONTHLY_CVG': int(row[8]),
				'MAX_NUM_REMOVALS_MONTHLY_DTW': int(row[9]),
				'MAX_NUM_REMOVALS_MONTHLY_LAX': int(row[10]),
				'MAX_NUM_REMOVALS_MONTHLY_MSP': int(row[11]),
				'MAX_NUM_REMOVALS_MONTHLY_SEA': int(row[12]),
				'MAX_NUM_REMOVALS_MONTHLY_SLC': int(row[13]),
				'MAX_NUM_REMOVALS_MONTHLY_NON_HUBS': int(row[14])}
			aos_cost_data_storage[engine_subtype] = float(row[15])
	logging.info("All engine removal information has been imported.")
	return engines_data_storage, removals_data_storage, aos_cost_data_storage

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
		hubs = data_as_list[0][1:]
		all_costs = data_as_list[1:]
		for row in all_costs:
			state_region = row[0]
			costs = row[1:]
			data_storage[engine_subtype][state_region] = {}
			for i in range(7):
				data_storage[engine_subtype][state_region][hubs[i]] = float(costs[i])
	return data_storage

def import_number_of_broken_engines_and_number_repaired(filepath, engine_subtype, data_storage):
	data_storage[engine_subtype] = {}
	with open(filepath, 'rt') as file:
		data_from_file = csv.reader(file)
		data_as_list = list(data_from_file)
		num_broken = data_as_list[0][1:]
		for num in num_broken:
			data_storage[engine_subtype][int(num)] = {}
		all_repair_probabilities = data_as_list[1:]
		for row in all_repair_probabilities:
			num_repaired = int(row[0])
			probabilities = row[1:]
			index_count = 0
			for num in num_broken:
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
			removal_location = row[0]
			rons_rads_coefficient = row[1]
			if '' in [row[1], row[2], row[3]]:
				continue
			else:
				rons_rads_coefficient = float(row[1])
				departures_coefficient = float(row[2])
				intercept = float(row[3])
				data_storage[engine_subtype][removal_location] = {
					'RR': rons_rads_coefficient,
					'D': departures_coefficient,
					'intercept': intercept}
	return data_storage

def import_all_possible_removal_situations(data_storage):
	logging.info("Importing all possible removal situations...")
	for engine_subtype in data.engine_subtypes:
		data_storage = import_removal_situations(
			filepath='data_exported/' + engine_subtype + '_all_possible_removal_situations.csv',
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
		header = data_as_list[0][1:]
		values = data_as_list[1:]
		for month in range(1, 11):
			data_storage[engine_subtype][month] = {}
			data_storage[engine_subtype][month]['OTHER'] = {1: 0, 2: 0, 3: 0}
			for hub in data.hubs:
				data_storage[engine_subtype][month][hub] = {1: 0, 2: 0, 3: 0}
		for month in range(10):
			m1 = values[month][1:]
			m2 = values[month+1][1:]
			m3 = values[month+2][1:]
			row_index = 0
			for head in header:
				data_storage[engine_subtype][month+1][head] = {1: float(m1[row_index]), 2: float(m2[row_index]), 3: float(m3[row_index])}
				row_index += 1
	return data_storage

def import_total_departures_ground_time_by_state_region_monthly(filepath, engine_subtype, data_storage):
	data_storage[engine_subtype] = {}
	with open(filepath, 'rt') as file:
		data_from_file = csv.reader(file)
		data_as_list = list(data_from_file)
		header = data_as_list[0][1:]
		values = data_as_list[1:]
		for month in range(1, 11):
			data_storage[engine_subtype][month] = {}
			for state_region in data.state_regions:
				data_storage[engine_subtype][month][state_region] = {1: 0, 2: 0, 3: 0}
		for month in range(10):
			m1 = values[month][1:]
			m2 = values[month+1][1:]
			m3 = values[month+2][1:]
			row_index = 0
			for head in header:
				data_storage[engine_subtype][month+1][head] = {1: float(m1[row_index]), 2: float(m2[row_index]), 3: float(m3[row_index])}
				row_index += 1
	return data_storage

def import_total_RONSRADS_ground_time_by_hub_monthly(filepath, engine_subtype, data_storage):
	data_storage[engine_subtype] = {}
	with open(filepath, 'rt') as file:
		data_from_file = csv.reader(file)
		data_as_list = list(data_from_file)
		header = data_as_list[0][1:]
		values = data_as_list[1:]
		for month in range(1, 11):
			data_storage[engine_subtype][month] = {}
			data_storage[engine_subtype][month]['OTHER'] = {1: 0, 2: 0, 3: 0}
			for hub in data.hubs:
				data_storage[engine_subtype][month][hub] = {1: 0, 2: 0, 3: 0}
		for month in range(10):
			m1 = values[month][1:]
			m2 = values[month+1][1:]
			m3 = values[month+2][1:]
			row_index = 0
			for head in header:
				data_storage[engine_subtype][month+1][head] = {1: float(m1[row_index]), 2: float(m2[row_index]), 3: float(m3[row_index])}
				row_index += 1
	return data_storage


