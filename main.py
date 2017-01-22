# should ultimately display the GUI and calculate everything where the user can change the following aspects:
# number of days to keep the stock, starting price, anual volatility, number of monteCarlo iterations
# should also draw afterwards a chart (last results of each iteration, iteration over all days = 1 iteration,
# so do it x time
# should also calculate mean, median, standard derivation, and the 5%,25% and 95% percentile of the result
# should also calculate the calc. val at risk and val at risk

# val at risk (VAR) = x% chance y% oder mehr von Portfolio verlieren in einem Tag!
# x% VAL = (1-(1-x))*total Count of Returns bei sortiertem aufliegen (=x% Quantil!!!)
# calc val at risk (CVAL) = in the worst x  % of returns the average loss will be y%
# x% CVAL = (1/VAR x%)*sum(from worst return to value of VAR x%)


# In one iteration do for each step:
# Simulated Price of that day = Starting price from the day before * (1+random number from N(0,x)
# Erwartungswert standard = 0 (user könnte ändern!) wegen der Random Walk Theory
# Last day = Result from the first iteration

#  CALCULATE THE ANNUAL VOLATILITY ! ... .CSV STOCK DATA IS ALWAYS FROM 1.1.2016-31.12.2016

# Todo: implement methods to reduce the varianz


from os.path import dirname, join

import pandas as pd
import numpy as np
import os

from bokeh.plotting import figure
from bokeh.layouts import row, column

from bokeh.models import ColumnDataSource, Div
from bokeh.models.widgets import PreText, Slider, Select, Button
from bokeh.io import curdoc
from simulator.valueAtRisk import valueAtRisk
from simulator.cValueAtRisk import cValueAtRisk

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



# HIER: LADE DATEN AUS .CSV


@lru_cache()
def load_ticker(ticker):
    fname = join(DATA_DIR, ticker)
    data = pd.read_csv(fname, header=None, parse_dates=['date'],
                       names=['date', 'foo', 'o', 'h', 'l', 'c', 'v'])
    data = data.set_index('date')

    # gibt tabelle aus in format ->     date - ticker(close) - ticker_returns
    df = pd.DataFrame({'t1': data.c, 't1_returns': data.c.pct_change()})

    return df

# HIER: DATEN ANPASSEN


def get_data(t1):
    df1 = load_ticker(t1)
    data = pd.concat([df1], axis=1)
    data = data.dropna()
    global data_source
    data_source = data
    return data

def getMonteCarloVAR():
    # valueAtRisk(dailyVolatility, days, startingPrice, numberofIterations, percentage):
    global data_source
    last = data_source.iloc[-1]
    vola = np.std(data_source[['t1_returns']])
    tage = daysToKeepTheStock.value
    iterationen = iterations.value
    interval = konfInterval.value

    # TODO Percentage
    temp = valueAtRisk(vola[0], tage, last['t1'], iterationen, interval)
    return temp


def getMonteCarloCVAR(VAR):

    # TODO Percentage
    temp = cValueAtRisk(VAR)
    return temp


DATA_DIR = join(dirname(__file__), 'daily')
DATA_DEFAULT = 'table_aapl.csv'
data_source = []
mc_returns = [0]

# Html Beschreibung
desc = Div(text=open(join(dirname(__file__), "Html/description.html")).read(), width=1200)

# Create Input controls
stock_ticker = os.listdir(DATA_DIR)  # returns list

# set up widgets
stock = Select(title='Auswahl der Aktie:', value=DATA_DEFAULT, options=stock_ticker)
days = Slider(title="Number of days to show", step=30)
select_varianzred = Select(title='Methoden zur Varianzreduktion: ', value='Ohne', options=['Ohne', 'Methode 1', 'Methode 2'])
iterations = Slider(title="Number of MonteCarlo iterations", value=10000, start=1000, end=200000, step=1)
daysToKeepTheStock = Slider(title="Number of days to keep the stock", value=10, start=1, end=30, step=1)
konfInterval = Slider(title="Konfidenzinterval", value=95, start=1, end=99, step=1)
stats2 = PreText(text='Es wurde noch keine Simulation durchgeführt', width=500)
button = Button(label="Berechnen", button_type="success")

# Create Column Data Source that will be used by the plot
source = ColumnDataSource(data=dict(date=[], o=[], h=[], l=[], c=[], volume=[]))
source_static = ColumnDataSource(data=dict(date=[], t1=[], t1_returns=[]))

# set up plots
tools = 'pan,wheel_zoom,reset'
ts1 = figure(name='linechart', title="Historische Werte der Aktie", plot_width=900, plot_height=300, tools=tools, x_axis_type='datetime')
ts1.line('date', 't1', source=source_static)


# Histogram zeichen von returns
# temp = get_data(DATA_DEFAULT)
hg1 = figure(title="Histogram", plot_width=1200, plot_height=300, tools=tools)
hist, edges = np.histogram(mc_returns, density=True, bins=50)
hg1.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], fill_color="#036564", line_color="#033649")


# SET-UP CALLBACKS------------------------------------------------------------------
# Callback für Änderung der Aktie

def stock_change(attrname, old, new):
    stock.value = new
    update()
# Callback für Änderung der Anzahl an Datensätzen für Simulation


def days_change(attrname, old, new):
    days.value = new
    t1 = stock.value
    get_data(t1)
    global data_source
    data_source = data_source.iloc[len(data_source[['t1']])-new:len(data_source[['t1']])]
    update_selection()


def update_selection():
    t1 = stock.value
    global data_source
    source.data = source.from_df(data_source[['t1', 't1_returns', ]])
    source_static.data = source.data


def update_first():
    t1 = stock.value
    get_data(t1)
    global data_source
    source.data = source.from_df(data_source[['t1', 't1_returns', ]])
    source_static.data = source.data
    days.end = len(data_source[['t1']])
    days.value = len(data_source[['t1']])


def update():
    t1 = stock.value
    get_data(t1)
    global data_source
    source.data = source.from_df(data_source[['t1', 't1_returns', ]])
    source_static.data = source.data
    days.end = len(data_source[['t1']])


def selection_change(attrname, old, new):
    t1 = stock.value
    get_data(t1)
    global data_source
    selected = source.selected['1d']['indices']
    if selected:
        data = data_source.iloc[selected, :]


def drawMonteCarlo():

    VAR = getMonteCarloVAR()
    CVAR = getMonteCarloCVAR(VAR)
    global mc_returns,hg1
    mc_returns = VAR['returnsSorted']
    hg1 = figure(title="Histogram", id='histog', plot_width=1200, plot_height=300, tools=tools)
    hist_, edges_ = np.histogram(mc_returns, density=True, bins=50)
    hg1.quad(top=hist_, bottom=0, left=edges_[:-1], right=edges_[1:], fill_color="#036564", line_color="#033649")
    vola=np.std(data_source[['t1_returns']])

    x = "Daily Volatility: {0:.4f} \n" \
        "Value at Risk: {1:.2f}%\n" \
        "conditional Value at Risk: {2:.2f}%".format(vola[0], VAR['valueAtRisk'], CVAR['cValueAtRisk'])
    stats2.text = x

    layout.children[2] = hg1

stock.on_change('value', stock_change)
days.on_change('value', days_change)
button.on_click(drawMonteCarlo)

# set up layout
c1 = column(stock, days, select_varianzred, daysToKeepTheStock, iterations, konfInterval, button)
c2 = column(ts1, stats2)
r1 = row(c1, c2)
cCalc = column()
layout = column(desc, r1, hg1)

curdoc().add_root(layout)

update_first()  # initial load of the data - first load metadata


curdoc().title = "Monte Carlo Simulation"
