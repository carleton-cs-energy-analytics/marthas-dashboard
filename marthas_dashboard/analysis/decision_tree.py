from ..api import API
from sklearn import tree
import pandas as pd
import graphviz
import csv

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


def string_decision_tree_test():
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


def to_string(list):
    new_list = []
    for item in list:
        new_list.append(str(item))
    return new_list


def evans_decision_tree_test():
    evans_df = pd.read_csv("marthas_dashboard/analysis/only_numeric.csv")
    evans_df = evans_df.select_dtypes("float64")

    # EV.HX2.HWST is label, others are too similar to label
    features = evans_df.drop(["EV.HX2.HWST","EV.HX2.HWSTSP", "EV.HX2.HWRT"], axis=1)

    classification_variable = evans_df.loc[:, evans_df.columns == "EV.HX2.HWST"]
    classification_variable = classification_variable.ix[:,0]
    labels_pd = pd.qcut(classification_variable, 4)
    labels = labels_pd.tolist()
    labels = to_string(labels)
    class_names = set(labels)
    class_names = sorted(list(class_names))

    clf_gini = tree.DecisionTreeClassifier(criterion="gini", random_state=100,
                                           max_depth=3, min_samples_leaf=5)
    clf_gini.fit(features, labels)

    dot_data = tree.export_graphviz(clf_gini, out_file=None,
                                    feature_names=features.columns.values,
                                    class_names=class_names,
                                    filled=True, rounded=True,
                                    special_characters=True)
    graph = graphviz.Source(dot_data)
    graph.render("test_tree_gini_heat")


def drop_non_numeric_columns(df, threshold):
    cols_to_keep = []
    for column in df:
        non_numeric_count = 0.0
        row_count = 0.0
        for row_cell in df.loc[:, column]:
            row_count += 1
            if not is_number(row_cell):
                non_numeric_count += 1
        if non_numeric_count / row_count < threshold:
            cols_to_keep.append(column)
    return df[cols_to_keep]


def drop_non_numeric_rows(df):
    rows_to_drop = set()
    for index, row in df.iterrows():
        for col_cell in row:
            if not is_number(col_cell):
                rows_to_drop.add(index)
    return_df = df.drop(df.index[list(rows_to_drop)])
    return return_df.apply(pd.to_numeric)


def format_labels(labels_series, is_numeric, num_bins = 0):
    if is_numeric:
        labels_series = pd.qcut(labels_series, num_bins)
    labels = labels_series.tolist()
    labels = to_string(labels)
    return labels


def hulings_energy_decision_tree():
    api_wrapper = API()
    siemens_raw_df = api_wrapper.building_values_in_range("4", "2017-08-19 00:00:00", "2017-08-19 23:45:00")
    lucid_raw_df = api_wrapper.building_values_in_range("6", "2017-08-19 00:00:00", "2017-08-19 23:45:00")
    print(lucid_raw_df.columns.values)

    siemens_df = (siemens_raw_df
              .groupby(['pointtimestamp', 'pointname'])['pointvalue']
              .sum().unstack().reset_index()
              .set_index('pointtimestamp'))

    lucid_df = (lucid_raw_df
              .groupby(['pointtimestamp', 'pointname'])['pointvalue']
              .sum().unstack().reset_index()
              .set_index('pointtimestamp'))

    #lucid_label = lucid_df[:,"Hulings Hall - Hulings Hall - Electricity (kWh)"]

    #print(lucid_label)






if __name__ == "__main__":
    hulings_energy_decision_tree()
