def init():

	global hubs
	hubs = ['ATL', 'CVG', 'DTW', 'LAX', 'MSP', 'SEA', 'SLC']

	global state_regions_without_hubs
	state_regions_without_hubs = ['AL', 'AR-LA', 'AR-OK', 'CT-RI-MA', 'DE-NJ-PA', 'GA', 'IA-IL', 'ID', 
		'ID-MT', 'IL', 'IL-IN-MI', 'IN', 'KS-MO', 'KY-OH', 'LA', 'MD-VA-PA', 'MI', 'MN', 'MO-AR', 'MS', 
		'MT', 'NC', 'NCA', 'ND', 'NFL', 'NH-VT-ME', 'NM-CO', 'NNY', 'NV-AZ-TX', 'NV-UT', 'OH', 'OR', 
		'PA', 'SC', 'SCA', 'SD-NE', 'SFL', 'SNY', 'TN', 'TX', 'VA', 'WA', 'WI', 'WI-MI', 'WV-VA', 'WY']

	global state_regions
	state_regions = ['ATL', 'CVG', 'DTW', 'LAX', 'MSP', 'SEA', 'SLC', 'AL', 'AR-LA', 'AR-OK', 
		'CT-RI-MA', 'DE-NJ-PA', 'GA', 'IA-IL', 'ID', 'ID-MT', 'IL', 'IL-IN-MI', 'IN', 'KS-MO', 'KY-OH', 
		'LA', 'MD-VA-PA', 'MI', 'MN', 'MO-AR', 'MS', 'MT', 'NC', 'NCA', 'ND', 'NFL', 'NH-VT-ME', 
		'NM-CO', 'NNY', 'NV-AZ-TX', 'NV-UT', 'OH', 'OR', 'PA', 'SC', 'SCA', 'SD-NE', 'SFL', 'SNY', 
		'TN', 'TX', 'VA', 'WA', 'WI', 'WI-MI', 'WV-VA', 'WY']

	global engine_subtypes
	engine_subtypes = ['BR700-715C1-30', 'CF6-80C2B8F', 'CFM56-5A', 'CFM56-5B3-3', 'CFM56-7B26',
		'CFM56-7B27E-B1F', 'PW2000-2037', 'PW2000-2040', 'TRENT8-892-17', 'V2500-D5']

	'''
	A dictionary that holds all possible states in the MDP as a list of lists for each total number 
	of working engines.

	Structure:
	{number of working engines: [
		[ATL, CVG, DTW, LAX, MSP, SEA, SLC], ...], ...}

	Example:
	{1: [
		[0, 0, 1, 0, 0, 0, 0], 
		[0, 0, 0, 0, 0, 1, 0], 
		[0, 1, 0, 0, 0, 0, 0], 
		[0, 0, 0, 1, 0, 0, 0], 
		[0, 0, 0, 0, 0, 0, 1], 
		[1, 0, 0, 0, 0, 0, 0], 
		[0, 0, 0, 0, 1, 0, 0]], ...}
	'''
	global all_possible_states
	all_possible_states = {}

	'''
	A dictionary that holds all possible actions in the MDP as a list of lists for each engine subtype.

	Structure:

	Example:
	'''
	global all_possible_actions
	all_possible_actions = {}

	'''
	A dictionary that holds all possible removal situations as a list of lists for each engine subtype.

	Structure:

	Example:
	'''
	global all_possible_removal_situations
	all_possible_removal_situations = {}

	'''
	A dictionary that holds information for the number of engines for each engine subtype.

	Structure:
	{'ENGINE SUBTYPE': {
		'NUM_BROKEN_ENGINES_ATL': number of engines broken and being held at ATL,
		'NUM_BROKEN_ENGINES_MSP': number of engines broken and being held at MSP,
		'NUM_WORKING_ENGINES': number of engines working and available for removals,
		'TOTAL_NUM_ENGINES': total number of engines for this type}, ...}

	Example:
	{'JT8D-219': {
		'NUM_BROKEN_ENGINES_ATL': 0,
		'NUM_BROKEN_ENGINES_MSP': 0,
		'NUM_WORKING_ENGINES': 4,
		'TOTAL_NUM_ENGINES': 4}, ...}
	'''
	global num_engines_info
	num_engines_info = {}

	'''
	A dictionary that holds information for the number of removals for each engine subtype.

	Structure:
	{'ENGINE SUBTYPE': {
		'MAX_NUM_REMOVALS_MONTHLY_ATL': max number of removals that have ever occurred in one month at ATL,
		'MAX_NUM_REMOVALS_MONTHLY_CVG': max number of removals that have ever occurred in one month at CVG,
		'MAX_NUM_REMOVALS_MONTHLY_DTW': max number of removals that have ever occurred in one month at DTW,
		'MAX_NUM_REMOVALS_MONTHLY_LAX': max number of removals that have ever occurred in one month at LAX,
		'MAX_NUM_REMOVALS_MONTHLY_MSP': max number of removals that have ever occurred in one month at MSP,
		'MAX_NUM_REMOVALS_MONTHLY_NON_HUBS': max number of removals that have ever occurred in one month outside of hubs,
		'MAX_NUM_REMOVALS_MONTHLY_SEA': max number of removals that have ever occurred in one month at SEA,
		'MAX_NUM_REMOVALS_MONTHLY_SLC': max number of removals that have ever occurred in one month at SLC,
		'MAX_NUM_REMOVALS_MONTHLY_TOTAL': max number of total removals that have ever occurred in one month}, ...}

	Example:
	{'CF6-80C2B6': {
		'MAX_NUM_REMOVALS_MONTHLY_ATL': 2,
		'MAX_NUM_REMOVALS_MONTHLY_CVG': 0,
		'MAX_NUM_REMOVALS_MONTHLY_DTW': 0,
		'MAX_NUM_REMOVALS_MONTHLY_LAX': 1,
		'MAX_NUM_REMOVALS_MONTHLY_MSP': 0,
		'MAX_NUM_REMOVALS_MONTHLY_NON_HUBS': 1,
		'MAX_NUM_REMOVALS_MONTHLY_SEA': 0,
		'MAX_NUM_REMOVALS_MONTHLY_SLC': 1,
		'MAX_NUM_REMOVALS_MONTHLY_TOTAL': 2}, ...}
	'''
	global num_removals_info
	num_removals_info = {}

	'''
	A dictionary that holds the default expected AOS cost for each engine subtype.

	Structure:
	{'ENGINE SUBTYPE': default expected AOS cost, ...}

	Example:
	{'BR700-715C1-30': 4525.0,
	 'CF6-80C2B6': 13121.0,
	 'CF6-80C2B6F': 8200.0,
	 'CF6-80C2B8F': 8580.0,
	 'CF6-80E1A4': 22403.0,
	 'CFM56-5A': 5053.5,
	 'CFM56-5B3-3': 8843.0, ...}
	'''
	global aos_cost
	aos_cost = {}

	'''
	A dictionary that holds the expected cost to transport an engine from a hub to an airport within a
	state region. 

	Structure:
	{'ENGINE SUBTYPE': {
		'STATE REGION': {
			'HUB': expected transport cost, ...}, ...}, ...}
	
	Example:
	{'V2500-D5': {
		'AL': {
			'ATL': 9500.811429,
			'CVG': 9960.96,
			'DTW': 10502.53714,
			'LAX': 12685.02857,
			'MSP': 10787.34857,
			'SEA': 13356.46,
			'SLC': 11813.42857},
		'AR-LA': {
			'ATL': 10196.244,
			'CVG': 10264.128,
			'DTW': 10787.808,
			'LAX': 11982.336,
			'MSP': 10504.404,
			'SEA': 12835.884,
			'SLC': 11276.0}, ...}, ...}

	'''
	global expected_transport_cost
	expected_transport_cost = {}

	'''
	A dictionary that holds the regression values to calculate the probabilities of removals for
	purposes of solving the MDP.

	Structure:
	{'ENGINE SUBTYPE': {
		'REMOVAL LOCATION': {
			'D': departure count coefficient, 
			'RR': RON/RAD ground time coefficient, 
			'intercept': y-intercept}, ...}, ...}
	
	Example:
	{'PW2000-2040': {
		'ATL': {
			'D': -0.00667, 'RR': -1e-05, 'intercept': 0.92},
		'DTW': {
			'D': -0.443, 'RR': 9.9e-05, 'intercept': 0.2},
		'LAX': {
			'D': -0.0009, 'RR': 0.000216, 'intercept': -5.03},
		'MSP': {
			'D': 0.01805, 'RR': 2.9e-05, 'intercept': -8.06},
		'OTHER': {
			'D': -0.00256, 'RR': -4.4e-05, 'intercept': 0.62}, ...}, ...}
	'''
	global regression
	regression = {}

	'''
	A dictionary that holds the probabilities associated with a number of engines being repaired
	within the month based on the number of engines that are broken.

	Structure:
	{'ENGINE SUBTYPE': {
		number engines broken: {
			number engines repaired: probability, ...}, ...}, ...}
	
	Example:
	{'CF6-80C2B8F': {
		1: {
			0: 0.579578279, 
			1: 0.420421721},
		2: {
			0: 0.335910981, 
			1: 0.366448343, 
			2: 0.297640676},
		3: {
		 	0: 0.194686708,
			1: 0.31857825,
			2: 0.260654932,
			3: 0.22608011}, ...}, ...}
	'''
	global probability_of_num_repair_given_num_broken
	probability_of_num_repair_given_num_broken = {}

	global num_departures_by_hub_monthly
	num_departures_by_hub_monthly = {}

	global total_departures_ground_time_by_state_region_monthly
	total_departures_ground_time_by_state_region_monthly = {}

	global total_RONSRADS_ground_time_by_hub_monthly
	total_RONSRADS_ground_time_by_hub_monthly = {}



