from marthas_dashboard import app
from flask import (request, redirect, url_for, render_template)
from bokeh.embed import components
from bokeh.util.string import encode_utf8
from bokeh.plotting import figure
from bokeh.models import HoverTool
from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    LinearColorMapper,
    AdaptiveTicker,
    PrintfTickFormatter,
    ColorBar
)
from bokeh.palettes import Greys
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

    # do our searches and get the coponents we need to inject there
    search_results = do_searches(searches)
    keywords['graphtype'] = 'compare'
    results_components = get_results_components(searches, search_results, keywords)

    # get our json for all rooms and points
    # so that we can change the values of the select fields based on other values
    rooms_points = get_rooms_points(building_names)
    json = rooms_points_json(rooms_points)

    html = render_template(
        'chart.html',
        buildings = building_names,
        scripts = json,
        result_components = results_components,
        allow_comparisons = True
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

    # do our searches and get the coponents we need to inject there
    search_results = do_searches(searches)
    keywords['graphtype'] = 'compare'
    keywords['alerts'] = True

    results_components = get_results_components(searches, search_results, keywords)
    # get our json for all rooms and points
    # so that we can change the values of the select fields based on other values
    rooms_points = get_rooms_points(building_names)
    json = rooms_points_json(rooms_points)

    html = render_template(
        'alerts.html',
        buildings = building_names,
        scripts = json,
        result_components = results_components,
        allow_comparisons = True
    )
    return encode_utf8(html)

@app.route('/room_comparison')
def room_comparison():

    building_names = api.buildings()  # Call API to get buildings for selector
    times = generate_15_min_timestamps()  # Call helper function in room_comparison.py

    searches = request.args
    # request.args returns back a immutable multi-dictionary. We want to get these values
    # back in order to be able to show them as the "selected" values.
    mutable_searches = {}
    for key, value in searches.items():
        mutable_searches[key] = value

    searches = mutable_searches

    # Just set some defaults if we didn't have any searches (I.e. this is the first loading)
    if len(searches) < 1:
        searches['building'] = '4'
        searches['date'] = '2017-08-18'
        searches['timestamp'] = '00:00:00'

    # do our searches and get the dataframe back
    search_results = get_room_comparison_results(searches)

    # Currently we are going to limit the size of the dataframe until we decide
    # how to handle the number of points. TODO: Decide how to display points
    truncated_search_results = search_results.head()

    result_components = searches # Save the values for the selectors
    result_components['dataframe'] = truncated_search_results

    html = render_template(
        'building_comparison.html',
        buildings=building_names,
        result_components=result_components,
        timestamps=times
    )
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
    json = rooms_points_json(rooms_points)

    html = render_template(
        'chart.html',
        buildings = building_names,
        scripts = json,
        result_components = results_components,
        allow_comparisons = False
    )
    return encode_utf8(html)

def generate_figure(data, keywords):
    if keywords['graphtype'] == 'heatmap':
        return generate_heatmap(data, keywords)
    return generate_line_graph(data, keywords)

def generate_heatmap(data, keywords):
    colors = {}
    colors['red-blue'] = list(reversed(['#f11712', '#e91b19', '#e21f20', '#da2327', '#d3272f', '#cb2b36', '#c42f3d', '#bc3344', '#b5384b', '#ad3c52', '#a6405a', '#9e4461', '#974868', '#8f4c6f', '#885076', '#80547d', '#795885', '#715c8c', '#696093', '#62649a', '#5a68a1', '#536ca8', '#4b70af', '#4474b7', '#3c79be', '#357dc5', '#2d81cc', '#2685d3', '#1e89da', '#178de2', '#0f91e9', '#0099f7']))
    colors['warm'] = ['#ffffff', '#fdfdfd', '#fbfbfb', '#f9f9f9', '#f7f6f6', '#f6f4f4', '#f4f2f2', '#f2f0ef', '#f1eded', '#efebea', '#eee9e8', '#ede6e5', '#ebe4e2', '#eae2df', '#e9dfdc', '#e8ddd9', '#e7dbd6', '#e6d8d3', '#e5d6d0', '#e4d4cd', '#e3d2ca', '#e3d0c6', '#e2cec3', '#e1ccbf', '#e1cabc', '#e0c8b8', '#e0c7b5', '#e0c5b1', '#e0c4ad', '#dfc2a9', '#dfc1a5', '#dfc0a1', '#dfbf9d', '#dfbe99', '#dfbd95', '#e0bd91', '#e0bc8d', '#e0bc88', '#e0bc84', '#e1bc7f', '#e1bc7b', '#e2bc76', '#e3bd71', '#e3be6d', '#e4bf68', '#e5c063', '#e6c15e', '#e7c359', '#e8c554', '#e9c74f', '#eac949', '#ebcc44', '#edce3f', '#eed13a', '#efd534', '#f1d82f', '#f2dc29', '#f4e023', '#f6e51e', '#f7e918', '#f9ee12', '#fbf30c', '#fdf906', '#ffff00', '#fffb00', '#fff700', '#fff300', '#ffef00', '#ffeb00', '#ffe700', '#ffe300', '#ffdf00', '#ffdb00', '#ffd700', '#ffd200', '#ffce00', '#ffca00', '#ffc600', '#ffc200', '#ffbe00', '#ffba00', '#ffb600', '#ffb200', '#ffae00', '#ffaa00', '#ffa600', '#ffa200', '#ff9e00', '#ff9a00', '#ff9600', '#ff9200', '#ff8e00', '#ff8a00', '#ff8600', '#ff8200', '#ff7d00', '#ff7900', '#ff7500', '#ff7100', '#ff6d00', '#ff6900', '#ff6500', '#ff6100', '#ff5d00', '#ff5900', '#ff5500', '#ff5100', '#ff4d00', '#ff4900', '#ff4500', '#ff4100', '#ff3d00', '#ff3900', '#ff3500', '#ff3100', '#ff2d00', '#ff2800', '#ff2400', '#ff2000', '#ff1c00', '#ff1800', '#ff1400', '#ff1000', '#ff0c00', '#ff0800', '#ff0400', '#ff0000', '#f90202', '#f30404', '#ed0606', '#e70808', '#e10909', '#dc0b0b', '#d60d0d', '#d00e0e', '#cb1010', '#c51111', '#c01212', '#bb1414', '#b61515', '#b01616', '#ab1717', '#a61818', '#a11919', '#9c1a1a', '#971b1b', '#921c1c', '#8e1c1c', '#891d1d', '#841e1e', '#801e1e', '#7b1f1f', '#771f1f', '#721f1f', '#6e1f1f', '#6a2020', '#662020', '#622020', '#5e2020', '#5a2020', '#562020', '#521f1f', '#4e1f1f', '#4a1f1f', '#471f1f', '#431e1e', '#401e1e', '#3c1d1d', '#391c1c', '#351c1c', '#321b1b', '#2f1a1a', '#2c1919', '#291818', '#261717', '#231616', '#201515', '#1d1414', '#1a1212', '#171111', '#151010', '#120e0e', '#100d0d', '#0d0b0b', '#0b0909', '#090808', '#060606', '#040404', '#020202', '#000000']
    colors['grey'] = Greys[256]
    colorkey = 'red-blue'

    if 'color' in keywords:
        if keywords['color'] in colors:
            colorkey = keywords['color']
    mapper = LinearColorMapper(palette=colors[colorkey], low=data['pointvalue'].min(), high=data['pointvalue'].max())
    if data['pointvalue'].min() == data['pointvalue'].max():
        mapper = LinearColorMapper(palette=colors[colorkey], low=data['pointvalue'].min() - 1, high=data['pointvalue'].max() + 1)


    source = ColumnDataSource(data)
    TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"
    p = figure(title=data['pointname'][0],
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
         ('pointvalue', '@pointvalue '+data['units'][0]),
    ]
    color_bar = ColorBar(color_mapper=mapper,
                     ticker=AdaptiveTicker(),
                     formatter=PrintfTickFormatter(format="%d "+data['units'][0]),
                     label_standoff=15, location=(0, 0))
    p.add_layout(color_bar, 'right')
    script, plot = components(p)
    color_picker = "Colors: <select class='color-picker' name='color'>"
    for color in colors:
        selected = ''
        if colorkey == color:
            selected = 'selected'
        color_picker +="<option value='"+color+"' "+selected+">"+color.title()+"</option>"
    color_picker+="</select>"
    plot = color_picker+plot
    return script, plot
    # Embed figure in template

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
    return components(fig)
    # Embed figure in template

def create_search_bins(args):
    search_bins = {}
    other_args = {}
    # each arg is formatted as formnum_attribute
    # where the form number is 0 for original, 1 for first comparison, etc.
    # and the attribute is something like start_date, end_date
    # ex 1_start_date is a valid arg
    # first step is to bin all the attributes for a form together
    for key, value in args.items(): 
        search_number = key.split('_')[0]
        attribute_name = key.replace(search_number+"_", "", 1)
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


# from all of our data
# generates plots, scripts and everything that we actually need to inject into the page
def get_results_components(searches, search_results, keywords):
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


# maps building ids to their points and rooms
# ie {4:{'rooms':{5}}}
def get_rooms_points(buildings):
    result = {}
    for building_id, name in buildings.items():
        building_data = {
            'rooms':map_rooms(api.building_rooms(building_id)),
            'points':map_points(api.building_points(building_id))
        }
        result[building_id] = building_data
    return result

# Simple mapping function to take a pandas df returned from building_points
# and turn it into something easier to use on the frontend
def map_points(points):
    results = {}
    for index, row in points.iterrows():
        results[row['id']] = row['name']+'- '+row['description']
    return results

# similar to the map_points function but for rooms
def map_rooms(rooms):
    results = {}
    for index, row in rooms.iterrows():
        results[row['id']] = row['name'].replace("_", " ")
    return results

def rooms_points_json(rooms_points):
    return '<script type="text/javascript">var rooms_points ='+json.dumps(rooms_points)+';</script>'
