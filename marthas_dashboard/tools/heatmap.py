from bokeh.embed import components
from bokeh.models import LinearColorMapper, ColumnDataSource, HoverTool, ColorBar, AdaptiveTicker, PrintfTickFormatter
from bokeh.plotting import figure

from marthas_dashboard.colors import heatmap_colors


def generate_heatmap(data, keywords):
    colors = heatmap_colors
    colorkey = 'red-blue'
    data = data.sort_values(by='pointtimestamp')

    if 'color' in keywords:
        if keywords['color'] in colors:
            colorkey = keywords['color']
    mapper = LinearColorMapper(palette=colors[colorkey], low=data['pointvalue'].min(), high=data['pointvalue'].max())

    if data['pointvalue'].min() == data['pointvalue'].max():
        mapper = LinearColorMapper(
            palette=colors[colorkey], low=data['pointvalue'].min() - 1,
            high=data['pointvalue'].max() + 1)

    source = ColumnDataSource(data)
    TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"
    p = figure(
        title=data['pointname'][0],
        y_range=list(reversed(data['date'].unique())), x_range=list(data['time'].unique()),
        x_axis_location="above", plot_width=1000, plot_height=700,
        tools=TOOLS, toolbar_location='below', sizing_mode='scale_width')
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

    color_bar = ColorBar(
        color_mapper=mapper, ticker=AdaptiveTicker(),
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
