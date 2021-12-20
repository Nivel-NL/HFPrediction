#%% Load which years are valid per patient
# These years are selected earlier on during conversion
# We only select the patients which have data for 2019

import pickle

main_folder = 'C:\\ThisIsTheMainFolder\\'
with open(main_folder + 'gp_patient_years', 'rb') as f:
    yearperpat= pickle.load(f)

d = [x for x in list(yearperpat.keys()) if '2019' in yearperpat[x]]

#%% Part processing

# From the preprocessing file, run only getid and getocc.
# This results in a data file with the first value for the disease
# We called the class 'a'

#%% Select incidence over the year 2019
# Minimal and maximum age can be altered such that age groups can be defined
from datetime import date

fixed_begin = date(2019, 1, 1)
fixed_end = date(2019, 12, 31)
minAge = 70
maxAge = 150

patlist = a.id2data
cases = []
controls = []

for key in d:
    
    age = fixed_begin.year - patlist[key]['data'][2]
    if (age < minAge) or (age>maxAge):
        continue
    
    if patlist[key]['dis_dates'][0] == 'negative':
        controls.append(key)
    elif (patlist[key]['dis_dates'][0] >= fixed_begin) and (patlist[key]['dis_dates'][0] <= fixed_end):
        cases.append(key)

total_years = fixed_end.year-fixed_begin.year + 1
incidence = len(cases)/ (len(cases)+len(controls))*1000/total_years
print('Incidence: {} in 1000 psy'.format(incidence))
print('Ratio of patients: 1 to {} controls'.format(1000/incidence))
print('Total life-years: {}'.format(len(cases)+len(controls)))