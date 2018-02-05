from marthas_dashboard import app
from flask import (request, redirect, url_for, render_template)
from bokeh.embed import components
from bokeh.util.string import encode_utf8
from bokeh.plotting import figure
# from bokeh.models import HoverTool
from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    LinearColorMapper,
    AdaptiveTicker,
    PrintfTickFormatter,
    ColorBar
)
from .api import API
from .alerts import generate_alerts
import json

from .colors import heatmap_colors

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
        buildings=building_names,
        scripts=json,
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
        buildings=building_names,
        scripts=json,
        result_components=results_components,
        allow_comparisons=True
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
        buildings=building_names,
        scripts=json,
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
        mapper = LinearColorMapper(palette=colors[colorkey], low=data['pointvalue'].min() - 1, high=data['pointvalue'].max() + 1)


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
    """Simple mapping function to take a pandas df returned from building_points
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


def rooms_points_json(rooms_points):
    return '<script type="text/javascript">var rooms_points =' + json.dumps(rooms_points) + ';</script>'
