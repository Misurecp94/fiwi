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

import pandas as pd
import os

from bokeh.plotting import figure
from bokeh.layouts import row, column
from bokeh.charts import Histogram

from bokeh.models import ColumnDataSource, Div
from bokeh.models.widgets import PreText, Slider, Select
from bokeh.io import curdoc

try:
    from functools import lru_cache
except ImportError:
    # Python 2 does stdlib does not have lru_cache so let's just
    # create a dummy decorator to avoid crashing
    print("WARNING: Cache is available on Python 3 only.")

    def lru_cache():
        def dec(f):
            def _(*args, **kws):
                return f(*args, **kws)
            return _
        return dec


DATA_DIR = join(dirname(__file__), 'daily')
DATA_DEFAULT = 'table_aapl.csv'

# Html Beschreibung
desc = Div(text=open(join(dirname(__file__), "Html/description.html")).read(), width=1000)


# Create Input controls Todo: Add Method which automaticaley chooses option based on available csv files??? DONE!
stock_ticker = os.listdir(DATA_DIR)  # returns list

# set up widgets

days = Slider(title="Number of days to keep the stock", value=100, start=1, end=252, step=30)
iterations = Slider(title="Number of MonteCarlo iterations", value=100, start=1, end=252, step=1)
stats = PreText(text='', width=500)
stock = Select(title='Auswahl der Aktie:', value=DATA_DEFAULT, options=stock_ticker)
select_varianzred = Select(title='Methoden zur Varianzreduktion: ', value='Methode 1', options=['Methode 1', 'Methode 2'])

# Create Column Data Source that will be used by the plot
source = ColumnDataSource(data=dict(date=[], o=[], h=[], l=[], c=[], volume=[]))

# HIER: LADE DATEN AUS .CSV


@lru_cache()
def load_ticker(ticker):
    fname = join(DATA_DIR, ticker)
    data = pd.read_csv(fname, header=None, parse_dates=['date'],
                       names=['date', 'foo', 'o', 'h', 'l', 'c', 'v'])
    data = data.set_index('date')
    # gibt tabelle aus in format ->     date - ticker(close) - ticker_returns
    return pd.DataFrame({ticker: data.c, ticker+'_returns': data.c.diff()})

# HIER: DATEN ANPASSEN


@lru_cache()
def get_data(t1):
    df1 = load_ticker(t1)
    data = pd.concat([df1], axis=1)
    data = data.dropna()
    data['t1'] = data[t1]
    data['t1_returns'] = data[t1+'_returns']
    return data


# set up plots

source_static = ColumnDataSource(data=dict(date=[], t1=[], t1_returns=[]))
tools = 'pan,wheel_zoom,xbox_select,reset'


ts1 = figure(plot_width=900, plot_height=500, tools=tools, x_axis_type='datetime', active_drag="xbox_select")
ts1.line('date', 't1', source=source_static)
ts1.circle('date', 't1', size=1, source=source, color=None, selection_color="orange")

# Histogram zeichen von returns
# temp = get_data(DATA_DEFAULT)
# hist = Histogram(plot_width=500, plot_height=200, bins=50, data=temp[['t1_returns']])


# SET-UP CALLBACKS------------------------------------------------------------------
# Callback für Änderung der Aktie

def stock_change(attrname, old, new):
    stock.value = new
    update()
# Callback für Änderung der Anzahl an Datensätzen für Simulation


def days_change(attrname, old, new):
    days.value = new
    t1 = stock.value
    data = get_data(t1)
    data = data.iloc[len(data[['t1']])-new:len(data[['t1']])]
    update_stats(data, t1)
    update_selection(data);


def update_selection(data):
    t1 = stock.value
    source.data = source.from_df(data[['t1', 't1_returns', ]])
    source_static.data = source.data
    update_stats(data, t1)


def update_first():
    t1 = stock.value
    data = get_data(t1)
    source.data = source.from_df(data[['t1', 't1_returns', ]])
    source_static.data = source.data
    days.end = len(data[['t1']])
    days.value = len(data[['t1']])
    update_stats(data, t1)


def update():
    t1 = stock.value
    data = get_data(t1)
    source.data = source.from_df(data[['t1', 't1_returns', ]])
    source_static.data = source.data
    days.end = len(data[['t1']])
    update_stats(data, t1)


def update_stats(data, t1):
    stats.text = str(data[[t1, t1+'_returns']].describe())


def selection_change(attrname, old, new):
    t1 = stock.value
    data = get_data(t1)
    selected = source.selected['1d']['indices']
    if selected:
        data = data.iloc[selected, :]
    update_stats(data, t1)


def updateDropDown():
    print("geht")


stock.on_change('value', stock_change)
days.on_change('value', days_change)
source.on_change('selected', selection_change)

# set up layout
c1 = column(stock, select_varianzred, days, iterations)
# c_ = row(stats, hist)
c_ = row(stats)
c2 = column(c_, ts1)
r1 = row(c1, c2)
layout = column(desc, r1)


update_first()  # initial load of the data - first load metadata
#updateDropDown()  # initial load of the dropdown - load Stock and calculate results based on metadata

curdoc().add_root(layout)
curdoc().title = "Monte Carlo Simulation"
