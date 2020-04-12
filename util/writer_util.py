import csv

def export_all_possible_removal_situations(filepath, engine_subtype, all_possible_removal_situations):
	with open(filepath, 'w') as file:
		writer = csv.writer(file)
		rows_to_write = []
		for row in all_possible_removal_situations:
			rows_to_write.append(row)
		writer.writerows(rows_to_write)