from marthas_dashboard import app
from flask import (request, redirect, url_for, render_template)
from bokeh.embed import components
from bokeh.util.string import encode_utf8
from bokeh.plotting import figure
from bokeh.models import HoverTool
from .api import API

api = API()


@app.route('/')
def index():
    return redirect(url_for('search'))


@app.route('/search')
def search():
    building_names = {'2': 'Libe'}
    pt_names = {
        "511": "LAB HOT H2O TEMP",
        "512": "A1 CCL TEMP",
        "513": "AH2 AIR VOLU",
        "514": "STATIC SET",
    }

    searches = create_search_bins(request.args)

    if len(searches) < 1:
        searches[0] = {}
        # Just set some defaults if we didn't have any searches
        searches[0]['building'] = '2'
        searches[0]['point'] = '511'
        searches[0]['from'] = '2016-08-18'
        searches[0]['to'] = '2017-08-19'

    search_results = do_searches(searches)
    components = get_components(searches, search_results)

    html = render_template(
        'chart.html',
        components = components,
        hide_comparison = (len(searches) < 2)
    )
    return encode_utf8(html)

def generate_figure(x, y):
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
    return fig
    # Embed figure in template


def create_search_bins(args):
    search_bins = {}
    # each arg is formatted as formnum_attribute
    # where the form number is 0 for original, 1 for first comparison, etc.
    # and the attribute is something like start_date, end_date
    # ex 1_start_date is a valid arg
    # first step is to bin all the attributes for a form together
    for key, value in args.items(): 
        search_number = key.split('_')[0]
        attribute_name = key.replace(search_number+"_", "", 1)
        search_number = int(search_number)
        if search_number not in search_bins:
            search_bins[search_number] = {}
        search_bins[search_number][attribute_name] = value
    return search_bins

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

# from all of our data
# generates plots, scripts and everything that we actually need to inject into the page
def get_components(searches, search_results):
    search_results = do_searches(searches)
    parts = []
    for i in range(len(search_results)):
        result = search_results[i]
        result_components = searches[i]
        if len(result) <= 1:
            result_components['plot'] = 'No data for that search'
            result_components['script'] = ''
        else:
            fig = generate_figure(result['pointtimestamp'], result['pointvalue'])
            result_components['script'], result_components['plot'] = components(fig)
        parts.append(result_components)
    return parts


