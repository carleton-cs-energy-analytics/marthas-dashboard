from marthas_dashboard.api import API
from sklearn import tree
import pandas as pd
import graphviz


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
    """
    Casts all items in the given list into a their string representations
    :param list
    :return: new list with all the same values as strings
    """
    new_list = []
    for item in list:
        new_list.append(str(item))
    return new_list


def is_number(s):
    """
    Checks if input s is a number
    :param s: anything
    :return: Boolean: True if s is a number
    """
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


def drop_non_numeric_columns(df, threshold):
    """
    Removes columns from dataframe that have a ratio of non-numeric entries greater than the input threshold
    :param df: Pandas dataframe
    :param threshold: float [0,1] Minimum fraction of non-numeric entries to keep column
    :return: Pandas dataframe with non-numeric (enumerated or "no data") columns removed
    """
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
    """
    Removes rows from dataframe that have any non-numeric entries
    (run after drop_non_numeric_columns so that not all rows are dropped due to enumerated columns)
    :param df: Pandas dataframe
    :return: Pandas dataframe with "no data" rows removed
    """
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
    # get data from database
    api_wrapper = API()
    siemens_raw_df = api_wrapper.building_values_in_range("4", "2017-08-19 00:00:00", "2017-08-19 23:45:00")
    lucid_raw_df = api_wrapper.building_values_in_range("6", "2017-08-19 00:00:00", "2017-08-19 23:45:00")

    # realign dataframes
    siemens_df = (siemens_raw_df
              .groupby(['pointtimestamp', 'pointname'])['pointvalue']
              .sum().unstack().reset_index()
              .set_index('pointtimestamp'))
    lucid_df = (lucid_raw_df
              .groupby(['pointtimestamp', 'pointname'])['pointvalue']
              .sum().unstack().reset_index()
              .set_index('pointtimestamp'))

    # only need one set of lucid data for labels/classes
    lucid_label = lucid_df["Hulings Hall - Electricity "]

    features_df = siemens_df.join(lucid_label, how="inner")

    # clean up data
    features_df = drop_non_numeric_columns(features_df, 0.8)
    features_df = drop_non_numeric_rows(features_df)

    labels = features_df.pop("Hulings Hall - Electricity ")
    #labels = pd.qcut(labels, 4)
    labels = pd.cut(labels, [0,35,50])

    labels_list = labels.tolist()
    labels_list = to_string(labels_list)

    class_names = set(labels_list)
    class_names = sorted(list(class_names))

    clf_gini = tree.DecisionTreeClassifier(criterion="entropy", random_state=100,
                                           max_depth=3, min_samples_leaf=5)
    clf_gini.fit(features_df, labels_list)

    dot_data = tree.export_graphviz(clf_gini, out_file=None,
                                    feature_names=features_df.columns.values,
                                    class_names=class_names,
                                    filled=True, rounded=True,
                                    special_characters=True)
    graph = graphviz.Source(dot_data)
    graph.render("test_tree_hulings_entropy_35cutoff")







if __name__ == "__main__":
    hulings_energy_decision_tree()
