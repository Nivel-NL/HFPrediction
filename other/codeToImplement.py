from loadData import loaddata
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pickle


## This code has to be performed after the dataset creation
# It indicates the numbers and demographics
#%%
#------------------------------------------------------------------------#
# Check number of missing values

baselinedata, extradata = trainmod.getDataSetForLearning([6], False)
t=baselinedata.copy()

e=baselinedata.iloc[:,-4::].sum(axis=1)
t['combi'] = e
t['target'] = trainmod.y

t1 = t.copy()
t1 = t.iloc[0:int(len(trainmod.y)/2),:]
t2=t.copy()
t2 = t.iloc[int(len(trainmod.y)/2)::,:]
t1.loc[t1['combi']<0.5] # Height is number of missing controls
t2.loc[t2['combi']<0.5] # Height is number of missing patients

#%%
#------------------------------------------------------------------------#
# Check number unique codes

baselinedata, extradata = trainmod.getDataSetForLearning([3], False)

baseline_control = baselinedata.loc[trainmod.y['target']==0]
baseline_case = baselinedata.loc[trainmod.y['target']==1]

chronic_control = baseline_control.filter(regex = 'chronic$', axis=1)
print('Chronic control 25 perc: {}'.format(np.percentile(chronic_control.sum(axis=1), 25)))
print('Chronic control 75 perc: {}'.format(np.percentile(chronic_control.sum(axis=1), 75)))
print('Chronic control Median: {}'.format(chronic_control.sum(axis=1).median()))
chronic_case = baseline_case.filter(regex = 'chronic$', axis=1)
print('Chronic case 25 perc: {}'.format(np.percentile(chronic_case.sum(axis=1), 25)))
print('Chronic case 75 perc: {}'.format(np.percentile(chronic_case.sum(axis=1), 75)))
print('Chronic case Median: {}'.format(chronic_case.sum(axis=1).median()))
print('Chronic T-test: {}'.format(scipy.stats.ttest_ind(chronic_control.sum(axis=1), chronic_case.sum(axis=1))[1]))

icpc_control = baseline_control.filter(regex = 'icpc$', axis=1)
print('icpc control 25 perc: {}'.format(np.percentile(icpc_control.sum(axis=1), 25)))
print('icpc control 75 perc: {}'.format(np.percentile(icpc_control.sum(axis=1), 75)))
print('icpc control Median: {}'.format(icpc_control.sum(axis=1).median()))
icpc_case = baseline_case.filter(regex = 'icpc$', axis=1)
print('icpc case 25 perc: {}'.format(np.percentile(icpc_case.sum(axis=1), 25)))
print('icpc case 75 perc: {}'.format(np.percentile(icpc_case.sum(axis=1), 75)))
print('icpc case Median: {}'.format(icpc_case.sum(axis=1).median()))
print('icpc T-test: {}'.format(scipy.stats.ttest_ind(icpc_control.sum(axis=1), icpc_case.sum(axis=1))[1]))

atc_control = baseline_control.filter(regex = 'atc$', axis=1)
print('atc control 25 perc: {}'.format(np.percentile(atc_control.sum(axis=1), 25)))
print('atc control 75 perc: {}'.format(np.percentile(atc_control.sum(axis=1), 75)))
print('atc control Median: {}'.format(atc_control.sum(axis=1).median()))
atc_case = baseline_case.filter(regex = 'atc$', axis=1)
print('atc case 25 perc: {}'.format(np.percentile(atc_case.sum(axis=1), 25)))
print('atc case 75 perc: {}'.format(np.percentile(atc_case.sum(axis=1), 75)))
print('atc case Median: {}'.format(atc_case.sum(axis=1).median()))
print('atc T-test: {}'.format(scipy.stats.ttest_ind(atc_control.sum(axis=1), atc_case.sum(axis=1))[1]))

lab_control = baseline_control.filter(regex = 'lab$', axis=1)
print('lab control 25 perc: {}'.format(np.percentile(lab_control.sum(axis=1), 25)))
print('lab control 75 perc: {}'.format(np.percentile(lab_control.sum(axis=1), 75)))
print('lab control Median: {}'.format(lab_control.sum(axis=1).median()))
lab_case = baseline_case.filter(regex = 'lab$', axis=1)
print('lab case 25 perc: {}'.format(np.percentile(lab_case.sum(axis=1), 25)))
print('lab case 75 perc: {}'.format(np.percentile(lab_case.sum(axis=1), 75)))
print('lab case Median: {}'.format(lab_case.sum(axis=1).median()))
print('lab T-test: {}'.format(scipy.stats.ttest_ind(lab_control.sum(axis=1), lab_case.sum(axis=1))[1]))

age_control = baseline_control.filter(regex = 'age$', axis=1)
print('age control 25 perc: {}'.format(np.percentile(age_control.sum(axis=1), 25)))
print('age control 75 perc: {}'.format(np.percentile(age_control.sum(axis=1), 75)))
print('age control Median: {}'.format(age_control.sum(axis=1).median()))
age_case = baseline_case.filter(regex = 'age$', axis=1)
print('age case 25 perc: {}'.format(np.percentile(age_case.sum(axis=1), 25)))
print('age case 75 perc: {}'.format(np.percentile(age_case.sum(axis=1), 75)))
print('age case Median: {}'.format(age_case.sum(axis=1).median()))
print('age T-test: {}'.format(scipy.stats.ttest_ind(age_control.sum(axis=1), age_case.sum(axis=1))[1]))

gender_control = baseline_control.filter(regex = 'gender$', axis=1)
print('gender control perc female: {}'.format(gender_control['gender'].sum()/(len(trainmod.y)/2)))
gender_case = baseline_case.filter(regex = 'gender$', axis=1)
print('gender case perc female: {}'.format(gender_case['gender'].sum()/(len(trainmod.y)/2)))
print('gender T-test: {}'.format(scipy.stats.ttest_ind(gender_control.sum(axis=1), gender_case.sum(axis=1))[1]))
