import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pandas_bokeh
pd.set_option('plotting.backend', 'pandas_bokeh')
import math
from datawrapper import Datawrapper
dw = Datawrapper(access_token = '6f64bb98e42b547e29d7299e0d65eb56dc04eb75c62c4517de69dceba4176915')

pandas_bokeh.output_notebook()


df = pd.read_csv('modzcta_data.csv')
df = df['']
date = '6/13/2020'

"""

"""
df.plot_bokeh()


"""
Looking at allocation of testing
"""
# Histograms of Testing per 100,000 persons
df['Tests per Capita'] = df['Total COVID Tests'] / df['Population_from_NYCHealth']
df['COVID-19 Tests (per 100,000 persons)'] = df['Tests per Capita'].apply(lambda x: x * 100000)
ef = df.sort_values(by = ['COVID-19 Tests (per 100,000 persons)'])

n_bins = int(len(ef['MOD ZCTA']) / 3)
fig, axs = plt.subplots(1, 1, sharey=True, tight_layout=True)
axs.hist(ef['COVID-19 Tests (per 100,000 persons)'], bins = n_bins)
plt.title('Distribution of COVID-19 Tests by modified ZCTA code (n = 177)')
plt.ylabel('Number of modifed ZCTA codes')
plt.show('Number of COVID-19 tests per 100,000 persons')
