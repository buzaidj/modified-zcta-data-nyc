import numpy as np
import pandas as pd

from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource, HoverTool, LinearColorMapper, Label, Select
from bokeh.palettes import plasma
from bokeh.plotting import figure
from bokeh.transform import transform
from bokeh.layouts import column, gridplot

import statsmodels.api as sm
import statsmodels.regression.linear_model as sml



df = pd.read_csv('modzcta_data.csv')

""" 1. New Variables useful for regressions / graphing"""
# weighting point size / in regressions
df['pointsize'] = pd.Series([max((n ** 0.6 / 150), 2) * 1 for n in df['Population']])
weights = df['Population']

# race variables
df['Black or Black and other races'] = df['Black or Black and other race']
df['Percent Black'] = df['Black or Black and other races'] / df['Population']
df['Percent of population identifying as black or black and other races'] = df['Percent Black']
df['Black or Black and other races (Thousands)'] = df['Black or Black and other races'] / 1000

# income variables
df['Median Income (Thousands)'] = df['Median Income'] / 1000
df['Median Family Income (Thousands)'] = df['Median Family Income'] / 1000
df['log Median Income'] = np.log(df['Median Income'])
df['log Median Income (Thousands)'] = np.log(df['Median Income (Thousands)'])
df['log Median Family Income'] = np.log(df['Median Income'])
df['log Median Family Income (Thousands)'] = np.log(df['Median Income (Thousands)'])


# positive tests per capita
df['Positive Tests per Capita'] = df['COVID Positive Tests'] / df['Population']
df['COVID-19 Positive Tests (per 100,000 persons)'] = df['Positive Tests per Capita'].apply(lambda x: x * 100000)

# number of tests variables
df['Tests per Capita'] = df['Total COVID Tests'] / df['Population']
df['COVID-19 Tests (per 100,000 persons)'] = df['Tests per Capita'].apply(lambda x: x * 100000)
sorted_by_tests = df.sort_values(by = ['COVID-19 Tests (per 100,000 persons)'])

# death variables
df['Deaths (less NH / ACF Deaths) per Capita'] = df['Deaths less NH/ACF Deaths'] / df['Population']
df['COVID-19 Non-NH/ACF Deaths (per 100,000 persons)'] = df['Deaths (less NH / ACF Deaths) per Capita'].apply(lambda x : x * 100000)

df['Deaths per Capita'] = df['COVID Death Count'] / df['Population']
df['COVID-19 Deaths (per 100,000 persons)'] = df['Deaths per Capita'].apply(lambda x : x * 100000)

df['Deaths as a percent of positive tests'] = df['Death Rate']

# density variables
df['Average Household Size'] = df['Average Unit Size']
df['Density (thousands of persons per square mile)'] = df['Density (persons per square mile)'] / 1000

# date (of data collected)
date = '6/14/2020'

""" WLS Function """
def _wls(y, x, weights):
    X = sm.add_constant(x)
    res = sml.WLS(y, X, weights = weights).fit()
    CI = res.conf_int(alpha = 0.05)
    CI_5, CI_95 = CI.iloc[1][:2]
    return pd.Series({'m': res.params.iloc[1],
        'b': res.params.iloc[0],
        'CI_5': CI_5, 'CI_95': CI_95,
        'p': res.pvalues.iloc[1],
        'r2': res.rsquared,
        'bse': res.bse.iloc[1],
        'n': len(y)})

def tf(name):
    return name.replace(" ", "").replace("/", "").replace(".", "").lower()

def get_bokeh(x_name, y_name, df):
    html = 'graphs/scatter_' + tf(x_name) + '_' + tf(y_name) + '.html'
    output_file(html)
    df = df.replace([np.inf, -np.inf], np.nan).dropna()
    x = df[x_name]
    y = df[y_name]
    percent_positive = df['Percent Positive']
    size = df['pointsize']
    neighborhood = df['Neighborhood Name']
    population = df['Population']
    median_income = df['Median Income']
    mod_zctas = df['MOD ZCTA']
    unit_size = df['Average Unit Size']
    percent_black = df['Percent Black']

    wls_model = _wls(y, x, weights = population)

    m = wls_model.m
    m_series = pd.Series(m, index = range(len(df.index)))

    b = wls_model.b
    b_series = pd.Series(b, index = range(len(df.index)))

    r2 = wls_model.r2
    r2_series = pd.Series(r2, index = range(len(df.index)))

    CI_5, CI_95 = wls_model.CI_5, wls_model.CI_95
    CI_5_series = pd.Series(CI_5, index = range(len(df.index)))
    CI_95_series = pd.Series(CI_95, index = range(len(df.index)))

    yhat = x.multiply(other = m).add(other = b)


    source = ColumnDataSource(data=dict(
        x = x,
        y = y,
        desc = mod_zctas,
        size = size,
        population = population,
        neighborhood = neighborhood,
        median_income = median_income,
        percent_black = percent_black,
        unit_size = unit_size,
        yhat = yhat,
        m = m_series,
        b = b_series,
        r2 = r2_series,
        CI_5 = CI_5_series,
        CI_95 = CI_95_series
        )
    )


    p = figure(plot_width=600, plot_height=400)

    circles = p.circle('x', 'y', size= 'size', source = source)
    line = p.line('x', 'yhat', color = 'red', source = source)

    hover = HoverTool(tooltips=[
        ('Modified ZCTA Code', '@desc'),
        ('(x, y)', '(@x{0.00}, @y{0.00})'),
        ('Population', '@population{0}'),
        ('Neighborhood', '@neighborhood'),
        ('Median Income', '@median_income{0}'),
        ('Average Household Size', '@unit_size{0.00}'),
        ('Percent black or black and other races', '@percent_black{0.00}')
    ], renderers = [circles])

    hover_line = HoverTool(tooltips =[
        ('Regression Line', 'y = @m{0.0000} * x + @b{0.0000}'),
        ('95% Confidence Interval for b1', '(@CI_5{0.0000}, @CI_95{0.0000})'),
        ('R-squared', '@r2{0.00}')
    ], renderers = [line])


    p.xaxis.axis_label = x_name
    p.yaxis.axis_label = y_name
    p.xaxis.formatter.use_scientific = False
    p.yaxis.formatter.use_scientific = False

    p.add_tools(hover)
    p.add_tools(hover_line)

    return p



graphs = []
y_vars = ['Percent Positive', 'COVID-19 Positive Tests (per 100,000 persons)', 'COVID-19 Tests (per 100,000 persons)', 'COVID-19 Non-NH/ACF Deaths (per 100,000 persons)', 'COVID-19 Deaths (per 100,000 persons)', 'Deaths as a percent of positive tests', 'NH/ACF Deaths']
# select_y = Select(title="Y Variables:", value="Percent Positive", options=y_vars)
x_vars = ['Percent of population identifying as black or black and other races', 'Average Household Size', 'log Median Income', 'log Median Family Income', 'Density (thousands of persons per square mile)', 'Percent Positive', 'COVID-19 Positive Tests (per 100,000 persons)']
# select_x = Select(title="X Variables:", value="Average Household Size", options=x_vars)

# for y_name in y_vars:
#     for x_name in x_vars:
#         g = get_bokeh(x_name, y_name, df)
#         sub_graphs.append(g)
#     graphs.append(sub_graphs)


for y_name in y_vars:
    sub_graphs = []
    for x_name in x_vars:
        g = get_bokeh(x_name, y_name, df)
        sub_graphs.append(g)
    graphs.append(sub_graphs)

grid = gridplot(graphs)
output_file('graphs/grid.html')
show(grid)

X = ['Percent of population identifying as black or black and other races', 'Average Household Size', 'log Median Income', 'log Median Family Income', 'Density (thousands of persons per square mile)']
y = 'Percent Positive'
