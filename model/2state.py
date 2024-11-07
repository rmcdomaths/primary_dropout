from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider, Div
from bokeh.plotting import figure, curdoc
import numpy as np

# Initialize parameters
k_init = 1
mui_init = 1
L_init = -.5
R_init = 0

# Create sliders
k_slider = Slider(title="k", value=k_init, start=0, end=2, step=0.05)
mui_slider = Slider(title="mui", value=mui_init, start=0, end=2, step=0.01)
L_slider = Slider(title="L", value=L_init, start=-2, end=2, step=0.01)
R_slider = Slider(title="R", value=R_init, start=-2, end=2, step=0.01)

# Initial data source
source = ColumnDataSource(data=dict(x1_red=[], y1_red=[], x1_blue=[], y1_blue=[], 
                                    x2_blue=[], y2_blue=[], x2_red=[], y2_red=[], 
                                    scatter_x=[], scatter_y=[], scatter_green_x=[], scatter_green_y=[]))

# Create plot
plot = figure(title="Interactive Line Segments", x_range=(-2, 2), y_range=(-2.5, -.5))

# Plotting lines and markers
line1_red = plot.line('x1_red', 'y1_red', source=source, color='red', line_width=2)
line1_blue = plot.line('x1_blue', 'y1_blue', source=source, color='blue', line_width=2)
line2_red = plot.line('x2_red', 'y2_red', source=source, color='red', line_width=2)
line2_blue = plot.line('x2_blue', 'y2_blue', source=source, color='blue', line_width=2)

# Points as 'X'
scatter = plot.scatter('scatter_x', 'scatter_y', source=source, size=20, color="black", marker="x", line_width=3)
scatter_green = plot.scatter('scatter_green_x', 'scatter_green_y', source=source, size=20, color="green", marker="x", line_width=3)

# Calculate and display p1 and p2
VL_text = Div(text="VL: ", width=200, height=30)
VR_text = Div(text="VR: ", width=200, height=30)
m1_text = Div(text="m1: ", width=200, height=30)
m2_text = Div(text="m2: ", width=200, height=30)

# Update function
def update_data(attr, old, new):
    k = k_slider.value
    mui = mui_slider.value
    L = L_slider.value
    R = R_slider.value

    # Calculate votes in first district
    m1 = (L + R) / 2

    # Define line segments
    y1_red = [-1, -1]
    y1_blue = [-1, -1]
    # If m1 is in range
    if -mui - 1 < m1 < -mui + 1:
        x1_red = [-mui - 1, m1]
        x1_blue = [m1, -mui + 1]
    elif m1 < -mui - 1:
        x1_red = [-mui - 1, -mui + 1]
        x1_blue = [R, R]
    elif -mui - 1:
        x1_red = [L, L]
        x1_blue = [-mui - 1, -mui + 1]

    # Calculate votes in second district 
    m2 = ((L + R) / 2) - k * ((x1_blue[1] - x1_blue[0]) - (x1_red[1] - x1_red[0]))

    y2_red = [-2, -2]
    y2_blue = [-2, -2]
    # If m2 is in range
    if mui - 1 < m2 < mui + 1:
        x2_red = [mui - 1, m2]
        x2_blue = [m2, mui + 1]
    elif m2 < mui - 1:
        x2_red = [L, L]
        x2_blue = [mui - 1, mui + 1]
    elif mui + 1 < m2:
        x2_red = [mui - 1, mui + 1]
        x2_blue - [R, R]

    # Update data source
    source.data = dict(
        x1_red=x1_red,
        y1_red=y1_red,
        x1_blue=x1_blue,
        y1_blue=y1_blue,
        x2_blue=x2_blue,
        y2_blue=y2_blue,
        x2_red=x2_red,
        y2_red=y2_red,
        scatter_green_x=[m1, m2],
        scatter_green_y=[-1, -2],
        scatter_x=[L, R, m1, L, R, m2],
        scatter_y=[-1, -1, -1, -2, -2, -2]
    )

    # Calculate v and p2
    VL = (x1_red[1] - x1_red[0]) + (x2_red[1] - x2_red[0])
    VR = (x1_blue[1] - x1_blue[0]) + (x2_blue[1] - x2_blue[0])

    # Update text
    VL_text.text = f"VL: {VL:.2f}"
    VR_text.text = f"VR: {VR:.2f}"
    m1_text.text = f"m1: {m1:.2f}"
    m2_text.text = f"m2: {m2:.2f}"

# Set the update function to be called when sliders are changed
for w in [k_slider, mui_slider, L_slider, R_slider]:
    w.on_change('value', update_data)

# Initial call to update the plot
update_data(None, None, None)

# Layout
layout = column(k_slider, mui_slider, L_slider, VL_text, VR_text, R_slider, plot)

curdoc().add_root(layout)
curdoc().title = "Interactive Line Segments"
