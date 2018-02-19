"""
Room_compare/ room_inspection tool(s).

"Room compare" :    refers to the tabular view of a the rooms in a building at a given time
"Room inspector" :  refers to the 24 hour plot(s) generated by clicking on a specific room.
"""

from datetime import (datetime, timedelta)
import pandas as pd
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.layouts import row

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
    """Activated after clicking a cell in room_compare table.
    Returns df ready for plotting (datetime and tags are columns)"""

    # From url args (searches): get "ts" (date + timestamp); building_id; room_name
    ts = datetime.strptime(' '.join([searches['date'], searches['timestamp']]), TIME_FMT)
    building_id = searches['building']
    room_name = searches['room']

    # Compute "start" (12 hours earlier) and "stop" (12 hours later) than timestamp
    start = (ts - timedelta(hours=12)).strftime(TIME_FMT)
    end = (ts + timedelta(hours=12)).strftime(TIME_FMT)

    # Make api calls (maybe this should be a single SQL call)
    points = api.building_points(building_id)
    rooms = api.building_rooms(building_id)
    vals = api.building_values_in_range(building_id, start, end)

    # Filter out all but selected room
    rooms = rooms.query('name == "{}"'.format(room_name))

    # Merge dfs together, attempt to tag points
    df = merge_tables(points, rooms, vals)
    df = hacky_tagging(df)

    # Add datetime column
    df['datetime'] = pd.to_datetime(df.date + ' ' + df.time)

    # Ignore points tagged as 'none'
    df = df.query('tag != "none"')

    # Remove points with 'none' tag,
    # Pivot so tags b/c columns, datetime is index
    return (df.query('tag != "none"')
            .pivot(index='datetime', columns='tag', values='pointvalue')
            .reset_index().rename_axis(None, axis=1))


def make_all_room_inspector_graphs(df):
    """Creates Bokeh plots for room inspector, once table cell clicked"""

    # tags is list of column names, excluding datetime
    tags = list(df.set_index('datetime').columns)

    # Make a plot for each tag
    plots = [make_room_inspector_graph(df, tag) for tag in tags]

    # Put plots in a "row" layout
    return components(row(plots))


def make_room_inspector_graph(df, tag):
    """Creates Bokeh plots for room inspector, once table cell clicked"""
    p = figure(plot_width=300, plot_height=300, x_axis_type='datetime')
    p.line(df['datetime'], df[tag], line_width=2)
    p.xaxis.axis_label = "time"
    p.yaxis.axis_label = tag
    p.toolbar.logo = None
    return p


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
    """Takes three dfs generated by api queries and merges together."""
    df = pd.merge(points, rooms, left_on='roomid', right_on='id', suffixes=('_point', '_room'))
    df = pd.merge(df, vals, left_on='id_point', right_on='pointid', )
    return df


def pivot_table_around_tags(df, idx):
    """Pivot table so tags become columns"""

    # Get values where tag is not 'none'
    df = df.query('tag != "none"')

    # call pivot_on_tag with each
    tags = ['valve', 'temp1 (RM)', 'temp2 (RMT)']
    frames = [pivot_on_tag(df, t) for t in tags]
    final_df = pd.concat(frames, axis=1).reset_index()
    return final_df


def pivot_on_tag(df, tag):
    """Helper function to 'pivot_table_around_tags'

    :param df: tagged df (with all rooms, points, and vals for given building/timestamp)
    :param tag: tag to extact (eg, "valve")
    :return: filtered/pivoted df: <index = name_room, columns = [pointid_{tag}, {tag}]>
    """
    return (df.query('tag == "{}"'.format(tag))
            .pivot_table(index=['name_room', 'pointid'], columns='tag', values='pointvalue')
            .reset_index().rename_axis(None, axis=1)
            .rename({'pointid': 'pointid_{}'.format(tag)}, axis='columns')
            .set_index('name_room'))