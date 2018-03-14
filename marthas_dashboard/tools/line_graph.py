from bokeh.embed import components
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.plotting import figure


def generate_line_graph(data, plot_width=500, plot_height=500):
    """Generate Bokeh line plot from given dataframe"""

    source = ColumnDataSource(data)

    plot_title = "{} ({}) [from: {} to: {}]".format(
        data.loc[0, 'pointname'],
        data.loc[0, 'units'],
        data.date.min(),
        data.date.max())

    hover = HoverTool(
        tooltips=[('Date', '@pointtimestamp{%F %T}'), ('Value', '$y')],
        formatters={'pointtimestamp': 'datetime'},
        mode='vline')

    plot_tools = ['pan', 'box_zoom', 'wheel_zoom', 'save', 'reset', 'lasso_select', hover]

    fig = figure(
        plot_width=plot_width, plot_height=plot_height,
        x_axis_type="datetime", title=plot_title,
        tools=plot_tools)
    fig.line(x='pointtimestamp', y='pointvalue', source=source, color="navy", line_width=2, alpha=0.5)
    fig.toolbar.logo = None
    return components(fig)  # Embed figure in template
