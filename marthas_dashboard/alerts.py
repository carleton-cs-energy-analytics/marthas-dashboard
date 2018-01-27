import pandas as pd
def generate_alerts(data, keywords):
    # keywords in this context will be things like logging level
    # eg if keywords['warnings'] is false then we only want to display high priority alerts
    average = data['pointvalue'].mean()
    std = data['pointvalue'].std()
    outliers = []
    for index, row in data.iterrows():
        if row['pointvalue'] > average + std*3 or row['pointvalue'] < average - std*3:
            roundpoints = 2
            formatstring = "{0:.{1}f}"
            # we were getting values like Average: -0.0 just because we were cutting off crucial info for low vals
            # just keep increasing the precision until we display an actual non zero value
            while float(formatstring.format(average, roundpoints)) == float(0):
                roundpoints+=1
            row['avg'] = formatstring.format(average, roundpoints)
            row['std'] = formatstring.format(std, roundpoints)
            row['pointvalue'] = formatstring.format(row['pointvalue'], roundpoints)
            outliers.append(row)

    return outliers

