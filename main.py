# should ultimately display the GUI and calculate everything where the user can change the following aspects:
# number of days to keep the stock, starting price, anual volatility, number of monteCarlo iterations
# should also draw afterwards a chart (last results of each iteration, iteration over all days = 1 iteration,
# so do it x time
# should also calculate mean, median, standard derivation, and the 5%,25% and 95% percentile of the result
# should also calculate the calc. val at risk and val at risk

# val at risk (VAR) = x% chance y% oder mehr von Portfolio verlieren in einem Tag!
# x% VAL = (1-(1-x))*total Count of Returns bei sortiertem aufliegen (=x% Quantil!!!)
# calc val at risk (CVAL) = in the worst x% of returns the average loss will be y%
# x% CVAL = (1/VAR x%)*sum(from worst return to value of VAR x%)


# In one iteration do for each step:
# Simulated Price of that day = Starting price from the day before * (1+random number from N(0,x)
# Erwartungswert standard = 0 (user könnte ändern!) wegen der Random Walk Theory
# Last day = Result from the first iteration

#  CALCULATE THE ANNUAL VOLATILITY ! ... .CSV STOCK DATA IS ALWAYS FROM 1.1.2016-31.12.2016

# Todo: implement methods to reduce the varianz


from os.path import dirname, join

import numpy as np
import pandas.io.sql as psql
import sqlite3 as sql

from bokeh.plotting import figure
from bokeh.layouts import layout, widgetbox
from bokeh.models import ColumnDataSource, HoverTool, Div
from bokeh.models.widgets import Slider, Select, TextInput
from bokeh.io import curdoc
from bokeh.sampledata.movies_data import movie_path

# WE DONT NEED A DATABASE ANYWAY
conn = sql.connect(movie_path)
query = open(join(dirname(__file__), 'SQL/query.sql')).read()
movies = psql.read_sql(query, conn)

movies["color"] = np.where(movies["Oscars"] > 0, "orange", "grey")
movies["alpha"] = np.where(movies["Oscars"] > 0, 0.9, 0.25)
movies.fillna(0, inplace=True)  # just replace missing values with zero
movies["revenue"] = movies.BoxOffice.apply(lambda x: '{:,d}'.format(int(x)))

with open(join(dirname(__file__), "CSV/razzies-clean.csv")) as f:
    razzies = f.read().splitlines()
movies.loc[movies.imdbID.isin(razzies), "color"] = "purple"
movies.loc[movies.imdbID.isin(razzies), "alpha"] = 0.9

axis_map = {
    "Tomato Meter": "Meter",
    "Numeric Rating": "numericRating",
    "Number of days": "Reviews",
    "Box Office (dollars)": "BoxOffice",
    "Length (minutes)": "Runtime",
    "Year": "Year",
}

desc = Div(text=open(join(dirname(__file__), "Html/description.html")).read(), width=800)

# Create Input controls Todo: Add Method which automaticaley chooses option based on available csv files??? MAYBE!
stock=select = Select(title="Stock:", value="Google", options=["Google", "Apple", "Microsoft"])
days = Slider(title="Number of days to keep the stock", value=100, start=1, end=252, step=1)

# Non used
min_year = Slider(title="Year released", start=1940, end=2014, value=1970, step=1)
max_year = Slider(title="End Year released", start=1940, end=2014, value=2014, step=1)
oscars = Slider(title="Minimum number of Oscar wins", start=0, end=4, value=0, step=1)
boxoffice = Slider(title="Dollars at Box Office (millions)", start=0, end=800, value=0, step=1)
genre = Select(title="Genre", value="All",
               options=open(join(dirname(__file__), 'Txt/genres.txt')).read().split())
director = TextInput(title="Director name contains")
cast = TextInput(title="Cast names contains")
x_axis = Select(title="X Axis", options=sorted(axis_map.keys()), value="Tomato Meter")
y_axis = Select(title="Y Axis", options=sorted(axis_map.keys()), value="Number of days")


# Create Column Data Source that will be used by the plot
source = ColumnDataSource(data=dict(x=[], y=[], color=[], title=[], year=[], revenue=[], alpha=[]))

hover = HoverTool(tooltips=[
    ("Title", "@title"),
    ("Year", "@year"),
    ("$", "@revenue")
])

p = figure(plot_height=600, plot_width=700, title="", toolbar_location=None, tools=[hover])
p.circle(x="x", y="y", source=source, size=7, color="color", line_color=None, fill_alpha="alpha")

# HIER: BERECHNE DATEN
def select_movies():
    genre_val = genre.value
    director_val = director.value.strip()
    cast_val = cast.value.strip()
    selected = movies[
        (movies.Reviews >= days.value) &
        (movies.BoxOffice >= (boxoffice.value * 1e6)) &
        (movies.Year >= min_year.value) &
        (movies.Year <= max_year.value) &
        (movies.Oscars >= oscars.value)
    ]
    if genre_val != "All":
        selected = selected[selected.Genre.str.contains(genre_val)]
    if director_val != "":
        selected = selected[selected.Director.str.contains(director_val)]
    if cast_val != "":
        selected = selected[selected.Cast.str.contains(cast_val)]
    return selected

# HIER: SETZE UPDATES UND RUFE UPDATEDROPDOWN AUF


def update():
    df = select_movies()
    x_name = axis_map[x_axis.value]
    y_name = axis_map[y_axis.value]

    p.xaxis.axis_label = x_axis.value
    p.yaxis.axis_label = y_axis.value
    p.title.text = "%d movies selected" % len(df)
    source.data = dict(
        x=df[x_name],
        y=df[y_name],
        color=df["color"],
        title=df["Title"],
        year=df["Year"],
        revenue=df["revenue"],
        alpha=df["alpha"],
    )

# HIER: BERECHNE DATEN


def updateDropDown():
    print("geht")

controls = [days, boxoffice, genre, min_year, max_year, oscars, director, cast, x_axis, y_axis]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())

dropDowns = [stock]
for dropDown in dropDowns:
    dropDown.on_change('value', lambda attr, old, new: updateDropDown())

sizing_mode = 'scale_width'

inputs = widgetbox(*dropDowns, *controls, sizing_mode=sizing_mode)
l = layout([
    [desc],
    [inputs, p],
], sizing_mode=sizing_mode)

update()  # initial load of the data - first load metadata
updateDropDown()  # initial load of the dropdown - load Stock and calculate results based on metadata

curdoc().add_root(l)
curdoc().title = "Monte Carlo Simulation"
