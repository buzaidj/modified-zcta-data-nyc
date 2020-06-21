from census import Census
from us import states
from datetime import datetime

import numpy as np
import pandas as pd

df = pd.read_csv("census.csv")
density = pd.read_csv("population_density_ZCTA.csv")
density.set_index('Zip/ZCTA', inplace = True)

c = Census("f2d65e4295f7da211515a9dbc1b8b665fc2e28c0")

def get_black_alone(zip):
    count = []
    for z in zip:
        each_count = c.acs5.zipcode('B02001_003E', str(int(z)))[0].get('B02001_003E')
        print(each_count)
        count.append(each_count)
    return count

def get_median_age(zip):
    count = []
    for z in zip:
        each_count = c.acs5.zipcode('B01002_001E', str(int(z)))[0].get('B01002_001E')
        print(each_count)
        count.append(each_count)
    return count

def get_housing_units(zip):
    count = []
    for z in zip:
        each_count = c.acs5.zipcode('B08201_001E', str(int(z)))[0].get('B08201_001E')
        print(each_count)
        count.append(each_count)
    return count

def get_density_data(zip):
    density_data = []
    for z in zip:
        density_per_sq_mile = density.loc[z].get('Density Per Sq Mile')
        density_data.append(density_per_sq_mile)
        print(density_per_sq_mile)
    return density_data

# df['Black alone'] = pd.Series(get_black_alone(df['zip_code_ta']))
# df['Median Age'] = pd.Series(get_median_age(df['zip_code_ta']))
# df['Housing Units'] = pd.Series(get_housing_units(df['zip_code_ta']))
df['Density (persons per square mile)'] = pd.Series(get_density_data(df['zip_code_ta']))

df['Average Unit Size'] = df['Population'] / df['Housing Units']
print(df['Average Unit Size'])

df.to_csv("census.csv")
