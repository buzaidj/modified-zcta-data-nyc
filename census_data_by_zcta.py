from census import Census
from us import states
from datetime import datetime

import numpy as np
import pandas as pd

zcta_to_modzcta = pd.read_csv('data/Geography-resources/ZCTA-to-MODZCTA.csv')

print(zcta_to_modzcta.set_index('ZCTA').to_dict())
