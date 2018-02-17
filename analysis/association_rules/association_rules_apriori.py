'''
We will likely not use this ---> It takes too long!
Keeping it for now because might want to reference some of the binning,
one-hot encoding, or general dataframe handling it contains.
'''

from marthas_dashboard.api import *
import sys
import pandas as pd
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules

def runAR(filename):
    with open(filename, 'w') as f:

        api = API()

        # THIS IS TOO MUCH DATA FOR OUR API, WE NEED TO DISCUSS THIS, 2 DAYS BREAKS IT???
        # data = api.building_values_in_range('4', '2016-08-18', '2017-08-19')


        data = api.building_values_in_range('4', '2017-08-18 12:00', '2017-08-18 20:00')

        data.head()
        f.write("{} is data shape from API\n".format(data.shape))

        basket = (data
                  .groupby(['pointtimestamp', 'pointname'])['pointvalue']
                  .sum().unstack().reset_index().fillna(0)
                  .set_index('pointtimestamp'))

        f.write("Basket is:\n{}\n\n".format(basket))

        f.write("Remove HU points for easier access")
        for column in basket:
            if "HU" in column:
                basket.drop([column], axis = 1, inplace = True)

        # Bin the data's point values into 100 different bins (all of equal size)
        for column in basket:
            basket[column] = pd.cut(basket[column], 50)
        f.write("Binning data into 50 bins for each point")
        f.write("{}\n\n".format(basket))

        f.write("One-Hot Encoding\n")
        result = pd.get_dummies(basket)
        f.write("Result head is {}\n\n".format(result.head()))

        f.write("Make dataframe sparse\n")
        result = result.to_sparse(fill_value=0)

        f.write("Generating frequent itemsets\n")
        # Frequent items
        frq_itemsets = apriori(result, min_support=0.8, use_colnames=True)
        #frq_itemsets = frequent_itemsets(result, min_support=0.2)
        f.write("Frequent itemsets:\n{}\n\n".format(frq_itemsets))

        # Generate association rules
        f.write("Generating Association Rules\n")
        f.flush()
        rules = association_rules(frq_itemsets, metric="lift")
        f.write("Rules:\n{}\n\n".format(rules))

def main():
    filename = sys.argv[1]
    print("Output to", filename)
    runAR(filename)
    print("DONE!")

main()