from bokeh.plotting import figure


def make_bar_chart():
    """Create bar chart"""
    fig = figure(plot_width=600, plot_height=600)
    fig.vbar(
        x=[1, 2, 3, 4],
        width=0.5,
        bottom=0,
        top=[1.7, 2.2, 4.6, 3.9],
        color='navy'
    )
    return fig


def make_poly_line(color, _from, to):
    """Create a polynomial line graph with arguments"""

    colors = {
        'Black': '#000000',
        'Red':   '#FF0000',
        'Green': '#00FF00',
        'Blue':  '#0000FF',
    }

    x = list(range(_from, to + 1))
    fig = figure(title="Polynomial")
    fig.line(x, [i ** 2 for i in x], color=colors[color], line_width=2)
    return fig
