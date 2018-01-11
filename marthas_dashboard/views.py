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

    # Make figure
    hover = HoverTool(
        tooltips=[('date', '$x'), ('y', '$y')],
        formatters={'date': 'datetime'},
        mode='vline',
    )
    tools = ['pan', 'box_zoom', 'wheel_zoom', 'save', 'reset', 'lasso_select', hover]

    fig = figure(plot_width=600, plot_height=600, x_axis_type="datetime", tools=tools)
    fig.line(data['pointtimestamp'], data['pointvalue'], color="navy", alpha=0.5)
    fig.toolbar.logo = None

    # Embed figure in template
    script, div = components(fig)
    html = render_template(
        'menu_chart.html',
        plot_script=script,
        plot_div=div,
        building_name=building_names[building],
        point_name=pt_names[point],
        start_date=start_date,
        end_date=end_date,
    )
    return encode_utf8(html)
