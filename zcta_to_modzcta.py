from census import Census
from us import states
from datetime import datetime

import numpy as np
import pandas as pd

zcta_to_modzcta = pd.read_csv('data/Geography-resources/ZCTA-to-MODZCTA.csv')
data_by_modzcta = pd.read_csv('data/data-by-modzcta.csv')

zips = zcta_to_modzcta['ZCTA']
zcta_dict = zcta_to_modzcta.set_index('ZCTA').to_dict().get('MODZCTA')
modzcta_dict =  {}
for k, v in zcta_dict.items():
    modzcta_dict[v] = modzcta_dict.get(v, [])
    modzcta_dict[v].append(k)


df = pd.DataFrame()
df['ZCTA'] = zips

"""
Add Census Data
"""
c = pd.read_csv("census.csv")
df = pd.concat([df, c], axis = 1)

# convert to meeting

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
    rf['Confirmed NH/ACF Deaths'] = confirmed
    rf['Presumed NH/ACF Deaths'] = presumed
    rf['NH/ACF Deaths'] = total

    return rf

rf = nh_acf(df, pd.read_csv('nhdata/nursing_homes.csv'), pd.read_csv('nhdata/acf.csv'))
df = pd.concat([df, rf], axis = 1)

df.to_csv("zip_code_data.csv")
df.set_index('ZCTA')

"""
Combining data to fit modZCTAs
"""
nf = pd.DataFrame()
nf['MOD ZCTA'] = data_by_modzcta['MODIFIED_ZCTA']
df = df.set_index('ZCTA')

def get_data(v):
    data = []
    for zip_code in v:
        data.append(df.loc[zip_code])
    return data


l = []
for k, v in modzcta_dict.items():
    l.append(get_data(v))


# df['Population'] = pd.Series(get_total_population(df['ZCTA']))
# df['Sample Count'] = pd.Series(get_sample_count(df['ZCTA']))
# df['Black or Black and other race'] = pd.Series(get_black(df['ZCTA']))
# df['White'] = pd.Series(get_white(df['ZCTA']))
# df['Median Income'] = pd.Series(get_median_inc(df['ZCTA']))
# df['Median Family Income In The Past 12 Months'] = pd.Series(get_median_family_inc(df['ZCTA']))


##########################
# adding up for each zip #
##########################


pop = [] #pop
sc = [] #sample count
black = [] # black or black and other races
white = [] # white (only)
median_income = [] # median income
median_family_income = [] # median family income
median_age = []
nh_acf = [] # nh / acf deaths
black_alone = []
avg_unit_size = []
density = []

total_pop = 0
for zips in l:
    p = 0
    s = 0
    b = 0
    w = 0
    pa = []
    mi = []
    mfi = []
    ma = []
    aus = []
    den = []
    n = 0
    bo = 0


    for zip in zips:

        p += zip.get('Population')
        total_pop += zip.get('Population')
        s += zip.get('Sample Count')
        b += zip.get('Black or Black and other race')
        w += zip.get('White')
        n += zip.get('NH/ACF Deaths')
        bo += zip.get('Black alone')

        pa.append(zip.get('Population'))
        mi.append(zip.get('Median Income'))
        mfi.append(zip.get('Median Family Income In The Past 12 Months'))
        ma.append(zip.get('Median Age'))
        aus.append(zip.get('Average Unit Size'))
        den.append(zip.get('Density (persons per square mile)'))

    i = 0

    # while i < len(pa):
    #     if mi[i] < 0 or mfi[i] < 0 or ma[i] < 0 or aus[i] < 0:
    #         pa.pop(i)
    #         mi.pop(i)
    #         mfi.pop(i)
    #         ma.pop(i)
    #         aus.pop(i)
    #     else:
    #         i += 1

    # estimate of median income is a weighted average with population, same for mfi
    mi_ = np.average(mi, weights = pa)
    mfi_ = np.average(mfi, weights = pa)
    ma_ = np.average(ma, weights = pa)
    aus_ = np.average(aus, weights = pa)
    den_ = np.average(den, weights = pa)

    pop.append(p)
    sc.append(s)
    black.append(b)
    white.append(w)
    median_income.append(mi_)
    median_family_income.append(mfi_)
    nh_acf.append(n)
    black_alone.append(bo)
    median_age.append(ma_)
    avg_unit_size.append(aus_)
    density.append(den_)

    print(total_pop)


nf['Population'] = pop[:-1]
sc = pd.Series(sc[:-1])
sc.fillna(0, inplace = True)
nf['Sample Count'] = sc

black = pd.Series(black[:-1])
black.fillna(0, inplace = True)
nf['Black or Black and other races'] = black

white = pd.Series(white[:-1])
white.fillna(0, inplace = True)
nf['White'] = white

nf['Median Income'] = median_income[:-1]
nf['Median Family Income'] = median_family_income[:-1]
nf['Median Age'] = median_age[:-1]
nf['Average Unit Size'] = avg_unit_size[:-1]
nf['Density (persons per square mile)'] = density[:-1]

nh_acf = pd.Series(nh_acf[:-1])
nh_acf.fillna(0, inplace = True)
nf['NH/ACF Deaths'] = nh_acf

"""
Add Data by MODZCTA
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

lf = pd.read_csv('data/tests-by-zcta-april04.csv')

nf['COVID Positive Tests April 4th'] = lf['Positive']
nf['Total COVID Tests April 4th'] = lf['Total']
nf['Percent Positive April 4th'] = nf['COVID Positive Tests April 4th'] / nf['Total COVID Tests April 4th']

print('Percent of Positive Tests Average, April 4th and June 15th')
print(np.average(nf['Percent Positive April 4th'], weights = nf['Population_from_NYCHealth']))
print(np.average(nf['Percent Positive'], weights = nf['Population_from_NYCHealth']))
print()
print('Total COVID tests April 4th and now')
print(nf['Total COVID Tests April 4th'].sum())
print(nf['Total COVID Tests'].sum())
print()
print('Total NYC Population')
print(nf['Population'].sum())
print()
print('Percent of Deaths from Nursing Homes')
print(nf['COVID Death Count'].sum() / nf['NH/ACF Deaths'].sum())

mf = pd.read_csv('data/modzcta.csv')
nf['the_geom'] = mf['the_geom'][:-1]

nf.to_csv('modzcta_data.csv')
