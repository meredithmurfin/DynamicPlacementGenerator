from util import reader_util, writer_util, data_util
import data, solve, generate_removal_situations
import pprint, logging
from solve import FiniteHorizonMDPSolver

if __name__ == '__main__':
	data.init()
	logging.basicConfig(level=logging.INFO)
	new_removal_data = False

	# Import all possible states
	data.all_possible_states = reader_util.import_all_possible_states(
		filepath='data_to_read/general/all_possible_states.csv', 
		data_storage=data.all_possible_states)

	# Import all possible actions
	data.all_possible_actions = reader_util.import_all_possible_actions(
		data_storage=data.all_possible_actions)

	# Import engine removal information
	data.num_engines_info, data.num_removals_info, data.aos_cost = reader_util.import_engine_removal_info(
		filepath='data_to_read/general/engine_removal_info.csv',
		engines_data_storage=data.num_engines_info,
		removals_data_storage=data.num_removals_info,
		aos_cost_data_storage=data.aos_cost)

	# Import engine subtype data
	reader_util.import_engine_subtype_data()

	# Generate all possible removal situations
	if new_removal_data:
		for engine_subtype in data.engine_subtypes:
			generate_removal_situations.find_all_removal_situations(
				engine_subtype=engine_subtype,
				removals_info=data.num_removals_info[engine_subtype])

	# Import all possible removal situations
	data.all_possible_removal_situations = reader_util.import_all_possible_removal_situations(
		data_storage=data.all_possible_removal_situations)

	# Import future data for regression
	reader_util.import_future_data()
	
	havent_done = ['CFM56-5A']
	for month_to_run in range(1, 11):
		for engine_subtype in data.engine_subtypes:
			if engine_subtype in ['PW2000-2037', 'V2500-D5']:
				num_engines = data.num_engines_info[engine_subtype]['NUM_WORKING_ENGINES']
				if num_engines >= 5:
					all_possible_actions_for_subtype = data_util.find_all_possible_actions_for_subtype(
						num_engines=num_engines,
						num_removals_info=data.num_removals_info[engine_subtype])
					solver = FiniteHorizonMDPSolver(engine_subtype, all_possible_actions_for_subtype, month_to_run)
					solver.solve_MDP()
				else:
					solver = FiniteHorizonMDPSolver(engine_subtype, data.all_possible_actions[num_engines][:], month_to_run)
					solver.solve_MDP()








