from marthas_dashboard.api import *
from orangecontrib.associate.fpgrowth import *
from orangecontrib.associate import frequent_itemsets, association_rules
from Orange.data import Domain, Table, DiscreteVariable, ContinuousVariable
from Orange.preprocess import Discretize, discretize


# https://github.com/biolab/orange3-associate/blob/master/orangecontrib/associate/fpgrowth.py

def AR():
    api = API()

    # THIS IS TOO MUCH DATA FOR OUR API, WE NEED TO DISCUSS THIS, 2 DAYS BREAKS IT???
    # data = api.building_values_in_range('4', '2016-08-18', '2017-08-19')
    data = api.building_values_in_range('4', '2017-08-18 12:00', '2017-08-18 20:00')


    basket = (data
              .groupby(['pointtimestamp', 'pointname'])['pointvalue']
              .sum().unstack().reset_index().fillna(0)
              .set_index('pointtimestamp'))
    basket.head()

    # for column in basket:
    #     if "HU" in column:
    #         basket.drop([column], axis = 1, inplace = True)
    # basket.head()

    # # Bin the data's point values into 100 different bins (all of equal size)
    # for column in basket:
    #     basket[column] = pd.cut(basket[column], 50)
    # basket.head()
    #
    # result = pd.get_dummies(basket)
    # result.head()
    #
    # result = result.to_sparse(fill_value=0)


    # Example from orange
    tab = df2table(basket)
    print("Table \n{}\n\n".format(tab))

    # Discretization
    # https://docs.orange.biolab.si/3/data-mining-library/reference/preprocess.html
    disc = Discretize()
    disc.method = discretize.EqualWidth(n=4)
    data = disc(tab)

    X, mapping = OneHot.encode(data, include_class=True)
    sorted(mapping.items())

    itemsets = dict(frequent_itemsets(X, .4))
    print("Length itemsets:",len(itemsets))

    print("data.domain", data.domain)

    class_items = {item
        for item, var, _ in OneHot.decode(mapping, data, mapping)
        if var in list(data.domain)}

    print("Sorted Class items:\n", sorted(class_items))

    # print("Data domain class_var values:\n", data.domain.class_var.values)

    rules = [(P, Q, supp, conf)
        for P, Q, supp, conf in association_rules(itemsets, .8)
        if len(Q) == 1 and Q & class_items]

    print("Length of rules is: ",len(rules))

    print("Rules are:\n{}\n\n".format(rules))

    names = {item: '{}={}'.format(var.name, val)
        for item, var, val in OneHot.decode(mapping, data, mapping)}
    print("Names is:\n{}\n\n".format(names))


    print("READABLE RULES??? \n\n")
    for ante, cons, supp, conf in rules:
        print(', '.join(names[i] for i in ante), '-->',
        names[next(iter(cons))],
        '(supp: {}, conf: {})'.format(supp, conf))


def df2table(df):
    # https://stackoverflow.com/questions/26320638/converting-pandas-dataframe-to-orange-table
    domain_list = []
    for col in df:
        domain_list.append(ContinuousVariable(col))

    domain = Domain(domain_list)
    table = Table(domain, [list(map(str, row)) for row in df.as_matrix()])
    return table

AR()