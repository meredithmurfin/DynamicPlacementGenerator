# DynamicPlacementGenerator

The DynamicPlacementGenerator is a Python program used to generate the best spare engine placement for a specific aircraft fleet. 

## Background

Delta Air Lines is an industry-leading, globally operating United States airline servicing over 300 destinations with a fleet of approximately 900 aircraft. Delta’s Engine Demand Planning team (EDP), which falls under Delta TechOps, is responsible for planning engine removals, assigning spare engines to seven designated hubs, and setting up the logistics of the removals and repairs of these engines.

The objective of this project is to assist Delta’s EDP team with improving the allocation of spare engines across the contiguous United States. To assist Delta in decreasing both transportation and AOS costs incurred throughout the year, the solution determines the optimal configuration of all spare engines on a monthly basis through a Markov Decision Process. The solution outputs a configuration recommendation for the upcoming month associated with the minimal cost of all possible options. Delta’s EDP team can use the model to make data-informed, cost-driven decisions with the added benefit of reducing required labor hours.

## Installations and Setup

Instructions to install the required installations are outlined below with provided terminal commands. These instructions assume basic understanding of using Terminal on Mac. If your machine is not a Mac, these instructions may need to be altered slightly. 

### Before Cloning this Repository

Install `python3`. Check that your version matches the one below or is more recent.
```
python3 --version
Python 3.7.6
```

Install `pip3`. Check that you have it by running the command below to check the version. You should see a response similar to the one below.
``` 
pip3 -V
pip 19.3.1 from /usr/local/lib/python3.7/site-packages/pip (python 3.7)
```

Install `numpy` using `pip3`.
```
pip3 install numpy
```

Install `pandas` using `pip3`.
```
pip3 install pandas
```

Install `scipy` using `pip3`.
```
pip3 install scipy
```

### Clone this Repository

To clone this repository, navigate to the folder in your terminal that you would like it to be in. Then run the following command:
```
git clone https://github.com/meredithmurfin/DynamicPlacementGenerator.git
```

You should then be able to use this command to be in the local `DynamicPlacementGenerator` directory on your machine:
```
cd DynamicPlacementGenerator
```

### After Cloning this Repository

This application uses the [`pymdptoolbox` module](https://github.com/sawcordwell/pymdptoolbox "Markov Decision Process (MDP) Toolbox for Python"). Clone the repository for it with the following command. **Make sure you are cloning the repository while in the `DynamicPlacementGenerator` directory on your machine.**
```
git clone https://github.com/sawcordwell/pymdptoolbox.git
```

Navigate to the `pymdptoolbox` folder, which now resides in the `DynamicPlacementGenerator` directory.
```
cd pymdptoolbox
```

Setup and install `pymdptoolbox` using the following terminal command (while in the `pymdptoolbox` directory):
```
python3 setup.py install
```

## Usage

### First Run 

Some files will need to be created to use for all subsequent runs. These tasks will only need to be completed once per machine this program is used on.

Navigate to the `DynamicPlacementGenerator` directory. Run the following command to set the `FIRST_RUN` environment variable to indicate this is the first time running this program on your machine:
```
export FIRST_RUN=true
```

Doing this will create the following for future use:
- All possible states exported to a file
- All possible actions exported to a file 
- All possible removal situations for each engine type exported to a file

### Subsequent Runs

The `FIRST_RUN` environment variable can be set to FALSE for all future runs.
```
export FIRST_RUN=false
```

Prior to running this program each month, a few files need to be updated.

#### Update Future Flight Information

For each engine type, update:
- `total_RONSRADS_ground_time_by_hub_monthly.csv`
- `total_departures_ground_time_by_state_region_monthly.csv`
- `num_departures_by_hub_monthly.csv`

These files can be found in `DynamicPlacementGenerator/data_to_read/engine_subtype/`. 

**It is very important that the format of these files stays the same as the examples that are currenty provided.** You must provide data for each engine subtype for the next 3 months. Below are descriptions of the structure for each, but we have provided file examples for each engine subtype already in the folders that reflect accurate data needed to run this program for January 2019. 

The files look similar to this:

| YEAR-MONTH	| ATL 	| CVG 	| DTW 	| LAX 	| MSP 	| SEA 	| SLC 	| OTHER 	|
| ------------- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | --------- |
| 2019-01		| 26159 | 2606	| 42975 | 11590 | 28155 | 38375 | 34586 | 975834	|
| 2019-02		| 24378 | 2067	| 36572 | 10296 | 32870 | 29834 | 36271 | 999810	|
| 2019-03		| 20976 | 3890	| 9786  | 9875  | 35019 | 40192 | 30289 | 967182	|

The `us_airport_data.csv` file located in `DynamicPlacementGenerator/data_to_read/` provides information on all airports used for this project. Any reference to *all airports* is only referring to airports listed in this file. The information for each airport includes:
- 3-letter IATA code
- Name
- Address
- State
- State Region (regions created by our group defined mostly by state lines)
- Closest hub by distance, with distance in miles
- Closest hub by travel time, with travel time in minutes

**`total_RONSRADS_ground_time_by_hub_monthly.csv`**

This file contains the summed monthly total ground time (in minutes) of all departures defined as a RON or RAD for each hub. The summed total for all airports excluding hubs is included in the OTHER column.

**`total_departures_ground_time_by_state_region_monthly.csv`**

This file contains the summed monthly total ground time (in minutes) of all departures for each hub and state region. 

**`num_departures_by_hub_monthly.csv`**

This file contains the monthly count of departure occurrences for each hub. The count of departure occurrences for all airports excluding hubs is included in the OTHER column.

#### Update Information to Reflect Current State/System

**`data_to_read/removal_info.csv`**

This file contains information on expected number of removals for each engine subtype. This will most likely not need to be updated often. For each engine subtype, the following is specified:
- Expected maximum number of removals in a month for all airports
- Expected maximum number of removals in a month for each specific hub
- Expected maximum number of removals in a month for all airports excluding hubs
- Expected AOS cost
- Whether or not these files were updated from the previous month (if any of the data for a subtype has been updated, make sure to set the UPDATED column value for that row to be TRUE)

Our team based these values on past removal data for each type. We set the maximum number of removals that could happen based on data from 2015-2019 by taking the maximum that had ever occurred for each and adding 1 to it. For example, if no more than 3 removals ever occurred in ATL, we assumed the maximum number of removals that could ever happen at ATL would be 4.

Limitations:
- The maximum number of removals for all airports cannot be less than 1 or greater than 10
- The maximum number of removals for each specific hub cannot be greater than 10
- The maximum number of removals for all airports excluding hubs cannot be greater than 2

The purpose of this file is to minimize the iterations the program runs so that runtime is reduced and extremely unlikely situations are not considered.

**`data_to_read/engine_info.csv`**

This file contains information on engine numbers for each engine subtype. This will probably need to be updated each month. For each engine subtype, the following is specified:
- Total number of current spare engines 
- Number of current working spare engines
- Number of current broken spare engines being repaired at ATL
- Number of current broken spare engines being repaired at MSP
- Number of working spare engines currently being stored at each hub

Limitations:
- The total number of current spare engines cannot be less than 1 and cannot be greater than 5

The purpose of this file is to understand the current state being considered so that the action to take associated with the minimum cost is returned.

#### Run the Program

Navigate to the `DynamicPlacementGenerator` directory if you aren't there already.

In your terminal, run the following command:
```
python3 app.py
```

The program may take several hours to run. 

## Authors

**Industrial and Systems Engineering, Georgia Institute of Technology**, Spring 2020

**Team 10**
- Samantha Davanzo
- Brian Davis
- Mary Elizabeth Davis
- Bella Jackson
- Meredith Thacker
- Miles Trumbauer

