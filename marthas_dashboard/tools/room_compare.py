from datetime import (datetime, timedelta)
import pandas as pd
from bokeh.embed import components
from bokeh.plotting import figure

from marthas_dashboard.api import API

api = API()


TIME_FMT = "%Y-%m-%d %H:%M:%S"


def get_room_comparison_results(keywords):
    """Use arguments to build df for displaying"""

    # Process arguments
    building_id, date, timestamp = keywords["building"], keywords["date"], keywords["timestamp"]
    full_timestamp = datetime.strptime((date + " " + timestamp), TIME_FMT)

    # Make api calls (maybe this should be a single SQL call)
    rooms = api.building_rooms(building_id)
    points = api.building_points(building_id)
    vals = api.building_values_at_time(building_id, full_timestamp)

    # Remove dummy rooms
    rooms = rooms[rooms['name'].str.find('_Dummy_') < 0]

    # Merge dfs together, attempt to tag points, pivot so tags become columns
    df = merge_tables(points, rooms, vals)
    df = hacky_tagging(df)
    df = pivot_table_around_tags(df, 'name_room')

    return df


def get_room_inspector_results(searches):
    """Returns df of tabular room data for room comparison"""

    # Process arguments
    time_string = ' '.join([searches['date'], searches['timestamp']])  # get date info
    ts = datetime.strptime(time_string, TIME_FMT)
    start = (ts - timedelta(hours=12)).strftime(TIME_FMT)
    end = (ts + timedelta(hours=12)).strftime(TIME_FMT)
    building_id = searches['building']

    # Make api calls (maybe this should be a single SQL call)
    points = api.building_points(building_id)
    rooms = api.building_rooms(building_id)
    vals = api.building_values_in_range(building_id, start, end)

    # Just focus on selected room
    rooms = rooms[rooms['name'] == searches['room']]

    # Merge dfs together, attempt to tag points
    df = merge_tables(points, rooms, vals)
    df = hacky_tagging(df)

    # Add datetime column
    df['datetime'] = pd.to_datetime(df.date + ' ' + df.time)

    # Pivot so tags become columns
    df = pivot_table_around_tags(df, 'datetime')

    return df


def make_room_inspector_graph(view_df):
    """Creates Bokeh plots for room inspector, once table cell clicked"""
    plot = figure(plot_width=400, plot_height=400, x_axis_type='datetime')
    plot.line(view_df['datetime'], view_df['valve'], line_width=2)
    return components(plot)


def hacky_tagging(df):
    """Attempt to tag points in DF: To be replaced with Zephyr's tags"""
    df['tag'] = 'none'  # add tag column (set to 'none' by default)
    df_valve = df[df['description'].str.find('VALVE') > 0]  # tag 'valve'
    df.loc[df_valve.index, 'tag'] = 'valve'
    df_temp = df[df['name_point'].str.find('.RM') > 0]  # tag 'temp1'
    df.loc[df_temp.index, 'tag'] = 'temp1 (RM)'
    df_temp = df[df['name_point'].str.find('.RMT') > 0]  # tag 'temp2'
    df.loc[df_temp.index, 'tag'] = 'temp2 (RMT)'
    return df


def merge_tables(points, rooms, vals):
    """Takes three DataFrames generated by api queries and merges together.
    Perhaps this should be done on SQL side, ideally"""
    df = pd.merge(points, rooms, left_on='roomid', right_on='id', suffixes=('_point', '_room'))
    df = pd.merge(df, vals, left_on='id_point', right_on='pointid', )
    return df


def pivot_table_around_tags(df, idx):
    """Pivot table so tags become columns"""

    # Get values where tag is not 'none'
    df = df.query('tag != "none"')

    # Pivot and return
    return (df.pivot(index=idx, columns='tag', values='pointvalue')
            .reset_index().rename_axis(None, axis=1))

