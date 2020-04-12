from util import data_util, writer_util
import data
import numpy as np
import scipy.sparse as sp
from itertools import combinations, chain, groupby
from operator import sub
import pprint, logging, operator, copy
from datetime import date

def find_all_removal_situations(engine_subtype, removals_info):
	logging.info("Generating all possible removal situations for the " + engine_subtype + " engine...")
	logging.info("Removal information being used for this type: " + str(removals_info))

	num_allowed_at_hubs = find_num_occurrences_of_max_removals_for_hubs([
		removals_info['MAX_NUM_REMOVALS_MONTHLY_ATL'],
		removals_info['MAX_NUM_REMOVALS_MONTHLY_CVG'],
		removals_info['MAX_NUM_REMOVALS_MONTHLY_DTW'],
		removals_info['MAX_NUM_REMOVALS_MONTHLY_LAX'],
		removals_info['MAX_NUM_REMOVALS_MONTHLY_MSP'],
		removals_info['MAX_NUM_REMOVALS_MONTHLY_SEA'],
		removals_info['MAX_NUM_REMOVALS_MONTHLY_SLC']])

	num_different_removals_non_hubs = 1
	if removals_info['MAX_NUM_REMOVALS_MONTHLY_NON_HUBS'] == 2:
		num_different_removals_non_hubs = 2
	num_different_removals_hubs = sum(num_allowed_at_hubs.values()) - (num_allowed_at_hubs[0] if 0 in num_allowed_at_hubs else 0)

	ranges = find_ranges_of_num_removal_values_valid_at_hubs(num_allowed_at_hubs)

	max_num_removals_total = removals_info['MAX_NUM_REMOVALS_MONTHLY_TOTAL']
	max_removals_non_hubs = removals_info['MAX_NUM_REMOVALS_MONTHLY_NON_HUBS']
	max_allowed = find_max_removals_allowed(num_allowed_at_hubs, max_removals_non_hubs)

	removal_sums = {}
	for num_removals in range(1, max_num_removals_total + 1):
		removal_sums[num_removals] = find_all_valid_sums_for_current_num_removals(
			num_removals=num_removals,
			num_allowed_at_hubs=num_allowed_at_hubs,
			num_different_removals_hubs=num_different_removals_hubs,
			num_different_removals_non_hubs=num_different_removals_non_hubs,
			max_removals_non_hubs=max_removals_non_hubs,
			ranges=ranges,
			max_allowed=max_allowed)

	logging.info("All combinations of values to generate possible removal situations have been found.")

	removals_generator = RemovalsGenerator(engine_subtype, removals_info, removal_sums, ranges)
	removals_generator.generate_all_removal_situations()

def find_num_occurrences_of_max_removals_for_hubs(max_num_removals_at_hubs):
	max_num_removals_at_hubs_set = set(max_num_removals_at_hubs)
	unique_max_num_removals_at_hubs = list(max_num_removals_at_hubs_set)
	num_allowed_at_hubs = {}
	for value in unique_max_num_removals_at_hubs:
		num_allowed_at_hubs[value] = 0
	for value in max_num_removals_at_hubs:
		num_allowed_at_hubs[value] += 1
	return num_allowed_at_hubs

def find_ranges_of_num_removal_values_valid_at_hubs(num_allowed_at_hubs):
	ranges = []
	num_removals_at_hubs = find_possible_num_removals_at_hubs(num_allowed_at_hubs)
	if at_least_one_hub_never_has_removals(num_removals_at_hubs[0]):
		num_removals_at_hubs = num_removals_at_hubs[1:]
	current_min = 1
	for num_removals in num_removals_at_hubs:
		ranges.append([current_min, num_removals])
		current_min = num_removals + 1
	ranges.reverse()
	return ranges

def find_possible_num_removals_at_hubs(num_allowed_at_hubs):
	num_removals_at_hubs = list(num_allowed_at_hubs.keys())
	num_removals_at_hubs.sort()
	return num_removals_at_hubs

def at_least_one_hub_never_has_removals(lowest_num_removals_at_hubs):
	return (lowest_num_removals_at_hubs == 0)

def find_max_removals_allowed(num_allowed_at_hubs, max_removals_non_hubs):
	max_allowed = max(num_allowed_at_hubs.keys())
	if only_one_removal_can_happen_at_hubs_but_up_to_two_removals_can_happen_at_non_hubs(max_allowed, max_removals_non_hubs):
		max_allowed = 2
	return max_allowed

def only_one_removal_can_happen_at_hubs_but_up_to_two_removals_can_happen_at_non_hubs(max_allowed, max_removals_non_hubs):
	return (max_allowed == 1) and (max_removals_non_hubs == 2)

def find_all_valid_sums_for_current_num_removals(num_removals, num_allowed_at_hubs, num_different_removals_hubs, num_different_removals_non_hubs, ranges, max_removals_non_hubs, max_allowed):
	all_sums = find_all_sums(num_removals)
	unique_sums_not_validated = get_unique_list_of_lists(all_sums)
	sums_validated = []
	for values_to_sum in unique_sums_not_validated:
		if too_many_values_in_this_sum_than_possible_for_a_possible_removal_situation(values_to_sum, num_different_removals_hubs, num_different_removals_non_hubs):
			continue
		elif a_value_in_the_sum_exceeds_the_max_allowed(values_to_sum, num_allowed_at_hubs, max_removals_non_hubs, max_allowed):
			continue
		elif only_one_removal_is_allowed_anywhere(ranges, max_allowed):
			sums_validated.append(values_to_sum)
		elif values_in_sum_invalid_due_to_max_num_removals_possible(values_to_sum, ranges, num_allowed_at_hubs, max_removals_non_hubs, num_different_removals_hubs):
			continue
		else:
			sums_validated.append(values_to_sum)
	return sums_validated

def find_all_sums(n):
	beginning, middle, end = [0], list(range(1, n)), [n]
	splits = (d for i in range(n) for d in combinations(middle, i))
	return (list(map(sub, chain(split, end), chain(beginning, split))) for split in splits)

def get_unique_list_of_lists(a_list):
	unique_list_of_lists = []
	for l in a_list:
		l.sort()
		if l not in unique_list_of_lists:
			unique_list_of_lists.append(l)
	return unique_list_of_lists

def too_many_values_in_this_sum_than_possible_for_a_possible_removal_situation(values_to_sum, num_different_removals_hubs, num_different_removals_non_hubs):
	return (len(values_to_sum) > (num_different_removals_hubs + num_different_removals_non_hubs))

def a_value_in_the_sum_exceeds_the_max_allowed(values_to_sum, num_allowed_at_hubs, max_removals_non_hubs, max_allowed):
	for value in values_to_sum:
		if value > max_allowed:
			return True
	return False

def only_one_removal_is_allowed_anywhere(ranges, max_allowed):
	if only_one_range_of_values_to_search(ranges):
		if range_to_search_is_for_1_removal(ranges[0]):
			if max_allowed == 1:
				return True
	return False

def only_one_range_of_values_to_search(ranges):
	return (len(ranges) == 1) 

def range_to_search_is_for_1_removal(range_to_search):
	return (range_to_search == [1, 1])

def values_in_sum_invalid_due_to_max_num_removals_possible(values_to_sum, ranges, num_allowed_at_hubs, max_removals_non_hubs, num_different_removals_hubs):
	num_allowed_in_each_range = get_num_allowed_in_each_range_to_edit(num_allowed_at_hubs)
	num_actually_in_each_range = get_num_actually_in_each_range_to_edit(num_allowed_in_each_range)
	num_allowed_in_each_range, num_actually_in_each_range, ranges = update_ranges_and_removals_allowed_to_reflect_values_to_sum(
		num_allowed_in_each_range=num_allowed_in_each_range, 
		num_actually_in_each_range=num_actually_in_each_range, 
		ranges=ranges, 
		values_to_sum=values_to_sum, 
		max_removals_non_hubs=max_removals_non_hubs, 
		num_different_removals_hubs=num_different_removals_hubs)
	num_actually_in_each_range = update_num_actually_in_each_range_to_reflect_values_to_sum(
		num_actually_in_each_range=num_actually_in_each_range, 
		ranges=ranges, 
		values_to_sum=values_to_sum)
	if values_in_sum_invalid(num_allowed_in_each_range, num_actually_in_each_range):
		return True
	else:
		return False

def get_num_allowed_in_each_range_to_edit(num_allowed_at_hubs):
	num_allowed_in_each_range = copy.deepcopy(num_allowed_at_hubs)
	if 0 in num_allowed_in_each_range:
		del num_allowed_in_each_range[0]
	return num_allowed_in_each_range

def get_num_actually_in_each_range_to_edit(num_allowed_in_each_range):
	num_actually_in_each_range = copy.deepcopy(num_allowed_in_each_range)
	for max_removals, max_allowed in num_actually_in_each_range.items():
		num_actually_in_each_range[max_removals] = 0
	return num_actually_in_each_range

def update_ranges_and_removals_allowed_to_reflect_values_to_sum(num_allowed_in_each_range, num_actually_in_each_range, ranges, values_to_sum, max_removals_non_hubs, num_different_removals_hubs):
	if max_removals_non_hubs == 2:
		if non_hubs_can_have_2_removals_and_values_to_sum_contain_2_1_1(values_to_sum):
			if having_2_removals_at_any_non_hub_is_not_possible(values_to_sum, num_different_removals_hubs): 
				ranges = update_ranges_to_include_new_range(ranges, [1, 1])
			else:
				ranges = update_ranges_to_include_new_range(ranges, [2, 2])
				num_allowed_in_each_range, num_actually_in_each_range = update_data_to_include_2_removals(num_allowed_in_each_range, num_actually_in_each_range)				
			num_allowed_in_each_range, num_actually_in_each_range = update_data_to_include_1_removal(num_allowed_in_each_range, num_actually_in_each_range, num_possible=2)
		elif non_hubs_can_have_2_removals_and_values_to_sum_contain_2_1(values_to_sum):
			ranges = update_ranges_to_include_new_range(ranges, [2, 2])
			num_allowed_in_each_range, num_actually_in_each_range = update_data_to_include_2_removals(num_allowed_in_each_range, num_actually_in_each_range)				
			num_allowed_in_each_range, num_actually_in_each_range = update_data_to_include_1_removal(num_allowed_in_each_range, num_actually_in_each_range, num_possible=1)
		elif non_hubs_can_have_2_removals_and_values_to_sum_contain_2(values_to_sum):
			ranges = update_ranges_to_include_new_range(ranges, [2, 2])
			num_allowed_in_each_range, num_actually_in_each_range = update_data_to_include_2_removals(num_allowed_in_each_range, num_actually_in_each_range)
		elif non_hubs_can_have_2_removals_and_values_to_sum_contains_1_1(values_to_sum): 
			ranges = update_ranges_to_include_new_range(ranges, [1, 1])
			num_allowed_in_each_range, num_actually_in_each_range = update_data_to_include_1_removal(num_allowed_in_each_range, num_actually_in_each_range, num_possible=2)
		elif non_hubs_can_have_2_removals_and_values_to_sum_contains_1(values_to_sum): 
			ranges = update_ranges_to_include_new_range(ranges, [1, 1])
			num_allowed_in_each_range, num_actually_in_each_range = update_data_to_include_1_removal(num_allowed_in_each_range, num_actually_in_each_range, num_possible=1)
	else:
		if non_hubs_can_have_1_removal_and_values_to_sum_conains_1(values_to_sum):
			ranges = update_ranges_to_include_new_range(ranges, [1, 1])
			num_allowed_in_each_range, num_actually_in_each_range = update_data_to_include_1_removal(num_allowed_in_each_range, num_actually_in_each_range, num_possible=1)
	return num_allowed_in_each_range, num_actually_in_each_range, ranges

def update_ranges_to_include_new_range(ranges, new_r):
	new_ranges = ranges[:]
	if new_r not in ranges:
		new_r_min, new_r_max = new_r[0], new_r[1]
		for r in ranges:
			r_min, r_max = r[0], r[1]
			if r_min == (new_r_min - 1):
				if r_max == new_r_max:
					new_ranges.append(new_r)
				else:
					new_ranges.remove(r)
					new_ranges.append([new_r_min - 1, new_r_max - 1])
					new_ranges.append(new_r)
					if r_max > new_r_max:
						new_ranges.append([new_r_min - 1, r_max])
				return sort_and_reverse_list(new_ranges)
			elif r_min == new_r_min:
				new_ranges.remove(r)
				new_ranges.append(new_r)
				new_ranges.append([new_r_min + 1, r_max])
				return sort_and_reverse_list(new_ranges)
	return sort_and_reverse_list(new_ranges)

def update_data_to_include_2_removals(num_allowed_in_each_range, num_actually_in_each_range):
	if 2 not in num_allowed_in_each_range:
		num_allowed_in_each_range[2] = 1
		num_actually_in_each_range[2] = 0
	else:
		num_allowed_in_each_range[2] += 1	
	return num_allowed_in_each_range, num_actually_in_each_range

def update_data_to_include_1_removal(num_allowed_in_each_range, num_actually_in_each_range, num_possible):
	if 1 not in num_allowed_in_each_range:
		num_allowed_in_each_range[1] = num_possible
		num_actually_in_each_range[1] = 0
	else:
		num_allowed_in_each_range[1] += num_possible
	return num_allowed_in_each_range, num_actually_in_each_range

def non_hubs_can_have_2_removals_and_values_to_sum_contain_2_1_1(values_to_sum):
	return (values_to_sum.count(2) > 0) and (values_to_sum.count(1) >= 2)

def non_hubs_can_have_2_removals_and_values_to_sum_contain_2_1(values_to_sum):
	return (values_to_sum.count(2) > 0) and (values_to_sum.count(1) == 1)

def non_hubs_can_have_2_removals_and_values_to_sum_contain_2(values_to_sum):
	return (values_to_sum.count(2) > 0) and (values_to_sum.count(1) == 0)

def non_hubs_can_have_2_removals_and_values_to_sum_contains_1_1(values_to_sum):
	return (values_to_sum.count(1) >= 2)

def non_hubs_can_have_2_removals_and_values_to_sum_contains_1(values_to_sum):
	return (values_to_sum.count(1) == 1)

def non_hubs_can_have_1_removal_and_values_to_sum_conains_1(values_to_sum):
	return (values_to_sum.count(1) >= 1)

def having_2_removals_at_any_non_hub_is_not_possible(values_to_sum, num_different_removals_hubs):
	return ((len(values_to_sum) - 1) > num_different_removals_hubs)

def update_num_actually_in_each_range_to_reflect_values_to_sum(num_actually_in_each_range, ranges, values_to_sum):
	for current_range in ranges:
		current_min = current_range[0]
		current_max = current_range[1]
		for value in values_to_sum:
			if value_within_range(value, current_min, current_max):
				num_actually_in_each_range[current_max] += 1
	return num_actually_in_each_range

def values_in_sum_invalid(num_allowed_in_each_range, num_actually_in_each_range):
	all_max_num_removals = list(num_allowed_in_each_range.keys())
	all_max_num_removals = sort_and_reverse_list(all_max_num_removals)
	count = 1
	for num_removals in all_max_num_removals:
		if values_in_sum_exceed_removals_allowed_for_that_range(num_allowed_in_each_range, num_actually_in_each_range, num_removals):
			return True
		if all_max_num_removals_have_not_been_iterated_yet(count, all_max_num_removals):
			num_allowed_in_each_range = add_num_not_used_in_range_to_next_range_to_iterate(num_allowed_in_each_range, num_actually_in_each_range, num_removals, all_max_num_removals, count)
			count += 1
	return False

def values_in_sum_exceed_removals_allowed_for_that_range(num_allowed_in_each_range, num_actually_in_each_range, num_removals):
	return (num_actually_in_each_range[num_removals] > num_allowed_in_each_range[num_removals])

def all_max_num_removals_have_not_been_iterated_yet(count, all_max_num_removals):
	return (count != len(all_max_num_removals))

def add_num_not_used_in_range_to_next_range_to_iterate(num_allowed_in_each_range, num_actually_in_each_range, num_removals, all_max_num_removals, count):
	num_removals_leftover = (num_allowed_in_each_range[num_removals] - num_actually_in_each_range[num_removals])
	num_allowed_in_each_range[all_max_num_removals[count]] += num_removals_leftover
	return num_allowed_in_each_range

def sort_and_reverse_list(a_list):
	a_list.sort()
	a_list.reverse()
	return a_list

def value_within_range(value, current_min, current_max):
	return ((value >= current_min) and (value <= current_max))

class RemovalsGenerator:

	def __init__(self, engine_subtype, removals_info, removal_sums, ranges):
		logging.info("Initializing RemovalsGenerator for the " + engine_subtype + " engine...")

		self.engine_subtype = engine_subtype
		
		self.max_removals_ATL = removals_info['MAX_NUM_REMOVALS_MONTHLY_ATL']
		self.max_removals_CVG = removals_info['MAX_NUM_REMOVALS_MONTHLY_CVG']
		self.max_removals_DTW = removals_info['MAX_NUM_REMOVALS_MONTHLY_DTW']
		self.max_removals_LAX = removals_info['MAX_NUM_REMOVALS_MONTHLY_LAX']
		self.max_removals_MSP = removals_info['MAX_NUM_REMOVALS_MONTHLY_MSP']
		self.max_removals_SEA = removals_info['MAX_NUM_REMOVALS_MONTHLY_SEA']
		self.max_removals_SLC = removals_info['MAX_NUM_REMOVALS_MONTHLY_SLC']
		
		self.max_removals_hubs_dict = {
			'ATL': self.max_removals_ATL, 
			'CVG': self.max_removals_CVG,
			'DTW': self.max_removals_DTW,
			'LAX': self.max_removals_LAX,
			'MSP': self.max_removals_MSP,
			'SEA': self.max_removals_SEA,
			'SLC': self.max_removals_SLC}

		self.max_removals_hubs_list = [self.max_removals_ATL, self.max_removals_CVG, self.max_removals_DTW,
			self.max_removals_LAX, self.max_removals_MSP, self.max_removals_SEA, self.max_removals_SLC]

		self.max_removals_non_hubs = removals_info['MAX_NUM_REMOVALS_MONTHLY_NON_HUBS']
		self.max_different_removals_hubs = 7 - self.max_removals_hubs_list.count(0)
		self.max_removals_total = removals_info['MAX_NUM_REMOVALS_MONTHLY_TOTAL']
		
		self.removal_sums = removal_sums

		self.ranges = ranges

		self.indeces_where_removals_should_not_occur = []
		self.find_indeces_where_removals_should_not_occur()

		self.num_all = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 
			24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 
			48, 49, 50, 51, 52]
		self.num_hubs = [0, 1, 2, 3, 4, 5, 6]
		self.num_non_hubs = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 
			28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 
			52]
		self.remove_indeces_from_lists_where_removals_should_not_occur()

		self.valid_indeces_for_ranges = {}
		self.find_indeces_for_ranges()

		self.all_perms = []
		self.zero_list_all = [0] * 53

		self.num_all_2_removals = []
		self.find_all_values_where_2_removals_can_occur()

		self.indeces_to_iterate_for_current_values = []
		self.indeces_to_iterate_for_current_values_again = []
		self.will_need_to_iterate_twice = False
		self.more_than_one_value_must_occur_at_non_hubs = False

		data.all_possible_removal_situations[self.engine_subtype] = []

	def find_all_values_where_2_removals_can_occur(self):
		for r in self.ranges:
			current_min = r[0]
			current_max = r[1]
			if (2 >= current_min) and (2 <= current_max):
				self.num_all_2_removals = self.valid_indeces_for_ranges[str(r)][:]
				self.num_all_2_removals.extend(self.num_non_hubs)

	def find_indeces_where_removals_should_not_occur(self):
		for index in range(7):
			if self.max_removals_hubs_list[index] == 0:
				self.indeces_where_removals_should_not_occur.append(index)

	def remove_indeces_from_lists_where_removals_should_not_occur(self):
		for index in sorted(self.indeces_where_removals_should_not_occur, reverse=True):
			del self.num_all[index]
			del self.num_hubs[index]

	def find_indeces_for_ranges(self):
		for r in self.ranges:
			self.valid_indeces_for_ranges[str(r)] = []
		for i in range(len(self.max_removals_hubs_list)):
			hub_max_removals = self.max_removals_hubs_list[i]
			for r in self.ranges:
				current_min = r[0]
				if hub_max_removals >= current_min:
					self.valid_indeces_for_ranges[str(r)].append(i)

	def generate_all_removal_situations(self):
		for num_removals, all_sums in self.removal_sums.items():
			current_num_removals = num_removals
			for values in all_sums:
				self.find_indeces_to_iterate(values)
				if len(values) == 1:
					self.one_value(values)
				elif len(values) == 2:
					self.two_values(values)
				elif len(values) == 3:
					self.three_values(values)
				elif len(values) == 4:
					self.four_values(values)
				elif len(values) == 5:
					self.five_values(values)
				elif len(values) == 6:
					self.six_values(values)
				elif len(values) == 7:
					self.seven_values(values)
				elif len(values) == 8:
					self.eight_values(values)
				elif len(values) == 9:
					self.nine_values(values)
		writer_util.export_all_possible_removal_situations(
			filepath='data_to_read/' + self.engine_subtype + '/' + self.engine_subtype + '_all_possible_removal_situations.csv',
			engine_subtype=self.engine_subtype,
			all_possible_removal_situations=data.all_possible_removal_situations[self.engine_subtype])

	def indeces_not_equal(self, list_of_indeces):
		set_of_indeces = set(list_of_indeces)
		list_of_set_of_indeces = list(set_of_indeces)
		if len(list_of_set_of_indeces) != len(list_of_indeces):
			return False
		return True

	def make_perms_unique_and_add_to_all_perms(self, perms):
		perms.sort()
		unique_perms_list = list(perm for perm,_ in groupby(perms))
		data.all_possible_removal_situations[self.engine_subtype].extend(unique_perms_list)
		return unique_perms_list

	def one_value(self, values):
		logging.info('Finding permutations for: ' + str(values))
		perms = []
		for i in self.indeces_to_iterate_for_current_values[0]:
			current_list = self.zero_list_all[:]
			current_list[i] = values[0]
			perms.append(current_list)
		unique_perms_list = self.make_perms_unique_and_add_to_all_perms(perms)
		num_unique_perms = len(unique_perms_list)
		logging.info(str(num_unique_perms) + ' permutations found.')

	def two_values(self, values):
		logging.info('Finding permutations for: ' + str(values))
		perms = []
		for i in self.indeces_to_iterate_for_current_values[0]:
			for j in self.indeces_to_iterate_for_current_values[1]:
				if self.indeces_not_equal([i, j]):
					current_list = self.zero_list_all[:]
					current_list[i] = values[0]
					current_list[j] = values[1]
					perms.append(current_list)
		unique_perms_list = self.make_perms_unique_and_add_to_all_perms(perms)
		num_unique_perms = len(unique_perms_list)
		logging.info(str(num_unique_perms) + ' permutations found.')

	def three_values(self, values):
		logging.info('Finding permutations for: ' + str(values))
		perms = []
		if self.will_need_to_iterate_twice:
			for i in self.indeces_to_iterate_for_current_values[0]:
				for j in self.indeces_to_iterate_for_current_values[1]:
					for k in self.indeces_to_iterate_for_current_values[2]:
						if self.indeces_not_equal([i, j, k]):
							current_list = self.zero_list_all[:]
							current_list[i] = values[0]
							current_list[j] = values[1]
							current_list[k] = values[2]
							perms.append(current_list)
			for i in self.indeces_to_iterate_for_current_values_again[0]:
				for j in self.indeces_to_iterate_for_current_values_again[1]:
					for k in self.indeces_to_iterate_for_current_values_again[2]:
						if self.indeces_not_equal([i, j, k]):
							current_list = self.zero_list_all[:]
							current_list[i] = values[0]
							current_list[j] = values[1]
							current_list[k] = values[2]
							perms.append(current_list)
		else:
			for i in self.indeces_to_iterate_for_current_values[0]:
				for j in self.indeces_to_iterate_for_current_values[1]:
					for k in self.indeces_to_iterate_for_current_values[2]:
						if self.indeces_not_equal([i, j, k]):
							current_list = self.zero_list_all[:]
							current_list[i] = values[0]
							current_list[j] = values[1]
							current_list[k] = values[2]
							perms.append(current_list)
		unique_perms_list = self.make_perms_unique_and_add_to_all_perms(perms)
		num_unique_perms = len(unique_perms_list)
		logging.info(str(num_unique_perms) + ' permutations found.')

	def four_values(self, values):
		logging.info('Finding permutations for: ' + str(values))
		perms = []
		if self.will_need_to_iterate_twice:
			for i in self.indeces_to_iterate_for_current_values[0]:
				for j in self.indeces_to_iterate_for_current_values[1]:
					for k in self.indeces_to_iterate_for_current_values[2]:
						for l in self.indeces_to_iterate_for_current_values[3]:
							if self.indeces_not_equal([i, j, k, l]):
								current_list = self.zero_list_all[:]
								current_list[i] = values[0]
								current_list[j] = values[1]
								current_list[k] = values[2]
								current_list[l] = values[3]
								perms.append(current_list)
			for i in self.indeces_to_iterate_for_current_values_again[0]:
				for j in self.indeces_to_iterate_for_current_values_again[1]:
					for k in self.indeces_to_iterate_for_current_values_again[2]:
						for l in self.indeces_to_iterate_for_current_values_again[3]:
							if self.indeces_not_equal([i, j, k, l]):
								current_list = self.zero_list_all[:]
								current_list[i] = values[0]
								current_list[j] = values[1]
								current_list[k] = values[2]
								current_list[l] = values[3]
								perms.append(current_list)
		else:
			for i in self.indeces_to_iterate_for_current_values[0]:
				for j in self.indeces_to_iterate_for_current_values[1]:
					for k in self.indeces_to_iterate_for_current_values[2]:
						for l in self.indeces_to_iterate_for_current_values[3]:
							if self.indeces_not_equal([i, j, k, l]):
								current_list = self.zero_list_all[:]
								current_list[i] = values[0]
								current_list[j] = values[1]
								current_list[k] = values[2]
								current_list[l] = values[3]
								perms.append(current_list)
		unique_perms_list = self.make_perms_unique_and_add_to_all_perms(perms)
		num_unique_perms = len(unique_perms_list)
		logging.info(str(num_unique_perms) + ' permutations found.')

	def five_values(self, values):
		logging.info('Finding permutations for: ' + str(values))
		perms = []
		if self.will_need_to_iterate_twice:
			for i in self.indeces_to_iterate_for_current_values[0]:
				for j in self.indeces_to_iterate_for_current_values[1]:
					for k in self.indeces_to_iterate_for_current_values[2]:
						for l in self.indeces_to_iterate_for_current_values[3]:
							for m in self.indeces_to_iterate_for_current_values[4]:
								if self.indeces_not_equal([i, j, k, l, m]):
									current_list = self.zero_list_all[:]
									current_list[i] = values[0]
									current_list[j] = values[1]
									current_list[k] = values[2]
									current_list[l] = values[3]
									current_list[m] = values[4]
									perms.append(current_list)
			for i in self.indeces_to_iterate_for_current_values_again[0]:
				for j in self.indeces_to_iterate_for_current_values_again[1]:
					for k in self.indeces_to_iterate_for_current_values_again[2]:
						for l in self.indeces_to_iterate_for_current_values_again[3]:
							for m in self.indeces_to_iterate_for_current_values_again[4]:
								if self.indeces_not_equal([i, j, k, l, m]):
									current_list = self.zero_list_all[:]
									current_list[i] = values[0]
									current_list[j] = values[1]
									current_list[k] = values[2]
									current_list[l] = values[3]
									current_list[m] = values[4]
									perms.append(current_list)
		else:
			for i in self.indeces_to_iterate_for_current_values[0]:
				for j in self.indeces_to_iterate_for_current_values[1]:
					for k in self.indeces_to_iterate_for_current_values[2]:
						for l in self.indeces_to_iterate_for_current_values[3]:
							for m in self.indeces_to_iterate_for_current_values[4]:
								if self.indeces_not_equal([i, j, k, l, m]):
									current_list = self.zero_list_all[:]
									current_list[i] = values[0]
									current_list[j] = values[1]
									current_list[k] = values[2]
									current_list[l] = values[3]
									current_list[m] = values[4]
									perms.append(current_list)
		unique_perms_list = self.make_perms_unique_and_add_to_all_perms(perms)
		num_unique_perms = len(unique_perms_list)
		logging.info(str(num_unique_perms) + ' permutations found.')

	def six_values(self, values):
		logging.info('Finding permutations for: ' + str(values))
		perms = []
		if self.will_need_to_iterate_twice:
			for i in self.indeces_to_iterate_for_current_values[0]:
				for j in self.indeces_to_iterate_for_current_values[1]:
					for k in self.indeces_to_iterate_for_current_values[2]:
						for l in self.indeces_to_iterate_for_current_values[3]:
							for m in self.indeces_to_iterate_for_current_values[4]:
								for n in self.indeces_to_iterate_for_current_values[5]:
									if self.indeces_not_equal([i, j, k, l, m, n]):
										current_list = self.zero_list_all[:]
										current_list[i] = values[0]
										current_list[j] = values[1]
										current_list[k] = values[2]
										current_list[l] = values[3]
										current_list[m] = values[4]
										current_list[n] = values[5]
										perms.append(current_list)
			for i in self.indeces_to_iterate_for_current_values_again[0]:
				for j in self.indeces_to_iterate_for_current_values_again[1]:
					for k in self.indeces_to_iterate_for_current_values_again[2]:
						for l in self.indeces_to_iterate_for_current_values_again[3]:
							for m in self.indeces_to_iterate_for_current_values_again[4]:
								for n in self.indeces_to_iterate_for_current_values_again[5]:
									if self.indeces_not_equal([i, j, k, l, m, n]):
										current_list = self.zero_list_all[:]
										current_list[i] = values[0]
										current_list[j] = values[1]
										current_list[k] = values[2]
										current_list[l] = values[3]
										current_list[m] = values[4]
										current_list[n] = values[5]
										perms.append(current_list)
		else:
			for i in self.indeces_to_iterate_for_current_values[0]:
				for j in self.indeces_to_iterate_for_current_values[1]:
					for k in self.indeces_to_iterate_for_current_values[2]:
						for l in self.indeces_to_iterate_for_current_values[3]:
							for m in self.indeces_to_iterate_for_current_values[4]:
								for n in self.indeces_to_iterate_for_current_values[5]:
									if self.indeces_not_equal([i, j, k, l, m, n]):
										current_list = self.zero_list_all[:]
										current_list[i] = values[0]
										current_list[j] = values[1]
										current_list[k] = values[2]
										current_list[l] = values[3]
										current_list[m] = values[4]
										current_list[n] = values[5]
										perms.append(current_list)
		unique_perms_list = self.make_perms_unique_and_add_to_all_perms(perms)
		num_unique_perms = len(unique_perms_list)
		logging.info(str(num_unique_perms) + ' permutations found.')

	def seven_values(self, values):
		logging.info('Finding permutations for: ' + str(values))
		perms = []
		if self.will_need_to_iterate_twice:
			for i in self.indeces_to_iterate_for_current_values[0]:
				for j in self.indeces_to_iterate_for_current_values[1]:
					for k in self.indeces_to_iterate_for_current_values[2]:
						for l in self.indeces_to_iterate_for_current_values[3]:
							for m in self.indeces_to_iterate_for_current_values[4]:
								for n in self.indeces_to_iterate_for_current_values[5]:
									for o in self.indeces_to_iterate_for_current_values[6]:
										if self.indeces_not_equal([i, j, k, l, m, n, o]):
											current_list = self.zero_list_all[:]
											current_list[i] = values[0]
											current_list[j] = values[1]
											current_list[k] = values[2]
											current_list[l] = values[3]
											current_list[m] = values[4]
											current_list[n] = values[5]
											current_list[o] = values[6]
											perms.append(current_list)
			for i in self.indeces_to_iterate_for_current_values_again[0]:
				for j in self.indeces_to_iterate_for_current_values_again[1]:
					for k in self.indeces_to_iterate_for_current_values_again[2]:
						for l in self.indeces_to_iterate_for_current_values_again[3]:
							for m in self.indeces_to_iterate_for_current_values_again[4]:
								for n in self.indeces_to_iterate_for_current_values_again[5]:
									for o in self.indeces_to_iterate_for_current_values_again[6]:
										if self.indeces_not_equal([i, j, k, l, m, n, o]):
											current_list = self.zero_list_all[:]
											current_list[i] = values[0]
											current_list[j] = values[1]
											current_list[k] = values[2]
											current_list[l] = values[3]
											current_list[m] = values[4]
											current_list[n] = values[5]
											current_list[o] = values[6]
											perms.append(current_list)
		else:
			for i in self.indeces_to_iterate_for_current_values[0]:
				for j in self.indeces_to_iterate_for_current_values[1]:
					for k in self.indeces_to_iterate_for_current_values[2]:
						for l in self.indeces_to_iterate_for_current_values[3]:
							for m in self.indeces_to_iterate_for_current_values[4]:
								for n in self.indeces_to_iterate_for_current_values[5]:
									for o in self.indeces_to_iterate_for_current_values[6]:
										if self.indeces_not_equal([i, j, k, l, m, n, o]):
											current_list = self.zero_list_all[:]
											current_list[i] = values[0]
											current_list[j] = values[1]
											current_list[k] = values[2]
											current_list[l] = values[3]
											current_list[m] = values[4]
											current_list[n] = values[5]
											current_list[o] = values[6]
											perms.append(current_list)
		unique_perms_list = self.make_perms_unique_and_add_to_all_perms(perms)
		num_unique_perms = len(unique_perms_list)
		logging.info(str(num_unique_perms) + ' permutations found.')

	def eight_values(self, values):
		logging.info('Finding permutations for: ' + str(values))
		perms = []
		if self.will_need_to_iterate_twice:
			for i in self.indeces_to_iterate_for_current_values[0]:
				for j in self.indeces_to_iterate_for_current_values[1]:
					for k in self.indeces_to_iterate_for_current_values[2]:
						for l in self.indeces_to_iterate_for_current_values[3]:
							for m in self.indeces_to_iterate_for_current_values[4]:
								for n in self.indeces_to_iterate_for_current_values[5]:
									for o in self.indeces_to_iterate_for_current_values[6]:
										for p in self.indeces_to_iterate_for_current_values[7]:
											if self.indeces_not_equal([i, j, k, l, m, n, o, p]):
												current_list = self.zero_list_all[:]
												current_list[i] = values[0]
												current_list[j] = values[1]
												current_list[k] = values[2]
												current_list[l] = values[3]
												current_list[m] = values[4]
												current_list[n] = values[5]
												current_list[o] = values[6]
												current_list[p] = values[7]
												perms.append(current_list)
			for i in self.indeces_to_iterate_for_current_values_again[0]:
				for j in self.indeces_to_iterate_for_current_values_again[1]:
					for k in self.indeces_to_iterate_for_current_values_again[2]:
						for l in self.indeces_to_iterate_for_current_values_again[3]:
							for m in self.indeces_to_iterate_for_current_values_again[4]:
								for n in self.indeces_to_iterate_for_current_values_again[5]:
									for o in self.indeces_to_iterate_for_current_values_again[6]:
										for p in self.indeces_to_iterate_for_current_values_again[7]:
											if self.indeces_not_equal([i, j, k, l, m, n, o, p]):
												current_list = self.zero_list_all[:]
												current_list[i] = values[0]
												current_list[j] = values[1]
												current_list[k] = values[2]
												current_list[l] = values[3]
												current_list[m] = values[4]
												current_list[n] = values[5]
												current_list[o] = values[6]
												current_list[p] = values[7]
												perms.append(current_list)
		else:
			for i in self.indeces_to_iterate_for_current_values[0]:
				for j in self.indeces_to_iterate_for_current_values[1]:
					for k in self.indeces_to_iterate_for_current_values[2]:
						for l in self.indeces_to_iterate_for_current_values[3]:
							for m in self.indeces_to_iterate_for_current_values[4]:
								for n in self.indeces_to_iterate_for_current_values[5]:
									for o in self.indeces_to_iterate_for_current_values[6]:
										for p in self.indeces_to_iterate_for_current_values[7]:
											if self.indeces_not_equal([i, j, k, l, m, n, o, p]):
												current_list = self.zero_list_all[:]
												current_list[i] = values[0]
												current_list[j] = values[1]
												current_list[k] = values[2]
												current_list[l] = values[3]
												current_list[m] = values[4]
												current_list[n] = values[5]
												current_list[o] = values[6]
												current_list[p] = values[7]
												perms.append(current_list)
		unique_perms_list = self.make_perms_unique_and_add_to_all_perms(perms)
		num_unique_perms = len(unique_perms_list)
		logging.info(str(num_unique_perms) + ' permutations found.')

	def nine_values(self, values):
		logging.info('Finding permutations for: ' + str(values))
		perms = []
		if self.will_need_to_iterate_twice:
			for i in self.indeces_to_iterate_for_current_values[0]:
				for j in self.indeces_to_iterate_for_current_values[1]:
					for k in self.indeces_to_iterate_for_current_values[2]:
						for l in self.indeces_to_iterate_for_current_values[3]:
							for m in self.indeces_to_iterate_for_current_values[4]:
								for n in self.indeces_to_iterate_for_current_values[5]:
									for o in self.indeces_to_iterate_for_current_values[6]:
										for p in self.indeces_to_iterate_for_current_values[7]:
											for q in self.indeces_to_iterate_for_current_values[8]:
												if self.indeces_not_equal([i, j, k, l, m, n, o, p, q]):
													current_list = self.zero_list_all[:]
													current_list[i] = values[0]
													current_list[j] = values[1]
													current_list[k] = values[2]
													current_list[l] = values[3]
													current_list[m] = values[4]
													current_list[n] = values[5]
													current_list[o] = values[6]
													current_list[p] = values[7]
													current_list[q] = values[8]
													perms.append(current_list)
			for i in self.indeces_to_iterate_for_current_values_again[0]:
				for j in self.indeces_to_iterate_for_current_values_again[1]:
					for k in self.indeces_to_iterate_for_current_values_again[2]:
						for l in self.indeces_to_iterate_for_current_values_again[3]:
							for m in self.indeces_to_iterate_for_current_values_again[4]:
								for n in self.indeces_to_iterate_for_current_values_again[5]:
									for o in self.indeces_to_iterate_for_current_values_again[6]:
										for p in self.indeces_to_iterate_for_current_values_again[7]:
											for q in self.indeces_to_iterate_for_current_values_again[8]:
												if self.indeces_not_equal([i, j, k, l, m, n, o, p, q]):
													current_list = self.zero_list_all[:]
													current_list[i] = values[0]
													current_list[j] = values[1]
													current_list[k] = values[2]
													current_list[l] = values[3]
													current_list[m] = values[4]
													current_list[n] = values[5]
													current_list[o] = values[6]
													current_list[p] = values[7]
													current_list[q] = values[8]
													perms.append(current_list)
		else:
			for i in self.indeces_to_iterate_for_current_values[0]:
				for j in self.indeces_to_iterate_for_current_values[1]:
					for k in self.indeces_to_iterate_for_current_values[2]:
						for l in self.indeces_to_iterate_for_current_values[3]:
							for m in self.indeces_to_iterate_for_current_values[4]:
								for n in self.indeces_to_iterate_for_current_values[5]:
									for o in self.indeces_to_iterate_for_current_values[6]:
										for p in self.indeces_to_iterate_for_current_values[7]:
											for q in self.indeces_to_iterate_for_current_values[8]:
												if self.indeces_not_equal([i, j, k, l, m, n, o, p, q]):
													current_list = self.zero_list_all[:]
													current_list[i] = values[0]
													current_list[j] = values[1]
													current_list[k] = values[2]
													current_list[l] = values[3]
													current_list[m] = values[4]
													current_list[n] = values[5]
													current_list[o] = values[6]
													current_list[p] = values[7]
													current_list[q] = values[8]
													perms.append(current_list)
		unique_perms_list = self.make_perms_unique_and_add_to_all_perms(perms)
		num_unique_perms = len(unique_perms_list)
		logging.info(str(num_unique_perms) + ' permutations found.')

	def reset_values_to_sum_variables(self):
		self.indeces_to_iterate_for_current_values = []
		self.indeces_to_iterate_for_current_values_again = []
		self.will_need_to_iterate_twice = False
		self.more_than_one_value_must_occur_at_non_hubs = False

	def more_than_one_value_must_occur_outside_of_hubs(self, values):
		return ((len(values) - 1) > self.max_different_removals_hubs)

	def values_to_sum_contain_less_than_two_ones(self, values):
		return (values.count(1) < 2)

	def append_to_beginning_of_indeces_to_iterate_for_current_values(self, list_of_lists_to_append):
		for a_list in list_of_lists_to_append:
			self.indeces_to_iterate_for_current_values.append(a_list)

	def append_to_beginning_of_indeces_to_iterate_for_current_values_again(self, list_of_lists_to_append):
		for a_list in list_of_lists_to_append:
			self.indeces_to_iterate_for_current_values_again.append(a_list)

	def append_to_end_of_indeces_to_iterate_for_current_values(self, values_to_edit):
		for value in values_to_edit:
			for r in self.ranges:
				current_min = r[0]
				current_max = r[1]
				if (value >= current_min) and (value <= current_max):
					self.indeces_to_iterate_for_current_values.append(self.valid_indeces_for_ranges[str(r)])

	def append_to_end_of_indeces_to_iterate_for_current_values_again(self, values_to_edit):
		for value in values_to_edit:
			for r in self.ranges:
				current_min = r[0]
				current_max = r[1]
				if (value >= current_min) and (value <= current_max):
					self.indeces_to_iterate_for_current_values_again.append(self.valid_indeces_for_ranges[str(r)])

	def remove_values_for_which_index_lists_have_been_found(self, values_to_edit, values_to_remove):
		for value in values_to_remove:
			values_to_edit.remove(value)
		return values_to_edit

	def find_indeces_to_iterate(self, values):
		self.reset_values_to_sum_variables()
		values_to_edit = values[:]
		if self.max_removals_non_hubs == 2:
			if self.more_than_one_value_must_occur_outside_of_hubs(values):
				self.more_than_one_value_must_occur_at_non_hubs = True
				if self.values_to_sum_contain_less_than_two_ones(values):
					raise Exception("Two values must occur at non-hubs to generate permutations for this sum.")
				else:
					self.append_to_beginning_of_indeces_to_iterate_for_current_values([self.num_non_hubs, self.num_non_hubs])
					values_to_edit = self.remove_values_for_which_index_lists_have_been_found(values_to_edit, [1, 1])
					self.append_to_end_of_indeces_to_iterate_for_current_values(values_to_edit)
			else:
				if values.count(2) > 0:
					if values.count(1) >= 2: # 2 occurs at least once, 1 occurs at least twice
						self.will_need_to_iterate_twice = True
						# first iteration
						list_of_lists_to_append = []
						list_of_ones_and_two = []
						for i in range(values.count(1)):
							list_of_ones_and_two.append(1)
							list_of_lists_to_append.append(self.num_hubs) # all 1s iterate through hubs only
						list_of_ones_and_two.append(2)
						list_of_lists_to_append.append(self.num_non_hubs) # 2 iterates through non-hubs only
						self.append_to_beginning_of_indeces_to_iterate_for_current_values(list_of_lists_to_append)
						values_to_edit = self.remove_values_for_which_index_lists_have_been_found(values_to_edit, list_of_ones_and_two)
						self.append_to_end_of_indeces_to_iterate_for_current_values(values_to_edit)
						# second iteration
						values_to_edit = values[:]
						self.append_to_beginning_of_indeces_to_iterate_for_current_values_again([self.num_all, self.num_all]) # two 1s iterate through everything
						values_to_edit = self.remove_values_for_which_index_lists_have_been_found(values_to_edit, [1, 1])
						self.append_to_end_of_indeces_to_iterate_for_current_values_again(values_to_edit)
					elif values.count(1) == 1: # 2 occurs at least once, 1 occurs only once
						self.will_need_to_iterate_twice = True
						# first iteration
						self.append_to_beginning_of_indeces_to_iterate_for_current_values([self.num_hubs, self.num_non_hubs])
						values_to_edit = self.remove_values_for_which_index_lists_have_been_found(values_to_edit, [1, 2])
						self.append_to_end_of_indeces_to_iterate_for_current_values(values_to_edit)
						# second iteration
						values_to_edit = values[:]
						self.append_to_beginning_of_indeces_to_iterate_for_current_values_again([self.num_all])
						values_to_edit = self.remove_values_for_which_index_lists_have_been_found(values_to_edit, [1])
						self.append_to_end_of_indeces_to_iterate_for_current_values_again(values_to_edit)
					elif values.count(1) == 0: # 2 occurs at least once, 1 never occurs
						self.append_to_beginning_of_indeces_to_iterate_for_current_values([self.num_all_2_removals])
						values_to_edit = self.remove_values_for_which_index_lists_have_been_found(values_to_edit, [2])
						self.append_to_end_of_indeces_to_iterate_for_current_values(values_to_edit)
				elif values.count(2) == 0:
					if values.count(1) >= 2: # 2 never occurs, 1 occurs at least twice
						self.append_to_beginning_of_indeces_to_iterate_for_current_values([self.num_all, self.num_all])
						values_to_edit = self.remove_values_for_which_index_lists_have_been_found(values_to_edit, [1, 1])
						self.append_to_end_of_indeces_to_iterate_for_current_values(values_to_edit)
					elif values.count(1) == 1: # 2 never occurs, 1 occurs once
						self.append_to_beginning_of_indeces_to_iterate_for_current_values([self.num_all])
						values_to_edit = self.remove_values_for_which_index_lists_have_been_found(values_to_edit, [1])
						self.append_to_end_of_indeces_to_iterate_for_current_values(values_to_edit)
					elif values.count(1) == 0: # 2 never occurs, 1 never occurs
						self.append_to_end_of_indeces_to_iterate_for_current_values(values_to_edit)
		else:
			if values.count(1) > 0: 
				self.append_to_beginning_of_indeces_to_iterate_for_current_values([self.num_all])
				values_to_edit = self.remove_values_for_which_index_lists_have_been_found(values_to_edit, [1])
				self.append_to_end_of_indeces_to_iterate_for_current_values(values_to_edit)
			if values.count(1) == 0:
				self.append_to_end_of_indeces_to_iterate_for_current_values(values_to_edit)








