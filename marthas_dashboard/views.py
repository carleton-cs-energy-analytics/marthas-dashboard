from marthas_dashboard import app
import flask
import json
import requests
from bokeh.embed import components
from bokeh.util.string import encode_utf8
from .api import API
from .plotting import (make_bar_chart, make_poly_line)
from bokeh.plotting import figure
import pandas as pd


@app.route('/')
def index():
    return 'Hello World!'


@app.route('/bar')
def bar():
    """
    Simpler example
    Based on: https://github.com/realpython/flask-bokeh-example
    """
    fig = make_bar_chart()

    # render template
    script, div = components(fig)
    html = flask.render_template(
        'chart.html',
        plot_script=script,
        plot_div=div,
    )
    return encode_utf8(html)


def getitem(obj, item, default):
    if item not in obj:
        return default
    else:
        return obj[item]


@app.route('/poly')
def poly():
    """
    Slightly more complex example
    Based on: https://github.com/bokeh/bokeh/tree/master/examples/embed/simple
    """

    # Grab the inputs arguments from the URL
    args = flask.request.args

    # Get all the form arguments in the url with defaults
    color = getitem(args, 'color', 'Black')
    _from = int(getitem(args, '_from', 0))
    to = int(getitem(args, 'to', 10))

    # make plot
    fig = make_poly_line(color, _from, to)

    script, div = components(fig)
    html = flask.render_template(
        'poly.html',
        plot_script=script,
        plot_div=div,
        color=color,
        _from=_from,
        to=to
    )
    return encode_utf8(html)

@app.route('/live')
def live():
    api = API()
    data = api.point_values('511', '2016-08-18', '2017-08-19')
    if(len(data) > 1):
        fig = figure(plot_width=600, plot_height=600, x_axis_type="datetime")
        fig.line(data['pointtimestamp'], data['pointvalue'], color="navy", alpha=0.5)
        script, div = components(fig)
        html = flask.render_template(
            'chart.html',
            plot_script=script,
            plot_div=div,
            color='navy'
        )
        return encode_utf8(html)
    return 'No Data For that Point'