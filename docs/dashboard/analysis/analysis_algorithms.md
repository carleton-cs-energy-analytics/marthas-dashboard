# Analysis Algorithms

## Option 1: Association rules

### Input
One data entry is a set of items. In the grocery store analogy, this might be {milk, bread, eggs}.
* Note that this is not the same as having a set number of items (or points in our case) and input their values, such as {1 carton, 2 loaves, 1 dozen}.

Since we have points which can be set to different values, the easiest way for us to create this data structure is:
1. Bin all continuous values
2. Implement one hot encoding so that an "item" is a point at a set value (e.g. "VAV>20" or "AC=ON", not just "VAV" or "ON")

### Output
Statements, or rules, of the form {X,Y,...} implies {Z,...} which suggest correlations between certain items, or in our case, point settings. (e.g. {"AC=ON", "TEMP=COOL"} implies {"ENERGY>2000"}). We do not get to decide which types of point settings go before or after the implies, so we would have to sort through the output for statements that are meaningful to us.  

### Typical algorithm
From what I have seen and Wikipedia says, a typical algorithm will find _frequent itemsets_ within the given data entries based on a minimum _support_ threshold. It will then define interesting rules from those itemsets based on a minimum _confidence_ threshold. Algorithms differ on how they iterate through itemsets and rules to test for confidence and support, since iterating through all subsets of a set can be a lengthy process.

## Option 2: Decision trees

### Input
A list of data entries (timestamps in our case) with features (equipment points in our case). A second list of the same data entries (timestamps) with a label (energy use, maintenance required, etc). Label must be categorical/discrete, which means binning for numerical data. Features can be anything theoretically (see note below), thresholds for splitting continuous data are decided by decision tree algorithm.

* NOTE: Python scikit learn implementation of decision trees requires **continuous numerical data**. Categorical data should use one hot encoding instead of numerical representation to avoid being confused with continuous data.

### Output
A decision tree flowchart with internal nodes representing decision points and leaf nodes representing classification. Internal nodes are labeled with which feature was used to branch at that point, and possibly some measure of accuracy or gained information at that node.

### Typical algorithm
A decision tree is created from training data by choosing branching points in order from the root of the tree down to the leaves. A branching point is decided by iterating over all possible features and splitting on that feature. Some measurement (algorithm dependent, examples are gini and entropy) is used to determine which feature will give the most information or accuracy by splitting the data at that point in the tree. Once some threshold of accuracy or max depth is reached, all remaining data are classified at leaf nodes and the tree is output. Multiple training and test datasets can be created to prevent overfitting the data. Since we have so many features (all of the equipment points) and only really care about what features are used to branch the first few levels, we will likely set a low max depth and not have to worry about overfitting.
