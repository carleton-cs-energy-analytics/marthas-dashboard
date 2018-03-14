# Analysis Done So Far

## Association Rules-- Orange (current implementation)

[About Orange](https://github.com/biolab/orange3-associate/blob/master/orangecontrib/associate/fpgrowth.py)

In ```Association_Rules_Orange.py``` we have our association rules algorithm, which uses the API to obtain a dataframe of points and pointvalues, converts that into an Orange Table, uses binning and one-hot-encoding in order to prep the data for the algorithms.  We then use Orange to get a frequent itemset which is a list of pointvalues (post binning and encoding) that are often found together.  This frequent itemset is then used to generate our association rules, which are lists of commonly seen occurrences, like if point1 in bin 1 and point2 in bin2 then point3 in bin3.  

### To use this code:

From [marthas-dashboard](https://github.com/carleton-cs-energy-analytics/marthas-dashboard.git):

```bash
pip install Orange3
pip install orange3-associate
python3 -m marthas_dashboard.analysis.Association_Rules_Orange.py
```

To change the points, change the building id or the times given

### To expand this code for other types of our data:

* SHOULD be able to follow along general guideline outlined below (using functions in the specified file)
* Just change the ```getDFBuildingValuesInRange``` to another api calling method of your choice (and be sure to clean/pivot the data)

```python
df = getDFBuildingValuesInRange('4', '2017-08-18 12:00', '2017-08-18 20:00')
orange_table = df2table(df)
data_table, X, mapping = formatTable(orange_table)
class_items = getClassItems(data_table, mapping)

itemsets = dict(frequent_itemsets(X, .4))
rules = getAssociationRules(itemsets, class_items)

pretty_print_rules(data_table, mapping, rules)
```

### Parameters
.....TODO

### Using the Orange3 Widget
This is a much faster way of running association rules.  The only issue is that we will only be able to look at 100 rules at a time, but we can use filtering of both input and output to look at a subset of the rules that might interest us

## Decision Trees

### Python: scikit-learn DecisionTreeClassifier
* must use continuous input features and categorical/discrete classes
* I interchangeably use the terms "classes" and "labels" (seen in code below)

#### Example code:
```python
# create classifier with input parameters
clf_gini = tree.DecisionTreeClassifier(criterion = "gini", random_state = 100,
                               max_depth=3, min_samples_leaf=5)
# train tree on data
clf_gini.fit(features, labels)

# create picture of tree, important parameters are: feature_names, class_names
dot_data = tree.export_graphviz(clf_gini, out_file=None,
                         feature_names=features.columns.values,
                         class_names=class_names,
                         filled=True, rounded=True,
                         special_characters=True)
# graph tree
graph = graphviz.Source(dot_data)

# write graphed tree to file
graph.render("test_tree")
```

#### Input parameters of interest

##### Classification parameters
See [sklearn documentation page](http://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html#sklearn.tree.DecisionTreeClassifier)
* **criterion:** way of choosing branching nodes. gini or entropy
* **random_state:** seed for RNG
* **max_depth, min_samples_leaf, etc:** the min/max parameters are mostly used to decide when to stop branching the tree or speed up tree creation (at the cost of accuracy)

##### Graphing parameters
* **feature_names:** list of column names of the dataframe of feature variables (in our case, point names)
* **class_names:** ordered list of possible classifications. Such as ["(92-94]","(94-97]","(97-100]"] if the classification is a binned continuous value. Could also be ["low","medium","high"]. Has to match the number of unique values in the list of labels, but not the values themselves. So you could have the classification values fall into the bins (92-94],(94-97], and (97-100], then use the class_names=["low","medium","high"]. Just make sure they are ordered so that they line up alphabetically/numerically ascending.

### R: rpart

Didn't end up using this method because it was slow, but kept code and documentation around because it allows both continuous and categorical input data.

* make sure method="class" parameter is included in rpart call to create classification tree rather than regression tree
* impossibly slow with continuous data - must bin everything
* can include categorical data (enumerated data in our DB)
* must specify by name which columns are used as features (might be some way around this, I didn't pursue)

#### Example code:

```r
# classify the "EV.RMG07.V" col of the "binned_data" dataframe based on the values of the "EV.RMG06.V" col
test_tree = rpart(binned_data$EV.RMG07.V ~ binned_data$EV.RMG06.V, method = "class", data=binned_data)
```
