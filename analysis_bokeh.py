import numpy as np
import pandas as pd

from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource, HoverTool, LinearColorMapper
from bokeh.palettes import plasma
from bokeh.plotting import figure
#, output_file, show
from bokeh.transform import transform


df = pd.read_csv('modzcta_data.csv')

""" 1. New Variables useful for regressions / graphing"""
# weighting point size / in regressions
df['pointsize'] = pd.Series([(n / 10000) * 1 for n in df['Population']])
weights = df['Population']

# race variables
df['Percent Black'] = df['Black or Black and other races'] / df['Population']
df['Black or Black and other races (Thousands)'] = df['Black or Black and other races'] / 1000

# income variables
df['Median Income (Thousands)'] = df['Median Income'] / 1000
df['Median Family Income (Thousands)'] = df['Median Family Income'] / 1000
df['log Median Income'] = np.log(df['Median Income'])
df['log Median Income (Thousands)'] = np.log(df['Median Income (Thousands)'])

# number of tests variables
df['Tests per Capita'] = df['Total COVID Tests'] / df['Population']
df['COVID-19 Tests (per 100,000 persons)'] = df['Tests per Capita'].apply(lambda x: x * 100000)
sorted_by_tests = df.sort_values(by = ['COVID-19 Tests (per 100,000 persons)'])

# death variables
df['Deaths (less NH / ACF Deaths) per Capita'] = df['Deaths less NH/ACF Deaths'] / df['Population']
df['COVID-19 Non-NH/ACF Deaths (per 100,000 persons)'] = df['Deaths (less NH / ACF Deaths) per Capita'].apply(lambda x : x * 100000)

df['Deaths per Capita'] = df['COVID Death Count'] / df['']
# density variables
df['Average Household Size'] = df['Average Unit Size']

# date (of data collected)
date = '6/14/2020'

""" Bokeh Percent Black and Percent Positive """
output_file("scatter_percentblack_percentpositive.html")
p = figure(plot_width=600, plot_height=400)
x = df['Percent Black']
y = df['Percent Positive']
size = df['pointsize']
neighborhood = df['Neighborhood Name']
population = df['Population']
median_income = df['Median Income']
mod_zctas = df['MOD ZCTA']
unit_size = df['Average Unit Size']


source = ColumnDataSource(data=dict(
    x = x,
    y = y,
    desc = mod_zctas,
    size = size,
    population = population,
    neighborhood = neighborhood,
    median_income = median_income,
    unit_size = unit_size
    )
)

hover = HoverTool(tooltips=[
    ('Modified ZCTA Code', '@desc'),
    ('Percent Black', '@x{0.00}'),
    ('Percent Positive', '@y{0.00}'),
    ('Population', '@population{0}'),
    ('Neighborhood', '@neighborhood'),
    ('Median Income', '@median_income{0}'),
    ('Average Household Size', '@unit_size{0.00}')
])

p = figure(plot_width=600, plot_height=400, tools=[hover],
           title="NYC COVID-19 positive rates by modified ZCTA (" + date + ") with 2017 ACS data")
p.circle('x', 'y', size= 'size', source=source)

p.xaxis.axis_label = "Percent of population identifying as black or black and other races"
p.yaxis.axis_label = "Percent Positive Cases"


show(p)

""" Bokeh Average Household Size and Percent Positive """
output_file("scatter_averagefamilysize_percentpositive.html")
p = figure(plot_width=600, plot_height=400)
x = df['Average Unit Size']
y = df['Percent Positive']
size = df['pointsize']
neighborhood = df['Neighborhood Name']
population = df['Population']
median_income = df['Median Income']
percent_black = df['Percent Black']

mod_zctas = df['MOD ZCTA']


source = ColumnDataSource(data=dict(
    x=x,
    y=y,
    desc=mod_zctas,
    size= size,
    population = population,
    neighborhood = neighborhood,
    median_income = median_income,
    percent_black = percent_black
    )
)

hover = HoverTool(tooltips=[
    ('Modified ZCTA Code', '@desc'),
    ('Average Household Size', '@x{0.00}'),
    ('Percent Positive', '@y{0.00}'),
    ('Population', '@population{0}'),
    ('Neighborhood', '@neighborhood'),
    ('Median Income', '@median_income{0}'),
    ('Percent Black', '@percent_black{0.00}')
])

p = figure(plot_width=600, plot_height=400, tools=[hover],
           title="NYC COVID-19 positive rates by modified ZCTA (" + date + ") with 2017 ACS data")
p.circle('x', 'y', size= 'size', source=source)

p.xaxis.axis_label = "Average Household Size"
p.yaxis.axis_label = "Percent Positive Cases"

show(p)

""" Deaths by average household size """
output_file("scatter_averagefamilysize_deaths.html")
p = figure(plot_width=600, plot_height=400)
x = df['Average Unit Size']
y = df['Percent Positive']
size = df['pointsize']
neighborhood = df['Neighborhood Name']
population = df['Population']
median_income = df['Median Income']
percent_black = df['Percent Black']

mod_zctas = df['MOD ZCTA']


source = ColumnDataSource(data=dict(
    x=x,
    y=y,
    desc=mod_zctas,
    size= size,
    population = population,
    neighborhood = neighborhood,
    median_income = median_income,
    percent_black = percent_black
    )
)

hover = HoverTool(tooltips=[
    ('Modified ZCTA Code', '@desc'),
    ('Average Household Size', '@x{0.00}'),
    ('Percent Positive', '@y{0.00}'),
    ('Population', '@population{0}'),
    ('Neighborhood', '@neighborhood'),
    ('Median Income', '@median_income{0}'),
    ('Percent Black', '@percent_black{0.00}')
])

p = figure(plot_width=600, plot_height=400, tools=[hover],
           title="NYC COVID-19 positive rates by modified ZCTA (" + date + ") with 2017 ACS data")
p.circle('x', 'y', size= 'size', source=source)

p.xaxis.axis_label = "Average Household Size"
p.yaxis.axis_label = "Percent Positive Cases"

show(p)



""" Bokeh Distribution of tests by average household size """
output_file("scatter_averagefamilysize_numberoftests.html")
p = figure(plot_width=600, plot_height=400)
x = df['Average Unit Size']
y = df['COVID-19 Tests (per 100,000 persons)']
size = df['pointsize']
neighborhood = df['Neighborhood Name']
population = df['Population']
median_income = df['Median Income']
percent_black = df['Percent Black']
mod_zctas = df['MOD ZCTA']


source = ColumnDataSource(data=dict(
    x=x,
    y=y,
    desc=mod_zctas,
    size= size,
    population = population,
    neighborhood = neighborhood,
    median_income = median_income,
    percent_black = percent_black
    )
)

hover = HoverTool(tooltips=[
    ('Modified ZCTA Code', '@desc'),
    ('Average Household Size', '@x{0.00}'),
    ('COVID-19 Tests (per 100,000 persons)', '@y{0}'),
    ('Population', '@population{0}'),
    ('Neighborhood', '@neighborhood'),
    ('Median Income', '@median_income{0}'),
    ('Percent Black', '@percent_black{0.00}')
])

p = figure(plot_width=600, plot_height=400, tools=[hover],
           title="NYC total COVID-19 tests by modified ZCTA (" + date + ") with 2017 ACS data")
p.circle('x', 'y', size= 'size', source=source)

p.xaxis.axis_label = "Average Household Size"
p.yaxis.axis_label = "COVID-19 Tests (per 100,000 persons)"
p.yaxis.formatter.use_scientific = False

show(p)
