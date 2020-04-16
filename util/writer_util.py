import csv

def export_all_possible_removal_situations(engine_subtype, all_possible_removal_situations):
	with open(filepath, 'w') as file:
		writer = csv.writer(file)
		rows_to_write = []
		for row in all_possible_removal_situations:
			rows_to_write.append(row)
		writer.writerows(rows_to_write)

def export_all_possible_states(all_states):
	with open('data_to_read/all_possible_states.csv', 'w') as file:
		writer = csv.writer(file)
		rows_to_write = []
		for num_engines, states in all_states.items():
			for state in states:
				row_to_write = [num_engines]
				row_to_write.extend(state)
				rows_to_write.append(row_to_write)
		writer.writerows(rows_to_write) 

def export_all_possible_actions(num, all_actions):
	with open('data_to_read/' + str(num) + '_engines_all_possible_actions.csv', 'w') as file:
		writer = csv.writer(file)
		rows_to_write = []
		for action in all_actions:
			row_to_write = []
			for row in action:
				for i in row:
					row_to_write.append(i)
			rows_to_write.append(row_to_write)
		writer.writerows(rows_to_write)