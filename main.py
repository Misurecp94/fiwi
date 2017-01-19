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
import pandas as pd
import sqlite3 as sql
import os

from bokeh.plotting import figure
from bokeh.layouts import layout, widgetbox, row, column

from bokeh.models import ColumnDataSource, HoverTool, Div
from bokeh.models.widgets import PreText, Slider, Select, TextInput
from bokeh.io import curdoc
from bokeh.sampledata.movies_data import movie_path


try:
    from functools import lru_cache
except ImportError:
    # Python 2 does stdlib does not have lru_cache so let's just
    # create a dummy decorator to avoid crashing
    print ("WARNING: Cache is available on Python 3 only.")

    def lru_cache():
        def dec(f):
            def _(*args, **kws):
                return f(*args, **kws)
            return _
        return dec


DATA_DIR = join(dirname(__file__), 'daily')

DEFAULT_TICKERS = ['AAPL', 'GOOG', 'INTC', 'BRCM', 'YHOO']

# (not in x) gibt eine liste zurück in der val nicht enthalten ist
def nix(val, lst):
    return [x for x in lst if x != val]


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

# Html Beschreibung
desc = Div(text=open(join(dirname(__file__), "Html/description.html")).read(), width=800)

# Create Input controls Todo: Add Method which automaticaley chooses option based on available csv files??? DONE!
stock_ticker=os.listdir("CSV") # returns list
stock = Select(title="Stock:", value="Google", options=stock_ticker)


days = Slider(title="Number of days to keep the stock", value=100, start=1, end=252, step=1)

# Non used
min_year = Slider(title="Year released", start=1940, end=2014, value=1970, step=1)
director = TextInput(title="Director name contains")
x_axis = Select(title="X Axis", options=sorted(axis_map.keys()), value="Tomato Meter")
y_axis = Select(title="Y Axis", options=sorted(axis_map.keys()), value="Number of days")


# Create Column Data Source that will be used by the plot
source = ColumnDataSource(data=dict(date=[], o=[], h=[], l=[], c=[], volume=[]))

hover = HoverTool(tooltips=[
    ("Title", "@title"),
    ("Year", "@year"),
    ("$", "@revenue")
])

p = figure(plot_height=600, plot_width=700, title="", toolbar_location=None, tools=[hover])
p.circle(x="x", y="y", source=source, size=7, color="color", line_color=None, fill_alpha="alpha")


# HIER: LADE DATEN AUS .CSV
@lru_cache()
def load_ticker(ticker):
    fname = join(DATA_DIR, 'table_%s.csv' % ticker.lower())
    data = pd.read_csv(fname, header=None, parse_dates=['date'],
                       names=['date', 'foo', 'o', 'h', 'l', 'c', 'v'])
    data = data.set_index('date')
    # print(data.c.diff())

    # gibt tabelle auf in format ->     date - ticker(close) - ticker_returns
    return pd.DataFrame({ticker: data.c, ticker+'_returns': data.c.diff()})


@lru_cache()
def get_data(t1):
    df1 = load_ticker(t1)
    data = pd.concat([df1], axis=1)

    data = data.dropna()
    data['t1'] = data[t1]
    data['t1_returns'] = data[t1+'_returns']
    return data

# set up widgets

stats = PreText(text='', width=500)
ticker1 = Select(title='Auswahl der Aktie:', value='AAPL', options=nix('AAPL', DEFAULT_TICKERS))
select_varianzred = Select(title='Methoden zur Varianzreduktion: ', value='Methode 1', options=['Methode 1', 'Methode 2'])

# set up plots

source_static = ColumnDataSource(data=dict(date=[], t1=[], t1_returns=[]))
tools = 'pan,wheel_zoom,xbox_select,reset'


ts1 = figure(plot_width=900, plot_height=200, tools=tools, x_axis_type='datetime', active_drag="xbox_select")
ts1.line('date', 't1', source=source_static)
ts1.circle('date', 't1', size=1, source=source, color=None, selection_color="orange")


# set up callbacks

def ticker1_change(attrname, old, new):
    ticker1.options = nix(new, DEFAULT_TICKERS)
    update()


# wird ausgeführt wenn noch keine auswahl in der selection box getroffen wurde (beim ersten start) - default AAPL
def update(selected=None):
    t1 = ticker1.value

    data = get_data(t1)
    source.data = source.from_df(data[['t1', 't1_returns', ]])
    source_static.data = source.data

    update_stats(data, t1)

    ts1.title.text, ts1


def update_stats(data, t1):
    stats.text = str(data[[t1, t1+'_returns']].describe())

ticker1.on_change('value', ticker1_change)


def selection_change(attrname, old, new):
    t1 = ticker1.value
    data = get_data(t1)
    selected = source.selected['1d']['indices']
    if selected:
        data = data.iloc[selected, :]
    update_stats(data, t1)


def updateDropDown():
    print("geht");

source.on_change('selected', selection_change)

# set up layout
c1 = column(ticker1, select_varianzred)
c2 = column(stats, ts1)
r1 = row(c1, c2)
layout = column(desc, r1)


#layout = column(main_row, series)

update()  # initial load of the data - first load metadata
#updateDropDown()  # initial load of the dropdown - load Stock and calculate results based on metadata

curdoc().add_root(layout)
curdoc().title = "Monte Carlo Simulation"
