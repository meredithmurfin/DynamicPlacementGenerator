# DynamicPlacementGenerator

The DynamicPlacementGenerator is a Python program used to generate the best spare engine placement for a specific aircraft fleet. 

## Background

Delta Air Lines is an industry-leading, globally operating United States airline servicing over 300 destinations with a fleet of approximately 900 aircraft. Delta’s Engine Demand Planning team (EDP), which falls under Delta TechOps, is responsible for planning engine removals, assigning spare engines to seven designated hubs, and setting up the logistics of the removals and repairs of these engines.

The objective of this project is to assist Delta’s EDP team with improving the allocation of spare engines across the contiguous United States. To assist Delta in decreasing both transportation and AOS costs incurred throughout the year, the solution determines the optimal configuration of all spare engines on a monthly basis through a Markov Decision Process. The solution outputs a configuration recommendation for the upcoming month associated with the minimal cost of all possible options. Delta’s EDP team can use the model to make data-informed, cost-driven decisions with the added benefit of reducing required labor hours.

## Installations and Setup

Instructions to install the required installations are outlined below with provided terminal commands. 

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

### After Cloning this Repository

Navigate to the `DynamicPlacementGenerator` directory (wherever you cloned it on your machine). 

This application uses the [`pymdptoolbox` module](https://github.com/sawcordwell/pymdptoolbox "Markov Decision Process (MDP) Toolbox for Python"). Clone the repository for it with the following command. **Make sure you are cloning the repository while in the `DynamicPlacementGenerator` directory.**
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

Some files will need to be created to use for all subsequent runs. Most of these tasks will only need to be completed once.

### Subsequent Runs

Navigate to the `DynamicPlacementGenerator` directory.

In your terminal, run the following command:
```
python3 app.py
```

**It's already set up to solve the MDP for the -5A only.**

## Notes

max that can occur at non-hubs = 2
max that can occur at hubs = 10
min that can occur at hubs = 1
max removals total that can occur = 10
max total working engines = 5

changing all inputs and re-running all possible removal situations adds time to the run time. It took me about 1 hour and 30 minutes to generate all possible removal situations for all fleets.# DynamicPlacementGenerator

## Authors

**Industrial and Systems Engineering, Georgia Institute of Technology**, Spring 2020

**Team 10**
Samantha Davanzo
Brian Davis
Mary Elizabeth Davis
Bella Jackson
Meredith Thacker
Miles Trumbauer

