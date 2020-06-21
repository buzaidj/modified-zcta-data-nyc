from census import Census
from us import states
from datetime import datetime

import numpy as np
import pandas as pd

df = pd.DataFrame()
zcta_to_modzcta = pd.read_csv('data/Geography-resources/ZCTA-to-MODZCTA.csv')
zips = zcta_to_modzcta['ZCTA']
df['ZCTA'] = zips

df.drop(df.tail(1).index,inplace=True) # drop last n rows




c = Census("f2d65e4295f7da211515a9dbc1b8b665fc2e28c0")

def get_total_population(zip):
    population = []
    for z in zip:
        print(z)
        zip_pop = c.acs5.zipcode('B02001_001E', str(int(z)))[0].get('B02001_001E')
        population.append(zip_pop)
        print(zip_pop)
        print()
    return population

def get_sample_count(zip):
    sample_count = []
    for z in zip:
        each_zip_count = c.acs5.zipcode('B00001_001E', str(int(z)))[0].get('B00001_001E')
        print(each_zip_count)
        sample_count.append(each_zip_count)
    return sample_count

def get_black(zip):
    count = []
    for z in zip:
        print(z)
        each_count = c.acs5.zipcode('B02009_001E', str(int(z)))[0].get('B02009_001E')
        print(each_count)
        count.append(each_count)
        print()
    return count

def get_white(zip):
    count = []
    for z in zip:
        print(z)
        each_count = c.acs5.zipcode('B02001_002E', str(int(z)))[0].get('B02001_002E')
        print(each_count)
        count.append(each_count)
        print()
    return count

def get_median_age(zip):
    count = []
    for z in zip:
        each_count = c.acs5.zipcode('B01002_001E', str(int(z)))[0].get('B01002_001E')
        print(each_count)
        count.append(each_count)
    return count

def get_median_inc(zip):
    count = []
    for z in zip:
        each_count = c.acs5.zipcode('B19326_001E', str(int(z)))[0].get('B19326_001E')
        print(each_count)
        count.append(each_count)
    return count

def get_median_family_inc(zip):
    count = []
    for z in zip:
        each_count = c.acs5.zipcode('B19125_001E', str(int(z)))[0].get('B19125_001E')
        print(each_count)
        count.append(each_count)
    return count

def get_black_alone(zip):
    count = []
    for z in zip:
        each_count = c.acs5.zipcode('B02001_003E', str(int(z)))[0].get('B02001_003E')
        print(each_count)
        count.append(each_count)
    return count

def get_gini(zip):
    pass
def get_snap(zip):
    pass

df['Population'] = pd.Series(get_total_population(df['ZCTA']))
df['Sample Count'] = pd.Series(get_sample_count(df['ZCTA']))
df['Black or Black and other race'] = pd.Series(get_black(df['ZCTA']))
df['White'] = pd.Series(get_white(df['ZCTA']))
df['Median Income'] = pd.Series(get_median_inc(df['ZCTA']))
df['Median Family Income In The Past 12 Months'] = pd.Series(get_median_family_inc(df['ZCTA']))
df['Black alone'] = pd.Series(get_black_alone(df['ZCTA']))

df.to_csv("census.csv")
