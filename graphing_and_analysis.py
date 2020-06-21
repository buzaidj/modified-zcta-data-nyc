import numpy as np
import pandas as pd
from sklearn import linear_model
import statsmodels.api as sm
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.ticker import PercentFormatter
import seaborn as sns


import math


class AnnoteFinder(object):
    """callback for matplotlib to display an annotation when points are
    clicked on.  The point which is closest to the click and within
    xtol and ytol is identified.

    Register this function like this:

    scatter(xdata, ydata)
    af = AnnoteFinder(xdata, ydata, annotes)
    connect('button_press_event', af)
    """

    def __init__(self, xdata, ydata, annotes, ax=None, xtol=None, ytol=None):
        self.data = list(zip(xdata, ydata, annotes))
        if xtol is None:
            xtol = ((max(xdata) - min(xdata))/float(len(xdata)))/2
        if ytol is None:
            ytol = ((max(ydata) - min(ydata))/float(len(ydata)))/2
        self.xtol = xtol
        self.ytol = ytol
        if ax is None:
            self.ax = plt.gca()
        else:
            self.ax = ax
        self.drawnAnnotations = {}
        self.links = []

    def distance(self, x1, x2, y1, y2):
        """
        return the distance between two points
        """
        return(math.sqrt((x1 - x2)**2 + (y1 - y2)**2))

    def __call__(self, event):

        if event.inaxes:

            clickX = event.xdata
            clickY = event.ydata
            if (self.ax is None) or (self.ax is event.inaxes):
                annotes = []
                # print(event.xdata, event.ydata)
                for x, y, a in self.data:
                    # print(x, y, a)
                    if ((clickX-self.xtol < x < clickX+self.xtol) and
                            (clickY-self.ytol < y < clickY+self.ytol)):
                        annotes.append(
                            (self.distance(x, clickX, y, clickY), x, y, a))
                if annotes:
                    annotes.sort()
                    distance, x, y, annote = annotes[0]
                    self.drawAnnote(event.inaxes, x, y, annote)
                    for l in self.links:
                        l.drawSpecificAnnote(annote)

    def drawAnnote(self, ax, x, y, annote):
        """
        Draw the annotation on the plot
        """
        if (x, y) in self.drawnAnnotations:
            markers = self.drawnAnnotations[(x, y)]
            for m in markers:
                m.set_visible(not m.get_visible())
            self.ax.figure.canvas.draw_idle()
        else:
            t = ax.text(x, y, " - %s" % (annote),)
            m = ax.scatter([x], [y], marker='d', c='r', zorder=100)
            self.drawnAnnotations[(x, y)] = (t, m)
            self.ax.figure.canvas.draw_idle()

    def drawSpecificAnnote(self, annote):
        annotesToDraw = [(x, y, a) for x, y, a in self.data if a == annote]
        for x, y, a in annotesToDraw:
            self.drawAnnote(self.ax, x, y, a)


df = pd.read_csv('modzcta_data.csv')
date = '6/14/2020'

df['Percent Black'] = df['Black or Black and other races'] / df['Population']

x = df['Percent Black']
y = df['Percent Positive']
annotes = df['Neighborhood Name']
df['pointsize'] = pd.Series([(n / 10000) * 1 for n in df['Population']])
fig, ax = plt.subplots()
ax.scatter(x, y, df['pointsize'])
af = AnnoteFinder(x,y, annotes, ax=ax)
fig.canvas.mpl_connect('button_press_event', af)
plt.title("NYC COVID-19 positive rates by \nMODZCTA (" + date + ") with 2017 ACS data")
plt.ylabel("Percent Positive Tests by MODZCTA Code")
plt.xlabel("Percent Black in ZIP Code")
plt.show()
plt.clf()

sns.regplot(x = 'Percent Black', y = 'Percent Positive', data = df)
plt.show()

df['pointsize'] = pd.Series([(n / 10000) * 1 for n in df['Population']])
plt.scatter(df['Percent Black'].values,df['Percent Positive'].values, df['pointsize'].values)
plt.title("NYC COVID-19 positive rates by \nMODZCTA (" + date + ") with 2017 ACS data")
plt.ylabel("Percent Positive Tests for COVID-19 in ZIP code")
plt.xlabel("Percent Black in ZIP code")
plt.show()
plt.clf()

df['Median Income (Thousands)'] = df['Median Income'] / 1000
df['Median Family Income (Thousands)'] = df['Median Family Income'] / 1000

df['log Median Income (Thousands)'] = np.log(df['Median Income (Thousands)'])

plt.scatter(df['Median Income (Thousands)'].values,df['Percent Positive'].values, df['pointsize'].values)
plt.title("NYC COVID-19 positive rates by \nMODZCTA (" + date + ") with 2017 ACS data")
plt.ylabel("Percent Positive Tests for COVID-19")
plt.xlabel("Median Income (Thousands)")
plt.show()
plt.clf()

plt.scatter(df['log Median Income (Thousands)'].values,df['Percent Positive'].values, df['pointsize'].values)
plt.title("NYC COVID-19 positive rates by \nMODZCTA (" + date + ") with 2017 ACS data")
plt.ylabel("Percent Positive Tests for COVID-19")
plt.xlabel("log Median Income (Thousands)")
plt.show()
plt.clf()


df['Black or Black and other races (Thousands)'] = df['Black or Black and other races'] / 1000
weights = df['Population']
X = pd.concat([df['Black or Black and other races (Thousands)'], df['Median Age'], df['log Median Income (Thousands)'], df['NH/ACF Deaths']], axis = 1)
X = sm.add_constant(X)
y = df['Percent Positive']

wls_model = sm.WLS(y, X, weights = weights)
results = wls_model.fit()
# print(results.summary())


plt.scatter(df['Median Income (Thousands)'].values,df['Death Rate'].values, df['pointsize'].values)
plt.title("NYC COVID-19 death rates by \nMODZCTA (" + date + ") with 2017 ACS data")
plt.ylabel("Death Rate for COVID-19")
plt.xlabel("Median Income (Thousands)")
plt.show()
plt.clf()


plt.scatter(df['Average Unit Size'].values,df['Percent Positive'].values, df['pointsize'].values)
plt.title("NYC COVID-19 positive rates by \nMODZCTA (" + date + ") with 2017 ACS data")
plt.ylabel("Positive Rate for COVID-19")
plt.xlabel("Average Unit Size")
plt.show()
plt.clf()

plt.scatter(df['log Median Income (Thousands)'].values,df['Average Unit Size'].values, df['pointsize'].values)
plt.title("log Median Income and Average Unit Size by \nMODZCTA (" + date + ") from 2017 ACS data")
plt.ylabel("Average Unit Size")
plt.xlabel("log Median Income (Thousands)")
plt.show()
plt.clf()

plt.scatter(df['Median Income (Thousands)'].values,df['Average Unit Size'].values, df['pointsize'].values)
plt.title("Median Income and Average Unit Size by \nMODZCTA (" + date + ") from 2017 ACS data")
plt.ylabel("Average Unit Size")
plt.xlabel("Median Income (Thousands)")
plt.show()
plt.clf()

"""
Incidence of infection per 100,000 persons
"""
df['Incidence of Infection (per 100,000 persons)'] = df['Case Rate'].apply(lambda x: x * 100000)
plt.scatter(df['Average Unit Size'], df['Incidence of Infection (per 100,000 persons)'], 1)
plt.ylabel("Incidence of Infection (per 100,000 persons)")
plt.xlabel("Average Household Size")

weights = df['Population']
X = pd.concat([df['Average Unit Size']], axis = 1)
X = sm.add_constant(X)
y = df['Incidence of Infection (per 100,000 persons)']

wls_model = sm.WLS(y, X, weights = weights)
results = wls_model.fit()

plt.show()
plt.clf()



"""
Computing Lorenz Curve
"""
print(df['Population'].sum())
print(df['COVID Case Count'].sum())

"""
Histograms of Tests per 100,000 persons
"""
df['Tests per Capita'] = df['Total COVID Tests'] / df['Population_from_NYCHealth']
df['COVID-19 Tests (per 100,000 persons)'] = df['Tests per Capita'].apply(lambda x: x * 100000)





# fig = plt.figure()
# ax1 = fig.add_subplot(111)
#
# ax1.scatter(df['Population'].values, df['COVID Death Count'].values, df['pointsize'].values)
# ax1.scatter(df['Population'].values,df['Deaths less NH/ACF Deaths'].values, df['pointsize'].values)
# plt.title("NYC COVID-19 deaths by \nZIP Code (" + date + ") with 2017 ACS data")
# plt.ylabel("Death Rate for COVID-19")
# plt.xlabel("Median Income (Thousands)")
# plt.legend(loc='upper left');
# plt.show()
