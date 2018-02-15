from marthas_dashboard import app
import pandas as pd
from flask import (request, redirect, url_for, render_template)
from bokeh.embed import components
from bokeh.util.string import encode_utf8
from bokeh.plotting import figure
from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    LinearColorMapper,
    AdaptiveTicker,
    PrintfTickFormatter,
    ColorBar
)
from .colors import heatmap_colors
from .api import API
from .alerts import generate_alerts
from .room_comparison import generate_15_min_timestamps
import json
from datetime import datetime

api = API()


@app.route('/')
def index():
    return redirect(url_for('compare'))


@app.route('/compare')
def compare():
    building_names = api.buildings()

    searches, keywords = create_search_bins(request.args)
    # Keywords are all the get params that aren't part of the comparison form
    # eg color map
    # basically just use them to pass around data to the portion of this that generates the actual graphs

    if len(searches) < 1:
        searches[0] = {}
        # Just set some defaults if we didn't have any searches
        searches[0]['building'] = '4'
        searches[0]['point'] = '511'
        searches[0]['from'] = '2017-08-18'
        searches[0]['to'] = '2017-08-30'

    # do our searches and get the components we need to inject there
    search_results = do_searches(searches)
    keywords['graphtype'] = 'compare'
    results_components = get_results_components(searches, search_results, keywords)

    # get our json for all rooms and points
    # so that we can change the values of the select fields based on other values
    rooms_points = get_rooms_points(building_names)
    json_res = rooms_points_json(rooms_points)

    html = render_template(
        'chart.html',
        buildings=building_names,
        scripts=json_res,
        result_components=results_components,
        allow_comparisons=True
    )
    return encode_utf8(html)


@app.route('/alerts')
def alerts():
    building_names = api.buildings()

    searches, keywords = create_search_bins(request.args)

    if len(searches) < 1:
        searches[0] = {}
        # Just set some defaults if we didn't have any searches
        searches[0]['building'] = '4'
        searches[0]['point'] = '511'
        searches[0]['from'] = '2017-08-18'
        searches[0]['to'] = '2017-08-30'

    # do our searches and get the components we need to inject there
    search_results = do_searches(searches)
    keywords['graphtype'] = 'compare'
    keywords['alerts'] = True

    results_components = get_results_components(searches, search_results, keywords)

    # get our json for all rooms and points
    # so that we can change the values of the select fields based on other values
    rooms_points = get_rooms_points(building_names)
    json_res = rooms_points_json(rooms_points)

    html = render_template(
        'alerts.html',
        buildings=building_names,
        scripts=json_res,
        result_components=results_components,
        allow_comparisons=True
    )
    return encode_utf8(html)


@app.route('/room_comparison')
def room_comparison():
    building_names = api.buildings()
    times = generate_15_min_timestamps()  # Call helper function in room_comparison.py

    searches = request.args
    # request.args returns back a immutable multi-dictionary. We want to get these values
    # back in order to be able to show them as the "selected" values so we convert it to a
    # dictionary we can edit.

    mutable_searches = {}
    for key, value in searches.items():
        mutable_searches[key] = value

    searches = mutable_searches
    # print(searches)

    # Just set some defaults if we didn't have any searches (I.e. this is the first loading)
    if len(searches) < 1:
        searches['building'] = '4'
        searches['date'] = '2017-08-18'
        searches['timestamp'] = '00:00:00'

    # do our searches and get the dataframe back
    search_results = get_room_comparison_results(searches)
    print(search_results)

    # Call a helper function to add the room names and descriptions to the search results data frame.
    # Only call the function if we actually got data for that query.
    if search_results.shape != (0, 0):
        search_results = get_room_names_from_point_names(searches, search_results)
        search_results = get_description_from_point_names(searches, search_results)

    print(search_results)

    # Currently we are going to limit the size of the dataframe until we decide
    # how to handle the number of points. TODO: Decide how to display points
    truncated_search_results = search_results.head()

    result_components = searches  # Save and pass back the values for the html form.
    result_components['dataframe'] = truncated_search_results

    html = render_template(
        'room_comparison.html',
        buildings=building_names,
        result_components=result_components,
        timestamps=times
    )
    return encode_utf8(html)


@app.route('/room-inspector')
def room_inspector():
    searches = request.args
    print(searches)
    html = render_template("base.html")
    return encode_utf8(html)


@app.route('/heatmap')
def heatmap():
    building_names = api.buildings()

    searches, keywords = create_search_bins(request.args)
    if len(searches) < 1:
        searches[0] = {}
        # Just set some defaults if we didn't have any searches
        searches[0]['building'] = '4'
        searches[0]['point'] = '511'
        searches[0]['from'] = '2017-08-18'
        searches[0]['to'] = '2017-08-30'
    searches = [searches[0]]

    # do our searches and get the coponents we need to inject there
    search_results = do_searches(searches)
    keywords['graphtype'] = 'heatmap'
    results_components = get_results_components(searches, search_results, keywords)

    # get our json for all rooms and points
    # so that we can change the values of the select fields based on other values
    rooms_points = get_rooms_points(building_names)
    json_res = rooms_points_json(rooms_points)

    html = render_template(
        'chart.html',
        buildings=building_names,
        scripts=json_res,
        result_components=results_components,
        allow_comparisons=False
    )
    return encode_utf8(html)


def generate_figure(data, keywords):
    if keywords['graphtype'] == 'heatmap':
        return generate_heatmap(data, keywords)
    return generate_line_graph(data, keywords)


def generate_heatmap(data, keywords):
    colors = heatmap_colors
    colorkey = 'red-blue'

    if 'color' in keywords:
        if keywords['color'] in colors:
            colorkey = keywords['color']
    mapper = LinearColorMapper(palette=colors[colorkey], low=data['pointvalue'].min(), high=data['pointvalue'].max())
    if data['pointvalue'].min() == data['pointvalue'].max():
        mapper = LinearColorMapper(palette=colors[colorkey], low=data['pointvalue'].min() - 1,
                                   high=data['pointvalue'].max() + 1)

    source = ColumnDataSource(data)
    TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"
    p = figure(
        title=data['pointname'][0],
        y_range=list(reversed(data['date'].unique())), x_range=list(data['time'].unique()),
        x_axis_location="above", plot_width=1000, plot_height=700,
        tools=TOOLS, toolbar_location='below')
    p.grid.grid_line_color = None
    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    p.axis.major_label_text_font_size = "5pt"
    p.axis.major_label_standoff = 0
    p.xaxis.major_label_orientation = 3.14 / 3
    p.xgrid.grid_line_color = None

    p.rect(x="time", y="date", width=1, height=.95,
           source=data,
           fill_color={'field': 'pointvalue', 'transform': mapper},
           line_color=None)

    p.select_one(HoverTool).tooltips = [
        ('date', '@date @time'),
        ('pointvalue', '@pointvalue ' + data['units'][0]),
    ]

    color_bar = ColorBar(color_mapper=mapper,
                         ticker=AdaptiveTicker(),
                         formatter=PrintfTickFormatter(format="%d " + data['units'][0]),
                         label_standoff=15, location=(0, 0))
    p.add_layout(color_bar, 'right')
    script, plot = components(p)
    color_picker = "Colors: <select class='color-picker' name='color'>"
    for color in colors:
        selected = ''
        if colorkey == color:
            selected = 'selected'
        color_picker += "<option value='" + color + "' " + selected + ">" + color.title() + "</option>"
    color_picker += "</select>"
    plot = color_picker + plot
    return script, plot  # Embed figure in template


def generate_line_graph(data, keywords):
    x = data['pointtimestamp']
    y = data['pointvalue']

    # Make figure
    hover = HoverTool(
        tooltips=[('date', '$x'), ('y', '$y')],
        formatters={'date': 'datetime'},
        mode='vline',
    )
    tools = ['pan', 'box_zoom', 'wheel_zoom', 'save', 'reset', 'lasso_select', hover]

    fig = figure(plot_width=600, plot_height=600, x_axis_type="datetime", tools=tools)
    fig.line(x, y, color="navy", alpha=0.5)
    fig.toolbar.logo = None
    return components(fig)  # Embed figure in template


def create_search_bins(args):
    """Takes requests.args dictionary as argument"""
    search_bins = {}
    other_args = {}
    # each arg is formatted as formnum_attribute
    # where the form number is 0 for original, 1 for first comparison, etc.
    # and the attribute is something like start_date, end_date
    # ex 1_start_date is a valid arg
    # first step is to bin all the attributes for a form together
    for key, value in args.items():
        search_number = key.split('_')[0]
        attribute_name = key.replace(search_number + "_", "", 1)
        try:
            search_number = int(search_number)
            if search_number not in search_bins:
                search_bins[search_number] = {}
            search_bins[search_number][attribute_name] = value
        except ValueError as e:
            other_args[key] = value
    return search_bins, other_args


def do_searches(search_bins):
    results = []
    # traverse in order so that the comparison and original don't flip screen position
    for i in range(len(search_bins)):
        search = search_bins[i]
        # in the future we'll want to be able to figure out the type of query that we want to do
        # based on their restrictions
        # for now just assume everything is a point values search
        data = api.point_values(search['point'], search['from'], search['to'])
        results.append(data)
    return results


def get_room_comparison_results(keywords):
    """ Function that does the api lookup for the room-comparison page.
        Calls the api.building_values_at_time after using python's datetime to fix the timestamp"""

    building_id, date, timestamp = keywords["building"], keywords["date"], keywords["timestamp"]
    full_timestamp = datetime.strptime((date + " " + timestamp), "%Y-%m-%d %H:%M:%S")

    data = api.building_values_at_time(building_id, full_timestamp)
    return data


def get_results_components(searches, search_results, keywords):
    """from all of our data, generates plots, scripts
    and everything that we actually need to inject into the page"""

    parts = []

    # each search result has a plot, script, and form params
    # we want to create a list of dictionaries
    # where each item in the outer list is a search result
    # and each in the inner dictionary is a component of that search result, 
    # ie el['plot'] stores the html code for the graph
    for i in range(len(search_results)):
        result = search_results[i]
        # as a default we want all the restrictions that the user specified
        # already have these in our searches, so just copy them over
        result_components = searches[i]
        # we also want all of the buildings points so that we can select the correct one
        result_components['point_names'] = map_points(api.building_points(result_components['building']))

        if len(result) <= 1:
            # no data associated with search, makes it easy
            result_components['plot'] = 'No data for that search'
            result_components['script'] = ''
        else:
            result_components['script'], result_components['plot'] = generate_figure(result, keywords)
            if 'alerts' in keywords:
                result_components['alerts'] = generate_alerts(result, keywords)
        parts.append(result_components)
    return parts


def get_room_names_from_point_names(searches, search_results):
    """ A helper function that takes in the data frame from the api.building_values_at_time
        query and then calls the api.building_rooms and api.building_points queries to
        then map points from the building_values_at_time query to the room ids in building_points
        followed by the room name in room_points.

        Input:
            searches: The search keywords as a dictionary
            search_results: A dataframe returned from an api.building_values call
        Output: The same dataframe with a new column called "roomname" added
        """

    # We get the building rooms in order to be able to display the correct NAME of a room for a point.
    building_rooms = api.building_rooms(searches["building"])

    # We get the building points to be able to get the room ID for a given point name.
    building_points = api.building_points(searches["building"])

    # Now we want to get the room id for each point in our search results
    room_ids = []
    for index, row in search_results.iterrows():
        # First find the row in building_points that has a matching point name
        row_in_building_points = building_points.loc[building_points["name"] == row["pointname"]]
        target_room_id = row_in_building_points["roomid"].tolist()
        room_ids.append(target_room_id[0])

    # Now that we have the room ids, we can look up the value in building_rooms.
    room_names = []
    for id in room_ids:
        row_in_building_rooms = building_rooms.loc[building_rooms["id"] == id]
        target_room_name = row_in_building_rooms["name"].tolist()
        room_names.append(target_room_name[0])

    # Finally, add the column to the results dataframe specifying the room name.
    search_results = search_results.assign(roomname=room_names)

    return search_results


def get_description_from_point_names(searches, search_results):
    """ A helper function similar to the above function. Maps point names to descriptions
        and then appends a new column to the search results table that is the description
        of the point.
        Input:
            searches: The search keywords as a dictionary
            search_results: A dataframe containing the search_results so far
        Output: The same dataframe with a new column called "description" added
    """

    # We get the building points to be able to get the room ID for a given point name.
    building_points = api.building_points(searches["building"])

    # Now we want to get the room id for each point in our search results
    descriptions = []
    for index, row in search_results.iterrows():
        # First find the row in building_points that has a matching point name
        row_in_building_points = building_points.loc[building_points["name"] == row["pointname"]]
        target_room_id = row_in_building_points["description"].tolist()
        descriptions.append(target_room_id[0])

    # Finally, add the column to the results dataframe specifying the description.
    search_results = search_results.assign(description=descriptions)

    return search_results


# maps building ids to their points and rooms
# ie {4:{'rooms':{5}}}
def get_rooms_points(buildings):
    """maps building ids to their points and rooms,
    ie {4:{'rooms':{5}}}"""
    result = {}
    for building_id, name in buildings.items():
        building_data = {
            'rooms': map_rooms(api.building_rooms(building_id)),
            'points': map_points(api.building_points(building_id))
        }
        result[building_id] = building_data
    return result


def map_points(points):
    """Take a pandas df returned from building_points
    and turn it into something easier to use on the frontend
    """
    results = {}
    for index, row in points.iterrows():
        results[row['id']] = row['name'] + '- ' + row['description']
    return results


def map_rooms(rooms):
    """Similar to the map_points function but for rooms"""
    results = {}
    for index, row in rooms.iterrows():
        results[row['id']] = row['name'].replace("_", " ")
    return results


def room_inspector_df():
    bld = api.building('Hulings').id
    timestamp = '2017-08-18 00:45:00'

    # Load some data
    rooms = api.building_rooms(bld)
    points = api.building_points(bld)
    vals = api.building_values_at_time(bld, timestamp)

    # Remove room 6, the scary dummy room
    rooms = rooms[rooms['id'] != 6]

    # Merge df together
    df = pd.merge(points, rooms, left_on='roomid', right_on='id', suffixes=('_point', '_room'))
    df = pd.merge(df, vals, left_on='id_point', right_on='pointid', )

    # Attempt to tag points

    df['tag'] = 'none'

    # Tag 'valve' based on description
    df_valve = df[df['description'].str.find('VALVE') > 0]
    df.loc[df_valve.index, 'tag'] = 'valve'

    # Tag 'temp' based on point name
    df_temp = df[df['name_point'].str.find('.RM') > 0]
    df.loc[df_temp.index, 'tag'] = 'temp1 (RM)'

    df_temp = df[df['name_point'].str.find('.RMT') > 0]
    df.loc[df_temp.index, 'tag'] = 'temp2 (RMT)'

    # View DF where tag is not "none
    view_df = df.query('tag != "none"')

    # Pivot
    view_df = (view_df.pivot(index='name_room', columns='tag',
                             values='pointvalue')
               .reset_index().rename_axis(None, axis=1))

    return view_df.to_html(index=False)


def rooms_points_json(rooms_points):
    return '<script type="text/javascript">var rooms_points =' + json.dumps(rooms_points) + ';</script>'
