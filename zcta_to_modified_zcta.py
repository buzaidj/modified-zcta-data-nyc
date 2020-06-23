import numpy as np
import pandas as pd

zcta_to_modzcta = pd.read_csv('coronavirus-data-master/Geography-resources/ZCTA-to-MODZCTA.csv')
data_by_modzcta = pd.read_csv('coronavirus-data-master/data-by-modzcta.csv')

zips = zcta_to_modzcta['ZCTA']
zcta_dict = zcta_to_modzcta.set_index('ZCTA').to_dict().get('MODZCTA')
modzcta_dict =  {}
for k, v in zcta_dict.items():
    modzcta_dict[v] = modzcta_dict.get(v, [])
    modzcta_dict[v].append(k)

"""
Add Census Data
"""
df = pd.read_csv("census-data/census.csv")
df['ZCTA'] = df['zip_code_ta']

"""
Add NH/ACF Data
"""
def nh_acf(df, nursing_homes, acf):
    def get_confirmed_deaths_presumed_deaths(zip):
        confirmed = []
        presumed = []
        total = []
        for z in zip:
            nursing_homes_with_zip = nursing_homes[[x == z for x in nursing_homes['ZIP']]]
            acf_with_zip = acf[[x == z for x in acf['ZIP']]]
            conf = nursing_homes_with_zip['Confirmed Deaths'].sum() + acf_with_zip['Confirmed Deaths'].sum()
            pres = nursing_homes_with_zip['Presumed Deaths'].sum() + acf_with_zip['Presumed Deaths'].sum()
            confirmed.append(conf)
            presumed.append(pres)
            total.append(conf + pres)

        return (confirmed, presumed, total)


    conf_pres_total = get_confirmed_deaths_presumed_deaths(df['ZCTA'])
    confirmed = pd.Series(conf_pres_total[0])
    presumed = pd.Series(conf_pres_total[1])
    total = pd.Series(conf_pres_total[2])

    rf = pd.DataFrame()
    rf['ZCTA'] = df['ZCTA']
    rf['Confirmed NH/ACF Deaths'] = confirmed
    rf['Presumed NH/ACF Deaths'] = presumed
    rf['NH/ACF Deaths'] = total

    return rf

rf = nh_acf(df, pd.read_csv('nhdata/nursing_homes.csv'), pd.read_csv('nhdata/acf.csv'))
rf = rf.set_index('ZCTA')
"""
Modified ZCTA dataframe
"""
df = df.set_index('ZCTA')
nf = pd.DataFrame()
nf['MOD ZCTA'] = data_by_modzcta['MODIFIED_ZCTA']
nf = nf.set_index('MOD ZCTA')

"""
Adding census data to modified ZCTA dataframe
"""
def get_sum_average(column_names, weight_name, df, nf, modzcta_dict, average = True):
    for name in column_names:
        nf[name] = np.nan
    for i, row in nf.iterrows():
        zctas = modzcta_dict.get(i)
        all_values = df.loc[zctas]
        values_needed = all_values[column_names]
        if weight_name != '':
            weights_needed = all_values[weight_name]
        # print('values')
        # print(len(values_needed.index))
        # print('\n')
        # print('weights')
        # print(len(weights_needed))
        # print('\n\n')
        if average:
            nf_values = np.average(values_needed, axis = 0, weights = weights_needed)
        else:
            nf_values = np.sum(values_needed, axis = 0)
        nf.at[i,column_names] = nf_values

sum_column_names = ['Population', 'Black or Black and other race', 'White', 'Black alone', 'Housing Units']
average_column_names = ['Median Income', 'Median Family Income In The Past 12 Months', 'Average Unit Size', 'Density (persons per square mile)']
sum_nh_names = ['Confirmed NH/ACF Deaths', 'Presumed NH/ACF Deaths', 'NH/ACF Deaths']
# new_average_column_names = ['Median Income', 'Median Family Income', 'Average Unit Size', 'Density (persons per square mile)']

get_sum_average(sum_column_names, 'Population',df, nf, modzcta_dict, False)
get_sum_average(average_column_names, 'Population', df, nf, modzcta_dict, True)
get_sum_average(sum_nh_names, '', rf, nf, modzcta_dict, False)

nf = nf.reset_index()
nf['MOD ZCTA'] = nf['MOD ZCTA'].astype(str)

nf['Median Family Income'] = nf['Median Family Income In The Past 12 Months']

"""
COVID Data
"""
nf['COVID Positive Tests'] = data_by_modzcta['COVID_CASE_COUNT']
nf['COVID Case Count'] = nf['COVID Positive Tests']
nf['COVID Death Count'] = data_by_modzcta['COVID_DEATH_COUNT']
nf['Total COVID Tests'] = data_by_modzcta['TOTAL_COVID_TESTS']
nf['Population_from_NYCHealth'] = data_by_modzcta['POP_DENOMINATOR']


nf['Percent Positive'] = nf['COVID Case Count'] / nf['Total COVID Tests']
nf['Death Rate'] = nf['COVID Death Count'] / nf['Population']
nf['Case Rate'] = nf['COVID Case Count'] / nf['Population']

nf['Borough'] = data_by_modzcta['BOROUGH_GROUP']
nf['Neighborhood Name'] = data_by_modzcta['NEIGHBORHOOD_NAME']

nf['Deaths less NH/ACF Deaths'] = nf['COVID Death Count'] - nf['NH/ACF Deaths']

lf = pd.read_csv('tests-by-zcta-april04.csv')

nf['COVID Positive Tests April 4th'] = lf['Positive']
nf['Total COVID Tests April 4th'] = lf['Total']
nf['Percent Positive April 4th'] = nf['COVID Positive Tests April 4th'] / nf['Total COVID Tests April 4th']

mf = pd.read_csv('modzcta.csv')
nf['the_geom'] = mf['the_geom'][:-1]

nf.to_csv('modzcta_data.csv')
