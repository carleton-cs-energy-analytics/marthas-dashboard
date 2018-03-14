def generate_alerts(data):
    """Find outliers in given df (point over time)."""

    average = data['pointvalue'].mean()
    std = data['pointvalue'].std()

    # filter df down to values outside 3 SD
    outliers_df = data.query('(pointvalue > {}) or (pointvalue < {})'.format(
        average + std * 3,
        average - std * 3))

    # get columns of interest
    smaller_df = outliers_df[['pointtimestamp', 'pointvalue', 'units']]
    return smaller_df.to_dict(orient='index')
