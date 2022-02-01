# Demo
## Formatting Data
[Download MovieLens 100K Data](https://grouplens.org/datasets/movielens/100k/)

100,000 ratings from 1,000 users on 1,700 movies.

For the demo, move the u.data file to ```./Movie/movie.csv```.

Then, run ```format_demo_data.py```.

The resulting data (```./Movie/formatted_movie_data.csv```) is of the form:

<table>
<tr>
  <th>Index</th>
  <th>Item</th>
  <th>Rating</th>
  <th>Term</th>
</tr>

<tr>
  <td>1</td>
  <td>"300"</td>
  <td>5</td>
  <td>0</td>
</tr>

<tr>
  <td>1</td>
  <td>"255</td>
  <td>1</td>
  <td>0</td>
</tr>

<tr>
  <td>1</td>
  <td>"715"</td>
  <td>3</td>
  <td>1</td>
</tr>

<tr>
  <td>...</td>
  <td>...</td>
  <td>...</td>
  <td>...</td>
</tr>
</table>

Then, using the GUI select ```Tools > Data Formatter```.

Select ```Browse``` under ```item_history_data```.

Navigate to, select, and open ```./Movie/formatted_movie_data.csv```.

Set ```target_coded_term``` to ```1```.

Under ```output_data``` select ```Save As``` and enter ```final_movie_data``` to save the result as ```final_movie_data.csv```.

Press the ```Format Data``` button to output and save the result.

The data is now in the correct format.

## Creating a Base Configuration
1. Select ```Generate Experiment/Base Config (CFG)```.
2. Select ```NEW CONFIG```.
3. Load the ```final_movie_data.csv``` file.
4. Select all columns for ``Use Columns``.
5. Select Index for ```Index```.
6. Select Item_History and Item_Rating for ```List/Dict Columns``` (history and ratings stored as a dictionary).
7. Press the ```Save Data Config``` button.

### Configuring the Splitter
1. Select the ```Worker Config``` tab.
2. Select ```percent``` for method.
3. Select the ```Interface Config``` tab.
4. Press the ```Launch``` button.
5. Press ```Submit``` to keep the default 80% train and 20% test split.
6. Select ```View```.
7. Press the ```Add/Update``` button.

### Configuring the Neighborhoods
1. Select ```Neighborhoods```.
2. Give the worker a name (must be a valid python identifier of length < ~200 characters), e.g. ```movie_history_rating_match```.
3. Select ```grade_match``` for method (matches item, rating pairs in history).
4. Set ```min_neighbors``` to 10.
5. Launch the interface configuration similar to the splitter case.
6. Choose ```Item_History``` for ```item_history_col``` and press submit.
7. Add/Update this neighborhood worker similar to the splitter case.

### Configuring Recommenders
#### HITSMM
1. Add a recommender with method ```hitsmm```.
2. In the interface configuration, select the previously configured neighborhood for the ```n_column```.
3. Set ```ir_column``` to ```Item_Rating```.
4. Set the required rating to ```5``` (out of 5).
5. Set xi to ```0.9```, tol to ```1e-6```, and max_iter to ```100```.
6. Submit and Add/Update the hitsmm recommender.
#### MovieAvg
1. Add a recommender (with a different/unique name) with method ```courseavg```.
2. Configure as before but with count parameter set to ```10```.
3. Add/Update the recommender.
#### Popular
1. Add a recommender for the ```popular``` method.
2. Configure the interface and Add/Update the recommender.
#### Actual (Dummy Recommender)
1. Add a recommender with method ```actual``` following steps as before.

### Configuring Metrics
#### Recommended Movie was rated 5.
1. Configure a metric with method ```passed```.
2. In the interface config, select all the recommenders in ```rec_col``` for this metric.
3. Set the item rating column and set threshold to ```5```.
4. Add/Update the metric.
#### Recommended Movie match a watched movie (in term 1 (rating) > term 0 (historical)).
1. Configure a metric with method ```match_recommended``` as above.
2. Add/Update the metric.

### Configuring Comparers.
#### Sum (Recommended Movie Rated 5) and Sum (Recommended was watched in term 1).
1. Add a comparer for each metric using method ```count```.
2. In the interface config choose the respective metric and set ```compare_to``` to actual.
3. Then, in the optional tab of the interface config set length to 10.
4. (Without the optional override,
each recommender would compute the metric for the up to top x items where x is the length of the compare to column.
By setting the length, each recommender compares it top ten (which is the first 10 for actual).)
5. Make sure to add/update each comparer.

### Save the Configuration
1. Select the ```Save``` tab.
2. Select ```Save As```.
3. Navigate to the ```Experiments/Demo/``` folder and use the filename ```movie.csv```.
4. Press the ```Save to File``` button.
5. Close the window to return to the main menu.

## Creating a Driving Config
1. Select ```Generate Experiment(s) Config (INI)```.
2. Browse and open the previously saved ```movie.cfg``` and press ```Get```.
3. Select ```Submit/Continue```
4. Set repeat experiment to ```2``` to run the experiment with two different train/test sets.
5. Save the driving config to ```Experiments/Demo/movie.ini```.
6. Close the window to return to the main menu.

## Running the Experiment
1. Select ```Run Experiment(s)```.
2. Select the ```movie.ini``` file and uncheck ```Load/Continue Experiment```.
3. Press the ```Run``` button.
4. (May take some time, framework is fairly slow)

## Summarizing the Experiment
1. On the main menu, select ```Experiment(s) Summary```.
2. Select ```Generate Summary (SUM) Config```.
3. Load the ```movie.ini``` file.
4. Set the name of the summary using ```Summary Name```.
5. For expression, use the mapped variables to create an expression consisting of the sum of the recommended movies 
with 5 star ratings divided by the sum of the matched recommended movies. If the movies with 5 stars are given variable a, then
set the expression to ```++a/++b```.
6. Save the summary to a .sum file.
7. Change the name of the summary and then change the expression to ```++b```.
8. Save this summary to a different .sum file.
9. The first summary computes the proportion of recommended movies that were 5 stars, and the second computes the 
number of recommended movies that were actually rated so that we can compare.

## Run the Summary
1. On the main menu, select ```Experiment(s) Summary```.
2. Then, select ```Run Summary (SUM)```.
3. Load and run the sum files.

## Viewing the Summary
1. On the main menu, select ```Experiment(s) Summary```.
2. Then, select ```Summary Table``` and load the summary.
3. After viewing, close the window.
4. Select ```Summary Plot``` and load the summary.
5. Use matplotlib color codes and markers to change the look.
6. Press the ```Plot``` button.
