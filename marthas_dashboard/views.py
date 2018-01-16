from marthas_dashboard import app
from flask import (request, redirect, url_for, render_template)
from bokeh.embed import components
from bokeh.util.string import encode_utf8
from bokeh.plotting import figure
from bokeh.models import HoverTool
from .api import API

api = API()


@app.route('/test3')
def index():
    return redirect(url_for('live'))


@app.route('/live')
def live():
    building_names = {'2': 'Libe'}
    pt_names = {
        "511": "LAB HOT H2O TEMP",
        "512": "A1 CCL TEMP",
        "513": "AH2 AIR VOLU",
        "514": "STATIC SET",
    }

    # Get arguments from URL, if any
    args = request.args
    building = args.get('building', default='2')
    point = args.get('point', default='511')
    start_date = args.get('_from', default='2016-08-18')
    end_date = args.get('to', default='2017-08-19')

    data = api.point_values(point, start_date, end_date)

    if len(data) <= 1:
        # Todo: Implement flask "flash" here
        # See: http://flask.pocoo.org/docs/0.12/patterns/flashing/
        return "No data for that point"

    fig = generate_figure(data['pointtimestamp'], data['pointvalue'])
    script, div = components(fig)
    html = render_template(
        'chart.html',
        plot_script=[script, script],
        plot_div=[div, div],
        building_names=[building_names[building], building_names[building]],
        point_names=[pt_names[point],pt_names[point]],
        start_dates=[start_date, start_date],
        end_dates=[end_date,end_date],
    )
    return encode_utf8(html)

@app.route('/comparison')
def comparison():
    building_names = {'2': 'Libe'}
    pt_names = {
        "511": "LAB HOT H2O TEMP",
        "512": "A1 CCL TEMP",
        "513": "AH2 AIR VOLU",
        "514": "STATIC SET",
    }

    # Get arguments from URL, if any
    args = request.args
    building = args.get('building', default='2')
    point = args.get('point', default='511')
    start_date = args.get('_from', default='2016-08-18')
    end_date = args.get('to', default='2017-08-19')
    c_building = args.get('c_building', default='2')
    c_point = args.get('c_point', default='511')
    c_start_date = args.get('c_from', default='2016-08-18')
    c_end_date = args.get('c_to', default='2017-08-19')

    data = api.point_values(point, start_date, end_date)
    c_data = api.point_values(c_point, c_start_date, c_end_date)


    if len(data) <= 1 and len(c_data) <= 1:
        # Todo: Implement flask "flash" here
        # See: http://flask.pocoo.org/docs/0.12/patterns/flashing/
        return "No data for those points"

    fig = generate_figure(data['pointtimestamp'], data['pointvalue'])
    c_fig = generate_figure(c_data['pointtimestamp'], c_data['pointvalue'])

    script, div = components(fig)
    c_script, c_div = components(c_fig)

    graph_building_names = [building_names[building], building_names[c_building]]
    graph_point_names = [pt_names[point], pt_names[c_point]]
    graph_starts = [start_date, c_start_date]
    graph_ends = [end_date, c_end_date]


    html = render_template(
        'chart.html',
        plot_scripts=[script, c_script],
        plot_divs=[div,c_div],
        building_names=graph_building_names,
        point_names=graph_point_names,
        start_dates=graph_starts,
        end_dates=graph_ends,
        comparison_hidden=False,
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
