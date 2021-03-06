'''
This is (probably) the association rules we will be using!!
'''

from marthas_dashboard.api import *
from orangecontrib.associate.fpgrowth import *
from orangecontrib.associate import frequent_itemsets, association_rules
from Orange.data import Domain, Table, DiscreteVariable, ContinuousVariable
from Orange.preprocess import Discretize, discretize
import sys

# Where I got how to do this
# https://github.com/biolab/orange3-associate/blob/master/orangecontrib/associate/fpgrowth.py

def getDFBuildingValuesInRange(building_id, start_date_time, stop_date_time):
    '''
    Grab df from api, made so that we can potentially more easily swap api calls with this analysis
    :param building_id:
    :param start_date_time:
    :param stop_date_time:
    :return: dataframe of proper format
    '''
    api = API()

    # THIS IS TOO MUCH DATA FOR OUR API, WE NEED TO DISCUSS THIS, 2 DAYS BREAKS IT???
    # data = api.building_values_in_range('4', '2016-08-18', '2017-08-19')
    df = api.building_values_in_range(building_id, start_date_time, stop_date_time)

    df_pivot = (df
              .groupby(['pointtimestamp', 'pointname'])['pointvalue']
              .sum().unstack().reset_index().fillna(0)
              .set_index('pointtimestamp'))

    #TODO rework?? rn doing this simple thing to try to get around size issues
    # --> without this removal, it takes >2 hrs (not exactly sure havent run the whole thing)
    known_point_names = []
    for column in df_pivot:
        point_name = ''.join([i for i in column if not i.isdigit()])
        # if "HU" in point_name:
        #     df_pivot.drop([column], axis=1, inplace=True)
        if point_name not in known_point_names:
            known_point_names.append(point_name)
        else:
            df_pivot.drop([column], axis=1, inplace=True)

    return df_pivot

def df2table(df):
    '''
    Given a dataframe, makes an Orange.Table
    https://stackoverflow.com/questions/26320638/converting-pandas-dataframe-to-orange-table
    :param df:
    :return: Orange.Table
    '''
    domain_list = []
    for col in df:
        domain_list.append(ContinuousVariable(col))

    domain = Domain(domain_list)
    table = Table(domain, [list(map(str, row)) for row in df.as_matrix()])
    return table

def formatTable(tble):
    '''
    Bins the data, one hot encodes the data
    :param tble:
    :return: data: tble with binned data,
             X: representation of data with one-hot-encoding,
             mapping: representations of what our one-hot-encoding is
    '''
    # Discretization (binning)
    # https://docs.orange.biolab.si/3/data-mining-library/reference/preprocess.html
    print("Discretizing data")
    disc = Discretize()
    disc.method = discretize.EqualWidth(n=4)
    data = disc(tble)
    # print("Discretized table:\n{}\n\n".format(data))

    print("One hot encoding data")
    X, mapping = OneHot.encode(data, include_class=True)
    sorted(mapping.items())

    return data, X, mapping

def getClassItems(data_table, mapping):
    '''
    This is 'The transaction-coded items corresponding to class values'
    :param data_table: binned datavalues in Orange.Table
    :param mapping: one hot encoding mapping
    :return: class_items: transaction encoded items corresponding to class values (points)
    '''
    class_items = {item
                   for item, var, _ in OneHot.decode(mapping, data_table, mapping)
                   if var in data_table.domain.variables}

    sorted(class_items)
    # print("Class items:\n", class_items)

    return class_items

def pretty_print_freq_itemsets(itemsets, mapping, data_table, class_items):
    print("CLASS ITEMS", class_items)
    print("Data table", data_table.domain.variables)

    for item in itemsets:
        print(item)

        # print(', '.join(names[i] for i in ante), '-->',
        #       names[next(iter(cons))],
        #       '(supp: {}, conf: {})'.format(supp, conf, ))


def getAssociationRules(itemsets, class_items):
    '''
    Get the rules!
    :param itemsets: frequent itemsets as constructed from our datatable that we used for class_items
    :param class_items: As returned from getClassItems
    :return: rules! these are weirdly formatted, let pretty print do its thing to see what it is
    '''
    rules = [(P, Q, supp, conf)
             for P, Q, supp, conf in association_rules(itemsets, .8)
             if len(Q) == 1 and Q & class_items]

    print("Length of rules is: ", len(rules))

    # print("Rules are:\n{}\n\n".format(rules))

    return rules

def pretty_print_rules(data_table, mapping, rules):
    '''
    Prints the rules! in a way that we can understand!
    :return: None
    '''
    names = {item: '{}={}'.format(var.name, val)
        for item, var, val in OneHot.decode(mapping, data_table, mapping)}

    api = API()
    for i in range(len(names)):
        pi = api.point_info(names[i].split('=')[0])
        names[i] = names[i] + " ({})".format(pi.description[0])

    # print("Names is:\n{}\n".format(names))
    print("READABLE RULES\n")
    for ante, cons, supp, conf in rules:
        print(', '.join(names[i] for i in ante), '-->',
        names[next(iter(cons))],
        '(supp: {}, conf: {}, lift: )\n'.format(supp, conf))

def write_rules(data_table, mapping, rules, filename):
    '''
    Prints the rules! in a way that we can understand!
    :return: None
    '''
    print("Writing rules to", filename)
    with open(filename, 'w') as f:
        names = {item: '{}={}'.format(var.name, val)
            for item, var, val in OneHot.decode(mapping, data_table, mapping)}

        api = API()
        for i in range(len(names)):
            pi = api.point_info(names[i].split('=')[0])
            names[i] = names[i] + " ({})".format(pi.description[0])

        f.write("READABLE RULES\n")
        for ante, cons, supp, conf in rules:
            s = "{} {} {} {}\n".format(', '.join(names[i] for i in ante), '-->',
            names[next(iter(cons))],
            '(supp: {}, conf: {})'.format(supp, conf))

            f.write(s)

def main():
    df = getDFBuildingValuesInRange('4', '2017-08-18 12:00', '2017-08-18 20:00')
    orange_table = df2table(df)
    data_table, X, mapping = formatTable(orange_table)
    class_items = getClassItems(data_table, mapping)

    itemsets = dict(frequent_itemsets(X, .4))
    # pretty_print_freq_itemsets(itemsets, mapping, data_table, class_items)
    print("Length of frequent itemsets:", len(itemsets))
    rules = getAssociationRules(itemsets, class_items)

    # pretty_print_rules(data_table, mapping, rules)

    # if len(sys.argv) > 1:
    #     write_rules(data_table, mapping, rules, sys.argv[1])
    write_rules(data_table, mapping, rules, "rules.txt")
    # Can get lift through this,,,
    rules_stats(rules, itemsets, n_examples=len(class_items))

main()