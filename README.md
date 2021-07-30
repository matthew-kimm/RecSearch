# RecSearch
A tool for research on recommender systems.

## Table of Contents
* [Description](#Description)
* [How To Start](#How-To-Start)
* [How It Works](#How-It-Works)
* [DataWorkers](#DataWorkers)
* [How To Extend](#How-To-Extend)
* [Tutorial](#Tutorial)

## Description
RecSearch is a tool for conducting research on 
top-n collaborative filtering based recommender systems.

## How To Start
### Install Python 3.9
Install Python 3.9 (add to PATH if not automatic)

### Install Requirements
#### Windows
Run `py -3.9 -m pip install -r requirements.txt`

#### Mac/Linux
Run `python3.9 -m pip install -r requirements.txt`

### Running the program
Download this repository and run `__main__.py` using Python version 3.9.0 or greater  to start the GUI
#### Windows
`py -3.9 __main__.py`
#### Mac/Linux
`python3.9 __main__.py`

### Why Python3.9?
* Usage of removeprefix(), removesuffix() [PEP616, 3.9]
* Usage of the walrus operator [PEP572, 3.8]

Requires
* configobj 5.0.6 (for .cfg files functioning like multilevel .ini files)
* numpy (scientific computing)
* pandas (data manipulation)
* PySimpleGUI (for GUI)
* scipy (for computation of t-statistic)
* matplotlib (for plotting summary)
* openpyxl (writing xlsx files)

## How It Works
### Idea
DataWorkers are the abstraction of steps in the recommendation system process.
Each DataWorker does its job, in order of precedence, using an appropriate DataInterface.
Both of these abstractions are controlled
by an external configuration file (.cfg), created by a GUI,
detailing the base experiment to be conducted.
Further, other experiment factors such as number of repeats (random samplings),
starting random seed, varying parameters (1D)
are controlled by a simpler configuration file (.ini) also created by a GUI.
Finally, the experiment summarizations (tables and plots) are controlled by
a set of simple configuration files (.sum) created by a GUI.

### Data
Data should be able to be split into historical items with ratings and target items with ratings,
the historical items will likely be separated from the target items by time, that is,
given a user's item history up to a certain point how did the user rate items after this point.

### Workflow
* Generate .cfg as a base for experiment
  * Use a splitter, neighborhoods, recommenders, metrics, comparers
* Generate .ini detailing how to run grand experiment 
  * Select parameter for variation (if desired and can select same parameter in multiple dataworkers)
  * Set number of repetitions to conduct
* Run .ini experiment file
* Generate .sum file for pulling in all the data and combining the comparers
* Run .sum file
* View Summary Tables and use right-click menu to export
* Plot Summary and save figure

(Note: Use Ctrl+click to select multiple single items in GUI,
and Shift+click to select items between a first click and the Shift+click.)


## DataWorkers
***
### Splitters
General DataWorker used to split the experiment data into train and test sets to support the experiment. Only one per experiment named Default.
#### percent
Splits the data by percentages.

e.g.
* train: 0.8
  
* test: 0.2
#### query
Splits the data by query.

e.g. (if a column user_year is in dataset)

* train: user_year in [2015, 2016, 2017, 2018]
  
* test: user_year in [2019]

***
### Neighborhoods
DataWorker used to find neighbors of users in the test set from the train set.

#### global
Every user in the train set is a neighbor.

#### attribute_match
Every user in the train set with matching specified attributes
is a neighbor.

#### grade_match
Every user in the train set with at least one matching item, item rating pair
is a neighbor.

#### grade_attribute_match
Every user in the train set with matching specified attributes and at least one matching item, rating pair
is a neighbor.
***
### Filters (Optional)
DataWorker that computes or looks-up a list of appropriate items for recommendation.

#### onfly_boolean
For the domain of academic course recommendation, uses partial information of academic state 
to derive classes above/below current academic state, that is,
not meeting prerequisites or classes below current academic level.

#### precomputed_boolean
Uses a precomputation of the onfly_boolean, that is,
a datatable with user and items to avoid recommending (filter out), for filtering.

***
### Recommenders
DataWorker that uses a neighborhood and train set target ratings to provide a list of ordered recommendations for users in the test set.

#### courseavg
Items rated by neighbors ordered by best average rating for the neighborhood,
provided enough neighbors rated the item.

#### popular
Items rated by neighbors ordered by most frequent (popular).

#### hits
Items rated by neighbors utilizing mutually reinforcing relationship between users and items based on ratings.

#### hitsmm_update
Items rated using hits on a directed weighted graph where proportions 
of neighborhood users rating above a threshold are used as the edge weights.

#### actual (Dummy Recommender)
The items actually selected by the user with ratings.
 
***
### Metrics
DataWorker that maps each recommendation of a test user to a numerical value, likely based off actual ratings.
Maps the list of recommendations to a list of numbers.

#### match_recommended
Evaluates to 1 if recommended item appears in target recommendation (actual) and 0 otherwise.

#### passed
Evaluates to 1 if recommended item appears in target recommendation with a rating above a desired threshold and 0 otherwise.

***
### Comparers
Maps the list of numerical values from the metric into a single numerical value.
The comparison can be with respect to a certain recommender (e.g. actual) which will evaluate recommendations up to
the length of that recommender,
or the length can optionally be set to override, e.g. length = 10 to compare up to top ten.

#### count
Sums the metric, to a desired length, of each test user;
e.g. count on match_recommended yields the number of realized recommendations.

#### quotient
Divides the metric of one recommender by another (when possible), likely used with a dummy recommender.
***

## How To Extend
### DataWorkers
* Add DataWorker to `RecSearch/DataWorkers/MyDataWorker.py`.
* DataWorker `.py` files must start with an uppercase alphabetical character.
* DataWorker configuration described in `RecSearch/Config/ConfigManagement.py`
* DataWorkers take a name (to reference columns of created data), a configuration dictionary,
  and an ExperimentData object (holds the experiment data).
* Calling the DataWorkers dowork() method should append column(s) of data to the ExperimentData.


### DataInterfaces
* Add DataInterface to `RecSearch/DataInterfaces/MyDataWorker/my_data_interface.py`.
* DataInterfaces `.py` files must start with a lowercase alphabetical character to be found.
* DataInterface configuration described in `RecSearch/Config/ConfigManagement.py`
* DataInterface `.py` file should implement an abstract class described in
  `RecSearch/DataInterfaces/MyDataWorker/Abstract.py` using the naming convention `IX*` for the implemented class
  which overrides an abstract method following the naming convention `iget_*`

### GUI
By following the configuration management scheme, all options are automatically added to the GUI
assuming an appropriate GUI element and scheme is already available.
Further, type-checking and interpolation is handled by ConfigObj,
and new input validation functions can be specified in `RecSearch/Config/ConfigValidator`

## Tutorials
* [Formatting Data](RecSearch/Tutorials/Formatting_Data.md)
* [Using the GUI](RecSearch/Tutorials/Using_the_GUI.md)
