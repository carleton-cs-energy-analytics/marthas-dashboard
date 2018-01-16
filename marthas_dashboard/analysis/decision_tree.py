from ..api import API
from sklearn import tree
import pandas as pd
import graphviz

# just testing some things out to get the setup
api_wrapper = API()
pd_table_values = api_wrapper.building_points("1")
#print(pd_table_values.head)
dummy_table = pd.get_dummies(pd_table_values)

dummy_table = dummy_table.to_dense()

features = dummy_table.loc[: ,dummy_table.columns != "pointtypeid"]
labels = dummy_table.loc[: ,dummy_table.columns == "pointtypeid"]

clf_gini = tree.DecisionTreeClassifier(criterion = "gini", random_state = 100,
                               max_depth=3, min_samples_leaf=5)
clf_gini.fit(features, labels)

dot_data = tree.export_graphviz(clf_gini, out_file=None,
                         feature_names=features.columns.values,
                         class_names=labels.unique.values,
                         filled=True, rounded=True,
                         special_characters=True)
graph = graphviz.Source(dot_data)
graph.render("test_tree")