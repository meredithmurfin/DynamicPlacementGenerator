# DynamicPlacementGenerator

## Installations

Install `python3`. Check the version and you should see the same as the output below or a more recent version.
```
python3 --version
Python 3.7.6
```

Install `pip3`. Check that you have it by running the command below to check the version.
``` 
pip3 -V
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

Clone this repository.

After doing that, navigate to the `DynamicPlacementGenerator` directory (wherever you cloned it on your machine) and clone the Git repository for `pymdptoolbox` with the following terminal command:
```
git clone https://github.com/sawcordwell/pymdptoolbox.git
```

Navigate to the `pymdptoolbox`.
```
cd pymdptoolbox
```

Install `pymdptoolbox` using the following terminal command (while in the `pymdptoolbox` directory):
```
python3 setup.py install
```

## To run locally

Clone this repository onto your local machine.
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
