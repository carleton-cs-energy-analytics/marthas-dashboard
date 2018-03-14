from marthas_dashboard import app
from flask import (request, redirect, url_for, render_template, jsonify)
from werkzeug.contrib.cache import SimpleCache
from bokeh.util.string import encode_utf8
from . import tools
from .api import API

api = API()
cache = SimpleCache()


@app.route('/')
def index():
    return redirect(url_for('compare'))


@app.route('/compare')
def compare():
    selector_data = get_selector_data()  # generate/retrieve data for selector menu
    default_data = {'building': '6', 'point': '305', 'from': '2017-08-18', 'to': '2017-08-30'}
    html = render_template('point_compare.html', selector_data=selector_data, data=default_data)
    return encode_utf8(html)


@app.route('/alerts')
def alerts():
    selector_data = get_selector_data()  # generate/retrieve data for selector menu
    default_data = {'building': '6', 'point': '305', 'from': '2017-08-18', 'to': '2017-08-30'}
    html = render_template('alerts.html', selector_data=selector_data, data=default_data)
    return encode_utf8(html)


@app.route('/heatmap')
def heatmap():
    selector_data = get_selector_data()  # generate/retrieve data for selector menu
    default_data = {'building': '6', 'point': '305', 'from': '2017-08-18', 'to': '2017-08-30'}
    html = render_template('heatmap.html', selector_data=selector_data, data=default_data)
    return encode_utf8(html)


@app.route('/_make_compare_plot/', methods=['GET', 'POST'])
def make_compare_plot():
    """Creates a line plot for point compare page."""

    search = request.args
    data = api.point_values(search['point'], search['from'], search['to'])

    if len(data) == 0:
        return jsonify(script=None, plot="Sorry, no data!", table=None)

    if search['tool'] == 'compare':
        script, plot = tools.generate_line_graph(data)
        return jsonify(script=script, plot=plot, table=None)

    if search['tool'] == 'alerts':
        script, plot = tools.generate_line_graph(data)
        table = tools.generate_alerts(data)
        return jsonify(script=script, plot=plot, table=table)

    if search['tool'] == 'heatmap':
        script, plot = tools.generate_heatmap(data, keywords=[])
        return jsonify(script=script, plot=plot, table=None)

    print("Error with plot generation.")


@app.route('/room_comparison')
def room_comparison():
    selector_data = get_selector_data()  # generate/retrieve data for selector menu
    times = tools.generate_15_min_timestamps()  # Call helper function in room_comparison.py

    default_data = {
        'building': api.building('Evans Hall').id,
        'date': '2017-12-26',
        'timestamp': '00:00:00'}

    html = render_template(
        'room_compare.html', selector_data=selector_data,
        data=default_data, timestamps=times)

    return encode_utf8(html)


@app.route('/_make_room_compare_table/', methods=['GET', 'POST'])
def make_room_compare_table():
    search = request.args
    print(search)
    try:
        df = tools.get_room_comparison_results(search)
        if search.get('detect-anomalies'):
            df = tools.get_anomalous_points(df, search)  # adds anomaly columns
        else:
            df['room_temp_anomalous'] = False  # add anomaly columns set to false
            df['valve_anomalous'] = False
        table = df.to_json(orient='index')
        return table
    except ValueError:
        return jsonify(None)


@app.route('/_make_room_compare_plots/', methods=['GET', 'POST'])
def make_room_compare_plots():
    searches = request.args
    search_results = tools.get_room_inspector_results(searches)
    script, div = tools.make_all_room_inspector_graphs(search_results)
    return jsonify(script=script, plot=div)


def get_selector_data(timeout_mins=10):
    """Get data about building/point names to populate menus.
    Makes use of caching to store this info for a while."""
    selector_dict = cache.get('selector_data')
    if selector_dict is None:
        selector_dict = create_selector_data_dict()
        cache.set('selector_data', selector_dict, timeout=timeout_mins * 60)
    return selector_dict


def create_selector_data_dict():
    """Called by get_selector_data.
    Uses api to build dict of building, room, and id data for menus."""
    data_dict = {}
    buildings_dict = api.buildings()
    for building_id, building_name in buildings_dict.items():
        points_df = api.building_points(building_id)
        points_dict = points_df.set_index('id').to_dict(orient='index')
        rooms_df = api.building_rooms(building_id)
        rooms_dict = rooms_df.set_index('id').to_dict(orient='index')
        data_dict[building_id] = {
            'name': building_name,
            'points': points_dict,
            'rooms': rooms_dict}
    return data_dict
