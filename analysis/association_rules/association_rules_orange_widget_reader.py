from marthas_dashboard.api import *
import pandas as pd
import numpy as np


def getDFBuildingValuesInRange(building_name_list, start_date_time, stop_date_time):
    '''
    Grab df from api, made so that we can potentially more easily swap api calls with this analysis
    :param building_id:
    :param start_date_time:
    :param stop_date_time:
    :return: dataframe of proper format
    '''

    api = API()

    building_ids = []
    for building in building_name_list:
        building_ids.append(api.building(building).id)


    # THIS IS TOO MUCH DATA FOR OUR API, WE NEED TO DISCUSS THIS, 2 DAYS BREAKS IT???
    # data = api.building_values_in_range('4', '2016-08-18', '2017-08-19')
    # df = api.building_values_in_range(building_id, start_date_time, stop_date_time)
    df_list = []
    for building_id in building_ids:
        df = api.building_values_in_range(building_id, start_date_time, stop_date_time)
        df_list.append(df)

    result = pd.concat(df_list)

    if result.empty:
        print("No data coming through")
        return

    df_pivot = pivot_df(result)

    return df_pivot

def grabAllPointsInBuildingByType(building_id, start, stop, type):
    api = API()
    result = api.building_values_in_range_by_type(building_id, start, stop, type)
    df = pivot_df(result)

    return df

def removeColumnsWherePtValueAlwaysTheSame(df):
    cols = df.select_dtypes([np.number]).columns
    diff = df[cols].diff().sum()
    df.drop(diff[diff == 0].index, axis=1)

    return df

def pivot_df(df):
    df_pivot = (df
                .groupby(['pointtimestamp', 'pointname'])['pointvalue']
                .sum().unstack().reset_index().fillna(0)
                .set_index('pointtimestamp'))

    return df_pivot

def parseHTML(filename):
    with open(filename, "r") as f:
        lines = f.readlines()

    for line in lines:
        if '<tbody>' in line:
            found_line = line
            print(found_line)

    lines = found_line.split("tr>")

    new_lines = []
    for line in lines:
        if 'style' in line:
            new_lines.append(line)

    newnew_lines = []
    for line in new_lines:
        newnew_lines.append(line.split('>'))

    thereal = []
    for line in newnew_lines:
        thelittlereal = []
        for l in line:
            if '</td' in l or '</th' in l:
                thelittlereal.append(l[:-4])
        thereal.append(thelittlereal)

    for line in thereal:
        print(line)

    df = pd.DataFrame(thereal[1:], columns=thereal[0])

    print(df.head())

    api = API()
    df['Antecedent_PointDescription'] = (0 for i in range(len(df['Antecedent'])))
    for i in range(len(df['Antecedent'])):
        point_list = df['Antecedent'][i].split(",")
        pt_descs = []
        for point in point_list:
            pt_desc = api.point_info(point.split('=')[0])
            if not pt_desc.empty:
                pt_descs.append(pt_desc.description[0])
        df['Antecedent_PointDescription'][i] = pt_descs

    df['Consequent_PointDescription'] = (0 for i in range(len(df['Consequent'])))
    for i in range(len(df['Consequent'])):
        point_list = df['Consequent'][i].split(",")
        pt_descs = []
        for point in point_list:
            pt_desc = api.point_info(point.split('=')[0])
            if not pt_desc.empty:
                pt_descs.append(pt_desc.description[0])
        df['Consequent_PointDescription'][i] = pt_descs

    print(df.head())
    return df

def main():
    buildings = ['Hulings', 'Hulings Hall']
    df = getDFBuildingValuesInRange(buildings, '2017-08-18 08:00', '2017-08-18 15:00')
    df = removeColumnsWherePtValueAlwaysTheSame(df)
    df.to_csv("orange_widget_pointvalues/orange_widget_AR_{}.csv".format("_".join(buildings)), index = False)
    print("Saved csv to orange_widget_pointvalues/orange_widget_AR_{}.csv".format("_".join(buildings)))

    # df = grabAllPointsInBuildingByType('4', '2017-08-18 12:00', '2017-08-18 20:00', 13)
    # df.to_csv("orange_widget_AR_temp_type_hulings.csv")

    # df = parseHTML("ar_hulings_hall_water.html")
    # print(df.head())

if __name__ == '__main__':
    main()



